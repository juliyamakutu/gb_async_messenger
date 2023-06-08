import unittest
from unittest import mock

from client import make_presence_message
from common import PresenceRequest


class TestClient(unittest.TestCase):
    USERNAME = "Guest"
    STATUS = "Yep, I am here!"
    REQUEST = PresenceRequest(
        action="presence",
        time=1,
        type="status",
        user=PresenceRequest.User(account_name=USERNAME, status=STATUS),
    )

    def test_make_presence_message(self):
        with mock.patch("client.datetime") as mock_datetime:
            mock_datetime.now.return_value.timestamp.return_value = 1
            response = make_presence_message(account_name=self.USERNAME, status=self.STATUS)
            assert response == self.REQUEST