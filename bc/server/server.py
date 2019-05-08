"""
This module contains the server.
"""

import socketserver

from bc.common.comm_util import Request, Transceiver

class RequestHandler(socketserver.BaseRequestHandler):
    """
    Request handler class.
    """

    def handle(self) -> None:
        socket = self.request
        transceiver = Transceiver(socket)

        msg_bytes = transceiver.receive()
        # TODO.
        print(msg_bytes)
        request = Request.from_bytes(msg_bytes)

    def handle_list_basket(self):
        pass


def server_main():
    """
    Server main loop.
    """

    print("Entering server.")
    HOST = "localhost"
    PORT = 9999

    with socketserver.TCPServer((HOST, PORT), RequestHandler) as server:
            # Activate the server; this will keep running until you
            # interrupt the program with Ctrl-C
            server.serve_forever()
