# pylint: disable=missing-docstring

import unittest
import socket

import bc.common.comm_util

class TestCommunication(unittest.TestCase):
    def test_receive_with_delimiter(self):
        try:
            socket1, socket2 = socket.socketpair()

            delimiter = b'\n\n'
            msg1 = b'First message'
            msg2 = b'Second message'

            socket1.send(msg1 + delimiter + msg2[:6])
            socket1.send(msg2[6:] + delimiter)
            receiver = bc.common.comm_util.Transceiver(socket2, delimiter)

            received1 = receiver.receive()
            received2 = receiver.receive()

            self.assertEqual(msg1, received1)
            self.assertEqual(msg2, received2)
        finally:
            socket1.close()
            socket2.close()
