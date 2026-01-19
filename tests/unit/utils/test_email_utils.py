from flask import Flask
import pytest

from utils import email as email_utils


def test_send_mail_spawns_thread(monkeypatch):
    app = Flask(__name__)

    captured = {"target": None, "args": None, "started": False}

    class FakeThread:
        def __init__(self, target, args):
            captured["target"] = target
            captured["args"] = args

        def start(self):
            captured["started"] = True

    monkeypatch.setattr(email_utils, "Thread", FakeThread)

    # perlu current_app (email.send_mail pakai current_app._get_current_object()) :contentReference[oaicite:3]{index=3}
    with app.app_context():
        dummy_msg = object()
        email_utils.send_mail(dummy_msg)

    assert captured["started"] is True
    # pastikan target-nya send_async_email
    assert captured["target"] == email_utils.send_async_email
    # args = (app_obj, msg)
    assert captured["args"][1] is dummy_msg
