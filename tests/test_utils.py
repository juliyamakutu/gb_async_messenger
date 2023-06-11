import unittest

from common import recv_message, send_message, Response


class TestSocket():
    def __init__(self, recv_value: bytes | None = None):
        self.sent_value = None
        self.recv_value = recv_value

    def send(self, message: bytes, *args, **kwargs):
        self.sent_value = message

    def recv(self, *args, **kwargs):
        return self.recv_value


class TestUtils(unittest.TestCase):
    def test_recv_message(self):
        conn = TestSocket(b'{"response": 200, "alert": "OK"}')
        assert recv_message(conn=conn) == {"response": 200, "alert": "OK"}

    def test_send_message(self):
        conn = TestSocket()
        send_message(conn=conn, message=Response(response=200, alert="OK"))
        assert conn.sent_value == b'{"response": 200, "alert": "OK"}'
