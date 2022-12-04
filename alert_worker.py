import datetime
import logging
import os
import time
import asyncio
import aiohttp

from diskcache import Cache

from DTO.userSetting import UserSetting
from service.settingManager import SettingManager

import service.container_service as dockercontainer
import service.image_service as manage

class ScaningWorker:
    setting: UserSetting = None

    gi_jun_time : datetime.datetime = None
    MINIMUM_DELAY = 0.5

    severity = ['CRITICAL', 'HIGH', 'MEDIUM']
    scan_success_list = []

    async_tasks = set()

    def __init__(self):
        self.get_setting()
        self.gi_jun_time = datetime.datetime.now()
        self.cache = Cache("./cache/settings")
        pass

    def get_setting(self):
        self.setting = SettingManager().get_setting()
        return self.setting

    def get_next_delay(self):
        now = datetime.datetime.now()
        GIJUN_PER_MINUTE = self.setting['GIJUN_PER_MINUTE']
        reset_time = self.gi_jun_time + datetime.timedelta(minutes=GIJUN_PER_MINUTE)
        if now > reset_time:
            self.quota_gi_jun_time = now
            return self.MINIMUM_DELAY + 0

        return (reset_time - now).total_seconds()

        pass

    async def do_scan(self):
        if not self.setting['AUTO_SCAN']:
            return

        # Scan 업무 시작
        try:
            container_list = dockercontainer.run_container_list()
            image_list = [container['Image'] for container in container_list]

            for image in image_list:
                if self.cache.get(f"alert_{image}"):
                    print("ok")
                    continue

                scan_result = manage.scan_image(
                    image_id=image
                )
                trivy_result = scan_result['scan_result']
                vul_result = []
                VUL_LEVEL = self.severity[0:self.setting['VUL_LEVEL']]

                container_id = [container['Id'] for container in container_list if container['Image'] == image][0]
                container_name = [container['Name'] for container in container_list if container['Image'] == image][0]

                for vul in trivy_result:

                    if vul['Severity'] in VUL_LEVEL:
                        if self.setting['AUTO_STOP']:
                            dockercontainer.stop_container(container_id)

                        if not image in vul_result:
                            vul_result.append(image)

                if len(vul_result) > 0:
                    self.cache.set(key=f"alert_{image}", value=True, expire=60*60*24, retry=True)
                    self.scan_success_list.append({
                        "container_name" : container_name,
                        "image" : image,
                        "vul_level" : VUL_LEVEL,
                        "vul_id" : vul['VulnerabilityID']
                    })
            return True

        except Exception as e:
            logging.error(e, exc_info=True)
            pass

    async def do_scan_loop(self):
        self.setting = self.get_setting()

        task = asyncio.create_task(self.do_scan())
        self.async_tasks.add(task)
        task.add_done_callback(self.async_tasks.discard)

        await asyncio.sleep(self.get_next_delay())

async def slack_al_lim_send(vul):
    payload = {
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "[Runtime] 취약점 발견 알림",
                    "emoji": True
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"- 컨테이너명 : {vul['container_name'][1:]} \n - 이미지명 : {vul['image'][:8]} \n - 취약점 : {vul['vul_id']} \n - 취약점 등급 : {vul['vul_level']}"
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "취약점 보고서 링크 바로가기"
                },
                "accessory": {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "바로가기",
                        "emoji": True
                    },
                    "value": "click_me_123",
                    "url": "https://works.miscthings.net/",
                    "action_id": "button-action"
                }
            }
            ]
    }

    async with aiohttp.ClientSession() as session:
        # get_setting
        setting = SettingManager().get_setting()
        webhook_url = setting['HOOK_URL']
        print(webhook_url)
        async with session.post(webhook_url, json=payload) as response:
            print("telegram_al_lim_send done")
            return True
    pass

async def telegram_al_lim_worker(scan_manager: ScaningWorker):
    tasks = set()

    while True:
        print("telegram al lim worker loop")

        if len(scan_manager.scan_success_list) > 0:
            reservation = scan_manager.scan_success_list.pop()
            task = asyncio.create_task(slack_al_lim_send(reservation))
            tasks.add(task)
            task.add_done_callback(tasks.discard)

        await asyncio.sleep(0.3)

async def main():
    tasks = set()
    scan_manager = ScaningWorker()

    tasks.add(asyncio.create_task(telegram_al_lim_worker(scan_manager)))

    while True:
        print("main loop")
        try:
            await scan_manager.do_scan_loop()
        except Exception as e:
            logging.error(e, exc_info=True)
            logging.info("never mind. continue")
        await asyncio.sleep(0.3)


asyncio.run(main())