"""
This module contains the server.
"""

import socketserver
from typing import Any, Callable, Dict, List, Union

from bc.common.comm_util import Appointment, Message, RequestType, Transceiver
from bc.server.server_util import ServerState, ServiceProvider, TimeSlotInfo, TimeSlotState, User

class RequestHandler(socketserver.BaseRequestHandler):
    """
    Request handler class.
    """

    def __init__(self, *args) -> None:
        socketserver.BaseRequestHandler.__init__(*args)
        print("Request handler being constructed.")
        self.server_state = ServerState()
        self.router: Dict[RequestType, Callable[[RequestHandler, Message], Message]] = {
            RequestType.LIST_BASKET: RequestHandler.handle_list_basket,
            RequestType.LIST_BOOKED_APPOINTMENTS: RequestHandler.handle_list_booked_appointments,
            RequestType.LIST_AVAILABLE_APPOINTMENTS: RequestHandler.handle_list_available_appointments,
            RequestType.ADD_APPOINTMENT_TO_BASKET: RequestHandler.handle_add_appointment_to_basket,
            RequestType.REMOVE_APPOINTMENT_FROM_BASKET: RequestHandler.handle_remove_appointment_from_basket,
            RequestType.CONFIRM_BOOKING: RequestHandler.handle_confirm_booking,
            RequestType.CANCEL_APPOINTMENT: RequestHandler.handle_cancel_appointment,
            }
        print("Request handler constructed.")

    def handle(self) -> None:
        print("Handling request from handler.")

        socket = self.request
        transceiver = Transceiver(socket)

        msg_bytes = transceiver.receive()
        # TODO.
        print(msg_bytes)

        try:
            request = Message.from_bytes(msg_bytes).data()
            request_type = request["type"]
            reply = self.router[request_type](self, request)
        except:
            reply = self.__get_reply_message(False, "Invalid request.")

        transceiver.send(reply.to_bytes())

    def handle_list_basket(self, request: Message) -> Message:
        client_id = request.data()["client_id"]

        provider_filter = lambda a: True
        ts_filter = lambda slot_info: (slot_info.owner == client_id
                and slot_info.state == TimeSlotState.IN_BASKET)

        return self._filter_appointments(provider_filter, ts_filter)

    def handle_list_booked_appointments(self, request: Message) -> Message:
        client_id = request.data()["client_id"]

        provider_filter = lambda a: True
        ts_filter = lambda slot_info: (slot_info.owner == client_id
                and slot_info.state == TimeSlotState.RESERVED)

        return self._filter_appointments(provider_filter, ts_filter)

    def handle_list_available_appointments(self, request: Message):
        provider_filter = lambda a: True
        ts_filter = lambda slot_info: slot_info.state == TimeSlotState.RESERVED

        return self._filter_appointments(provider_filter, ts_filter)

    def handle_add_appointment_to_basket(self, request: Message) -> Message:
        request_data = request.data()
        client_id = request_data["client_id"]

        appointment = request_data["appointment"]

        ts_info = self._find_ts_info_for_appointment(appointment)

        if isinstance(ts_info, Message):
            return ts_info

        if ts_info.state == TimeSlotState.AVAILABLE:
            ts_info.state = TimeSlotState.IN_BASKET
            ts_info.owner = client_id
            return self.__get_reply_message(True, "OK.")

        return self.__get_reply_message(False, "Time slot not available.")

    def handle_remove_appointment_from_basket(self, request: Message) -> Message:
        return self._handle_remove_or_cancel_appointment(request, TimeSlotState.IN_BASKET)

    def handle_confirm_booking(self, request: Message):
        request_data = request.data()
        client_id = request_data["client_id"]

        provider_predicate = lambda a: True
        ts_predicate = lambda ts_info: ts_info.owner == client_id and ts_info.state == TimeSlotState.IN_BASKET
        appointments = self._filter_appointments_list(provider_predicate, ts_predicate)

        if not appointments:
            return self.__get_reply_message(False, "No appointments in basket.")

        for appointment in appointments:
            ts_info = self._find_ts_info_for_appointment(appointment)
            if isinstance(ts_info, Message):
                return ts_info

            ts_info.state = TimeSlotState.RESERVED

        return self.__get_reply_message(True, "OK.")

    def handle_cancel_appointment(self, request: Message):
        return self._handle_remove_or_cancel_appointment(request, TimeSlotState.RESERVED)

    def _handle_remove_or_cancel_appointment(self, request: Message, expected_state: TimeSlotState) -> Message:
        request_data = request.data()
        client_id = request_data["client_id"]

        appointment = request_data["appointment"]

        ts_info = self._find_ts_info_for_appointment(appointment)

        if isinstance(ts_info, Message):
            return ts_info

        if ts_info.state != expected_state or ts_info.owner != client_id:
            return self.__get_reply_message(False, "Appointment not reserved by you.")

        ts_info.state = TimeSlotState.AVAILABLE

        return self.__get_reply_message(True, "OK.")


    def _find_ts_info_for_appointment(self, appointment: Appointment) -> Union[Message, TimeSlotInfo]:
        if appointment.service_provider() not in self.server_state.service_provider_db:
            return self.__get_reply_message(False, "No such provider")

        ts_infos = self.server_state.service_provider_db[appointment.service_provider()]

        ts_info_filtered = list(filter(lambda ts_info: ts_info.time_slot == appointment.time_slot, ts_infos))

        if not ts_info_filtered:
            return self.__get_reply_message(False, "No such time slot for the provider")

        ts_info = ts_info_filtered[0]

        return ts_info

    def _filter_appointments_list(self,
                             provider_predicate: Callable[[ServiceProvider], bool],
                             ts_predicate: Callable[[TimeSlotInfo], bool]) -> List[Appointment]:
        appointments: List[Appointment] = []

        providers = filter(provider_predicate, self.server_state.service_provider_db.keys())

        for provider in providers:
            info = self.server_state.service_provider_db[provider]
            ts_infos = filter(ts_predicate, info)
            aps = map(lambda ts_info: Appointment(provider, ts_info.time_slot), ts_infos)
            appointments.extend(aps)

        return appointments

    def _filter_appointments(self,
                             provider_predicate: Callable[[ServiceProvider], bool],
                             ts_predicate: Callable[[TimeSlotInfo], bool]) -> Message:
        appointments: List[Appointment] = self._filter_appointments_list(provider_predicate, ts_predicate)
        text = "\n".join(map(str, appointments))
        return Message(self.__get_reply_message(True, text))

    @staticmethod
    def __get_reply_message(ok: bool, text: str) -> Message:
        msg_dict = {
            "OK": ok,
            "text": text
            }
        return Message(msg_dict)


def server_main():
    """
    Server main loop.
    """

    print("Entering server!")
    HOST = "localhost"
    PORT = 9998

    # TODO: RequestHandler
    with socketserver.TCPServer((HOST, PORT), RequestHandler) as server:
            # Activate the server; this will keep running until you
            # interrupt the program with Ctrl-C
            server.timeout = None
            server.handle_request()
            print("Handled request.")
            server.serve_forever()
