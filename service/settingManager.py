import os
from dataclasses import dataclass
from enum import Enum
from diskcache import Cache
import json
import requests

from DTO.userSetting import UserSetting


class SettingManager:
    def __init__(self):
        self.setting_key = "user_setting"
        self.cache = Cache("./cache/settings")
        pass

    def update_setting(self, user_setting: UserSetting):
        self.cache.set(self.setting_key, user_setting.to_dict(), tag=f"{self.setting_key}", retry=True)

    def get_setting(self):
        user_setting_dict = self.cache.get(self.setting_key, retry=True, default=UserSetting().to_dict())
        user_setting = UserSetting(**user_setting_dict)
        user_setting.AUTO_SCAN = False
        return

    def slack_oauth(self, code):
        client_id = os.getenv("CLIENT_ID")
        client_secret = os.getenv("CLIENT_SECRET")
        redirect_uri = os.getenv("REDIRECT_URI")
        r = requests.post("https://slack.com/api/oauth.v2.access",
                          data={'client_id': client_id,
                                'client_secret': client_secret,
                                'code': code,
                                'redirect_uri': redirect_uri
                                }
                          )
        response = json.loads(r.text)
        webhook_url = response['incoming_webhook']['url']
        payload = {"text": webhook_url}
        requests.post(webhook_url, json=payload)
        requests.post(webhook_url, json={"text": "전송된 URL을 saba Setting에 등록해주세요."})
        return "정상적으로 인증이 완료 되었습니다. Slack을 확인해 주세요"