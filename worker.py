import datetime
import logging
import asyncio
import time
import requests
import json

import diskcache
from urllib3.exceptions import HTTPError
from DTO.VulnerabilityQueue import VulnerabilityQueue
import service.image_service as manage
import service.clair_service as clair

class ReservationWorker:
    request_count = 0
    quota_gi_jun_time: datetime.datetime = datetime.datetime.now()
    MINIMUM_DELAY = 0.5
    QUOTA_PER_MINUTE = 100

    reservation_success_list = []
    async_tasks = set()

    clair_indexer_url = 'http://localhost:6060/indexer/api/v1/index_report'

    def __init__(self):
        self.worker_status = diskcache.Cache(directory="./cache/worker_status")
        self.scan_result = diskcache.Cache(directory="./cache/scan_result")
        self.sign_result = diskcache.Cache(directory="./cache/sign_result")
        self.auth_token = diskcache.Cache(directory="./cache/auth_token")
        pass

    def write_worker_status(self):
        self.worker_status.set("request_count", self.request_count, retry=True)
        self.worker_status.set("quota_gi_jun_time", self.quota_gi_jun_time, retry=True)
        print("기준시간", self.quota_gi_jun_time)
        print("요청 횟수", self.request_count)
        print("남은 제한 횟수", self.QUOTA_PER_MINUTE - self.request_count)
        pass

    def get_next_delay(self) -> float:
        self.request_count += 1

        now = datetime.datetime.now()
        reset_time = self.quota_gi_jun_time
        quota = self.QUOTA_PER_MINUTE
        remain_quota = quota - self.request_count

        # 기준시각 + 1분 이 지나면 현재 사용량 초기화
        if reset_time < now:
            self.quota_gi_jun_time = now
            self.request_count = 0
            return self.MINIMUM_DELAY + 0

        # 다음 delay 시간 결정
        # 제한 보다 현재 요청 횟수가 많으면
        if self.request_count >= quota:
            # 다음 초기화 시간까지 대기.
            return (reset_time - now).total_seconds()
        else:
            # 남은 시간 대비 요청 횟수 비율에 따라 delay 시간 결정
            # + 최소 delay 시간.
            return self.MINIMUM_DELAY + (reset_time - now).total_seconds() / remain_quota
        pass

    async def do_reservation(self, reservation: VulnerabilityQueue):
        if not reservation:
            return
        try:
            print("do_reservation")
        except Exception as e:
            logging.error(e)
            self.worker_status.delete(f"Vulnerability_{reservation.uuid}", retry=True)
            return False

        # 예약 요청 처리
        try:
            # Trivy First
            print("scan")
            reservation_ticket = manage.scan_image(
                image_id=reservation.imageId
            )

            # Trivy Data Saving
            reservation.result = []
            trivy_result = reservation_ticket['scan_result']
            for t in trivy_result:
                vid = t['VulnerabilityID']
                d   = t['Description']
                s   = t['Severity']
                p   = t['PkgName']
                pi  = t['InstalledVersion']
                pix = t.get('FixedVersion', '')

                reservation.result.append({
                    'cveid': vid,
                    'description': d,
                    'severity': s,
                    'packageName': p,
                    'packageInstalled': pi,
                    'packageFixedIn': pix,
                    'engine': 'trivy',
                })


            # Clair Second
            if len(reservation.digest) == 0:
                # TODO: local image scan
                raise Exception("Local image scan is currently not supported.")

            breakpoint()
            digest = clair.validate_digest(reservation)
            response = requests.get(self.clair_indexer_url + f'/{digest}')
            if response.status_code == 404:
                layers = clair.clair_get_layers(reservation)
                clair.clair_post_manifest(layers=layers, reservation=reservation)
            elif response.status_code == 500:
                parsed_response = json.loads(response.content)
                raise HTTPError(parsed_response)

            clair_result = clair.clair_get_report(digest)

            if clair_result != {}:
                for ck, cv in clair_result['vulnerabilities'].items():
                    vid = cv['name']
                    d   = cv['description']
                    p   = cv['package']['name']
                    s   = cv['severity'] or cv['normalized_severity']
                    pi  = cv['package']['version']
                    pix = cv['fixed_in_version']

                    reservation.result.append({
                        'cveid': vid,
                        'description': d,
                        'severity': s,
                        'packageName': p,
                        'packageInstalled': pi,
                        'packageFixedIn': pix,
                        'engine': 'clair',
                    })

            # 결과값 DB 저장
            logging.info(f"처리 완료: {reservation.result}")

            self.scan_result.set(f"Vulnerability_{reservation.imageId}", reservation.result, retry=True)
            self.reservation_success_list.append(reservation)
            return True


        except HTTPError as e:
            logging.error("While handling clair related, error occured")
            logging.error(e)
            return False

        except Exception as e:
            logging.error(e)
            return False

        finally:
            self.worker_status.delete(f"Vulnerability_{reservation.uuid}", retry=True)

        pass


    async def process_reservation_work(self):

        for reservation_key in self.worker_status.iterkeys():
            # 예약 항목이 아니면 건너뛰기
            if not reservation_key.startswith("Vulnerability_"):
                await asyncio.sleep(0.01)
                continue

            print("1")
            reservation = self.worker_status.get(reservation_key)
            task = asyncio.create_task(self.do_reservation(reservation))
            self.async_tasks.add(task)
            task.add_done_callback(self.async_tasks.discard)

            # quota delay
            delay = self.get_next_delay()
            self.write_worker_status()
            await asyncio.sleep(delay)


async def main():
    tasks = set()
    reservation_manager = ReservationWorker()

    while True:
        # print("main loop")
        try:
            await reservation_manager.process_reservation_work()
        except Exception as e:
            logging.error(e, exc_info=True)
            logging.info("never mind. continue")
        await asyncio.sleep(0.3)

if __name__ == '__main__':
    asyncio.run(main())
