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


class ReservationWorker:
    request_count = 0
    quota_gi_jun_time: datetime.datetime = datetime.datetime.now()
    MINIMUM_DELAY = 0.5
    QUOTA_PER_MINUTE = 100

    reservation_success_list = []
    async_tasks = set()

    auth_url = 'https://auth.docker.io/token'
    docker_registry_url = 'https://registry-1.docker.io/'
    docker_manifest_url = 'https://registry-1.docker.io/v2/{}/manifests/{}'
    clair_indexer_url = 'http://localhost:6060/indexer/api/v1/index_report'
    clair_matcher_url = 'http://localhost:6060/matcher/api/v1/vulnerability_report/'

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
                # named container scan maybe?
                raise Exception("Local image scan is currently not supported.")

            digest = self.validate_digest(reservation)
            response = requests.get(self.clair_indexer_url + f'/{digest}')
            if response.status_code == 404:
                layers = self.clair_get_layers(reservation)
                self.clair_post_manifest(layers=layers, reservation=reservation)
            elif response.status_code == 500:
                parsed_response = json.loads(response.content)
                raise HTTPError(parsed_response)

            clair_result = self.clair_get_report(digest)

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

    # Private Functions
    def clair_post_manifest(self, layers: list, reservation: VulnerabilityQueue):
        token = self.get_auth_token(reservation)
        header = { 'Authorization': [ f'Bearer {token}' ] }
        digest = reservation.digest
        repo = reservation.repo_name
        _layers = []
        for layer in layers:
            layer_digest = layer['digest']
            layer_uri = self.docker_registry_url
            layer_uri += f'/v2/{repo}/blobs/{layer_digest}'

            _layers.append({'hash': layer_digest, 'uri': layer_uri, 'headers': header})

        _manifest = {
                        'hash': digest,
                        'layers': _layers
                    }

        response = requests.post(self.clair_indexer_url, json=_manifest)
        return response.status_code

    def clair_get_layers(self, reservation: VulnerabilityQueue):
        token = 'Bearer ' + self.get_auth_token(reservation)
        header = {'Authorization': token}
        digest = reservation.digest
        repo = reservation.repo_name
        if repo.find('/') == -1:
            repo = 'library/' + repo


        request_url = self.docker_manifest_url.format(repo, digest)
        response = requests.get(request_url, headers=header)
        parsed_res = json.loads(response.content)

        if 'layers' in parsed_res:
            return parsed_res['layers']

        elif 'manifests' in parsed_res:
            # It must have 'layers', not 'manifests'
            # see 'validate_digest' function
            raise Exception('Cannot get manifest: digest not validated.\n' + parsed_res)

        else:
            raise Exception('Cannot get manifest: Unexpected Response.\n' + parsed_res)

    def validate_digest(self, reservation: VulnerabilityQueue):
        repo = reservation.repo_name
        if repo.find('/') == -1:
            repo = 'library/' + repo
        digest = reservation.digest
        token = 'Bearer ' + self.get_auth_token(reservation)
        header = {'Authorization': token}

        request_url = self.docker_manifest_url.format(repo, digest)
        response = requests.get(request_url, headers=header)
        if response.status_code == 401:
            raise HTTPError(response.content)

        parsed_res = json.loads(response.content)
        if 'manifests' in parsed_res:
            for manifest in parsed_res['manifests']:
                # For this reason, arm is not supported currently.
                if manifest['platform']['architecture'] == 'amd64':
                    reservation.digest = manifest['digest']
                    return reservation.digest

        elif 'layers' in parsed_res:
            return reservation.digest

        else:
            raise Exception('Cannot validate digest: Unexpected response' + parsed_res)


    def clair_get_report(self, digest: str):
        response = requests.get(self.clair_matcher_url + digest)
        if response.status_code == 401:
            error_report = 'clair_get_report: 401 Unauthorized\n'
            error_report += json.loads(response.content)
            raise HTTPError(error_report)
        if response.status_code >= 500:
            error_report = 'clair_get_report: Database or clair server has error; it might be because it is busy.'
            error_report += json.loads(response.content)
            raise HTTPError(error_report)
        return json.loads(response.content)['vulnerabilities']

    def get_auth_token(self, rsv: VulnerabilityQueue)->str:
        # request for token of 'ch1keen/pwnable': OK
        # request for token of 'library/ruby': OK
        # request for token of 'ruby': OK but won't work
        repository = rsv.repo_name
        if repository.find('/') == -1:
            repository = 'library/' + repository

        token = self.auth_token.get(repository)
        if token is None:
            params = {
                        'service': 'registry.docker.io',
                        'scope': f'repository:{repository}:pull',
                     }
            response = requests.get(self.auth_url, params = params)

            if response.status_code == 200:
                token_json = json.loads(response.content)

                self.auth_token.set(repository, token_json['token'], expire=token_json['expires_in'])
                return token_json['token']

            else:
                logging.error("Cannot retrieve a token: Received %d" % response.status_code)
                logging.error(json.loads(response.content))

                raise HTTPError('get_auth_token: Cannot retrieve the token.')

        else:
            return str(token)

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
