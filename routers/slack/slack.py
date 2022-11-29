from fastapi import APIRouter, Depends, HTTPException
import os
import json
import requests

router = APIRouter()

def slack_oauth(code):
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

@router.post("/oauth")
def oauth(code: str):
    slack_oauth(code)
    return "정상적으로 인증이 완료 되었습니다. Slack을 확인해 주세요"


@router.get("/oauth")
def oauth(code: str):
    slack_oauth(code)
    return "정상적으로 인증이 완료 되었습니다. Slack을 확인해 주세요"