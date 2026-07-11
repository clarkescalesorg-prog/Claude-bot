import pytest
from twilio.base.exceptions import TwilioRestException

import outreach.twilio_client as client_module


class _FakeMessage:
    def __init__(self, sid):
        self.sid = sid


class _FakeMessages:
    def __init__(self, results):
        self._results = list(results)
        self.calls = 0

    def create(self, **kwargs):
        self.calls += 1
        result = self._results.pop(0)
        if isinstance(result, Exception):
            raise result
        return result


class _FakeClient:
    def __init__(self, results):
        self.messages = _FakeMessages(results)


def test_send_returns_sid_on_success(monkeypatch):
    fake = _FakeClient([_FakeMessage("SM123")])
    monkeypatch.setattr(client_module, "_get_client", lambda: fake)

    sid = client_module.send("+441111111111", "hi")

    assert sid == "SM123"
    assert fake.messages.calls == 1


def test_send_retries_once_on_retryable_error(monkeypatch):
    err = TwilioRestException(status=429, uri="/Messages", msg="Too Many Requests")
    fake = _FakeClient([err, _FakeMessage("SM456")])
    monkeypatch.setattr(client_module, "_get_client", lambda: fake)
    monkeypatch.setattr(client_module.time, "sleep", lambda *_: None)

    sid = client_module.send("+441111111111", "hi")

    assert sid == "SM456"
    assert fake.messages.calls == 2


def test_send_does_not_retry_on_non_retryable_error(monkeypatch):
    err = TwilioRestException(status=400, uri="/Messages", msg="Invalid number")
    fake = _FakeClient([err])
    monkeypatch.setattr(client_module, "_get_client", lambda: fake)

    with pytest.raises(TwilioRestException):
        client_module.send("+441111111111", "hi")

    assert fake.messages.calls == 1


def test_send_gives_up_after_one_retry(monkeypatch):
    err1 = TwilioRestException(status=500, uri="/Messages", msg="oops")
    err2 = TwilioRestException(status=500, uri="/Messages", msg="oops again")
    fake = _FakeClient([err1, err2])
    monkeypatch.setattr(client_module, "_get_client", lambda: fake)
    monkeypatch.setattr(client_module.time, "sleep", lambda *_: None)

    with pytest.raises(TwilioRestException):
        client_module.send("+441111111111", "hi")

    assert fake.messages.calls == 2
