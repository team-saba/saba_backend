from fastapi import APIRouter, Depends, HTTPException


from DTO.userSetting import UserSetting
from service.settingManager import SettingManager

router = APIRouter()



@router.post("/oauth")
def oauth(code: str):
    return SettingManager().slack_oauth(code)


@router.get("/oauth")
def oauth(code: str):
    return SettingManager().slack_oauth(code)

@router.get("/settings")
def get_settings():
    return SettingManager().get_setting()


@router.put("/settings")
def put_settings(user_setting: UserSetting):
    return SettingManager().update_setting(user_setting=user_setting)