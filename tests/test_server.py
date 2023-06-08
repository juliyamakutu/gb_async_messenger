from common import Response
from server import parse_message


PRESENCE_MESSAGE = {
    "action": "presence",
    "time": 1613486948.023,
    "type": "status",
    "user": {"account_name": "Guest", "status": "Yep, I am here!"},
}

WRONG_MESSAGE = {
    "foo": "bar",
}


def test_parse_presence_message():
    assert parse_message(PRESENCE_MESSAGE) == Response(response=200, alert="OK")


def test_parse_wrong_message():
    assert parse_message(WRONG_MESSAGE) == Response(response=400, alert="Bad Request")
