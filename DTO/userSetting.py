import dataclasses
from dataclasses import dataclass


@dataclass
class UserSetting:
    GIJUN_PER_MINUTE: int = 10

    HOOK_URL: str = "https://hooks.slack.com/services/XXXXXXXXX/XXXXXXXXX/XXXXXXXXXXXXXXXXXXXXXXXX"

    VUL_LEVEL: int = 3

    AUTO_SCAN: bool = False
    AUTO_STOP: bool = False

    def to_dict(self):
        return dataclasses.asdict(self)