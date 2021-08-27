from typing import Dict
from pathlib import Path
from pprint import pprint

import yaml
import firebase_admin
from firebase_admin import messaging, credentials
from pyfcm import FCMNotification


def load_config(file) -> Dict:
    with open(file, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
        return data


PROJECT = Path(__file__).parent
FCM_FILE = load_config(PROJECT / "etc" / "fcm.yaml")
CRED_PATH = str(PROJECT) + "\\etc\\fir-test-cc410-firebase-adminsdk-ts2di-060894ad5d.json"

FCM = {**FCM_FILE["main"]}
PUSH_SERVICE = FCMNotification(FCM["api_key"])

CRED = credentials.Certificate(CRED_PATH)
firebase_admin.initialize_app(CRED)


def send_fcm():
    message = messaging.Message(
        notification=messaging.Notification(
            title="안녕하세요.",
            body="푸시알림서비스를 게시하였습니다."
        ),
        token=FCM["device_token"]
    )
    response = messaging.send(message)
    pprint(response)


if __name__ == '__main__':
    send_fcm()