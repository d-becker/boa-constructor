"""
This module contains the server.
"""

import socketserver
from typing import Callable, Dict

from bc.common.comm_util import Message, RequestType, Transceiver

class RequestHandler(socketserver.BaseRequestHandler):
    """
    Request handler class.
    """

    router: Dict[RequestType, Callable[[RequestHandler, Message], Message]] = {
        RequestType.LIST_BASKET: RequestHandler.handle_list_basket,
        RequestType.LIST_BOOKED_APPOINTMENTS: RequestHandler.handle_list_booked_appointments,
        RequestType.LIST_AVAILABLE_APPOINTMENTS: RequestHandler.handle_list_available_appointments,
        RequestType.ADD_APPOINTMENT_TO_BASKET: RequestHandler.handle_add_appointment_to_basket,
        RequestType.REMOVE_APPOINTMENT_FROM_BASKET: RequestHandler.handle_remove_appointment_from_basket,
        RequestType.CONFIRM_BOOKING: RequestHandler.handle_confirm_booking,
        RequestType.CANCEL_APPOINTMENT: RequestHandler.handle_cancel_appointment,
        }

    def handle(self) -> None:
        socket = self.request
        transceiver = Transceiver(socket)

        msg_bytes = transceiver.receive()
        # TODO.
        print(msg_bytes)

        try:
            request = Message.from_bytes(msg_bytes).data()
            request_type = request["type"]
            reply = RequestHandler.router[request_type](self, request)
        except:
            # TODO: handle error.
            reply = None # TODO: We need a message

        transceiver.send(reply.to_bytes())

    def handle_list_basket(self, request: Message):
        pass

    def handle_list_booked_appointments(self, request: Message):
        pass

    def handle_list_available_appointments(self, request: Message):
        pass

    def handle_add_appointment_to_basket(self, request: Message):
        pass

    def handle_remove_appointment_from_basket(self, request: Message):
        pass

    def handle_confirm_booking(self, request: Message):
        pass

    def handle_cancel_appointment(self, request: Message):
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
