from pathlib import Path
from pprint import pprint

import firebase_admin
from firebase_admin import messaging, credentials
from pyfcm import FCMNotification

from .utils import load_config


PROJECT = Path(__file__).parent.parent
FCM_FILE = load_config(PROJECT / "etc" / "fcm.yaml")
CRED_PATH = (PROJECT / "etc" / "fir-test-cc410-firebase-adminsdk-ts2di-060894ad5d.json")

FCM = {**FCM_FILE["main"]}
PUSH_SERVICE = FCMNotification(FCM["api_key"])

CRED = credentials.Certificate(CRED_PATH)
firebase_admin.initialize_app(CRED)


def send_mail(title: str, body: str, token):
    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body
        ),
        token=token or FCM["device_token"]
    )
    response = messaging.send(message)
    pprint(response)


if __name__ == '__main__':
    send_mail("타이틀", "푸시알림테스트")
