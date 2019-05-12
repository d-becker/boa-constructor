# pylint: disable=missing-docstring
import socket
import sys

from typing import Callable, Dict, Optional, Tuple

from bc.common.comm_util import Message, RequestGenerator, Transceiver
from bc.common.entities import Appointment, TimeSlot, ServiceProvider


def client_main():
    server_ip = 'localhost'
    server_port = 9998

    if len(sys.argv) > 1:
        server_ip = sys.argv[1]

    if len(sys.argv) > 2:
        server_port = int(sys.argv[2])

    client = Client(server_ip, server_port)
    client.start()

class Client:
    def __init__(self, server_ip: str = 'localhost', server_port: int = 9998):
        self.server_ip = server_ip
        self.server_port = server_port

        req_gen: Optional[RequestGenerator] = self.handle_login()
        while not req_gen:
            req_gen = self.handle_login()

        assert isinstance(req_gen, RequestGenerator)
        self.req_gen: RequestGenerator = req_gen

        self.task_handlers: Dict[str, Callable[[], None]] = {
            '1': self.handle_list_booked_appointments,
            '2': self.handle_list_available_appointments,
            '3': self.handle_list_basket,
            '4': self.handle_add_appointment_to_basket,
            '5': self.handle_remove_appointment_from_basket,
            '6': self.handle_confirm_booking,
            '7': self.handle_cancel_appointment
            }

    def start(self) -> None:
        while True:
            task = self.main_prompt()

            if task == 'q':
                print("Exiting.")
                return

            if task not in self.task_handlers:
                print("Invalid task.")
                continue

            self.task_handlers[task]()

    def handle_login(self) -> Optional[RequestGenerator]:
        username, password = self.login_prompt()
        request = RequestGenerator.msg_login(username, password)
        reply = self.send_request_and_print_response(request)

        if reply.data().get("OK"):
            client_id = reply.data().get("client_id")

            try:
                client_id_int: Optional[int] = int(client_id)
            except:
                client_id_int = None

            if client_id_int:
                return RequestGenerator(client_id_int)
            else:
                print("Server sent erroneous response.")

        return None

    def handle_list_booked_appointments(self) -> None:
        request = self.req_gen.msg_list_booked_appointments()
        self.send_request_and_print_response(request)

    def handle_list_available_appointments(self) -> None:
        provider_name: Optional[str] = self.provider_prompt_or_empty()

        if provider_name == "":
            provider_name = None

        request = self.req_gen.msg_list_available_appointments(provider_name)
        self.send_request_and_print_response(request)

    def handle_list_basket(self) -> None:
        request = self.req_gen.msg_list_basket()
        self.send_request_and_print_response(request)

    def handle_add_appointment_to_basket(self) -> None:
        appointment = self.prompt_for_appointment()

        if not appointment:
            return

        request = self.req_gen.msg_add_appointment_to_basket(appointment)
        self.send_request_and_print_response(request)

    def handle_remove_appointment_from_basket(self) -> None:
        appointment = self.prompt_for_appointment()

        if not appointment:
            return

        request = self.req_gen.msg_remove_appointment_from_basket(appointment)
        self.send_request_and_print_response(request)

    def handle_confirm_booking(self) -> None:
        request = self.req_gen.msg_confirm_booking()
        self.send_request_and_print_response(request)

    def handle_cancel_appointment(self) -> None:
        appointment = self.prompt_for_appointment()

        if not appointment:
            return

        request = self.req_gen.msg_cancel_appointment(appointment)
        self.send_request_and_print_response(request)

    def send_request(self, request: Message) -> Message:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((self.server_ip, self.server_port))
            trans = Transceiver(sock)
            trans.send(request.to_bytes())
            ans = trans.receive()

            return Message.from_bytes(ans)

    def send_request_and_print_response(self, request: Message) -> Message:
        response = self.send_request(request)
        self.print_response(response)

        return response

    @staticmethod
    def print_response(reply: Message) -> None:
        ans_dictionary = reply.data()

        status_ok = ans_dictionary.get("OK")
        text = ans_dictionary.get("text")
        if status_ok is None or text is None:
            print("Invalid response from server.")
            return

        if status_ok:
            print('Server response: OK.')
        else:
            print('Server response: ERROR.')

        print(text + '\n\n')

    @staticmethod
    def main_prompt() -> str:
        prompt = '''Please choose an option:
            1 - list my booked appointments
            2 - list available appointments
            3 - list basket
            4 - add appointment to basket
            5 - remove appointment form basket
            6 - confirm booking
            7 - cancel appointment
            q - quit\n'''

        task = input(prompt)
        return task

    @staticmethod
    def login_prompt() -> Tuple[str, str]:
        prompt_username = "Please enter your username: "
        username = input(prompt_username)

        prompt_password = "Please enter your password: "
        password = input(prompt_password)

        return (username, password)
    @staticmethod
    def provider_prompt() -> str:
        prompt = 'Please enter a providers name: '
        return input(prompt)

    @staticmethod
    def provider_prompt_or_empty() -> str:
        prompt = 'Please enter a providers name or leave empty to list all of them: '
        return input(prompt)

    @staticmethod
    def timeslot_prompt() -> str:
        prompt = "Please choose a timeslot (yyyy-mm-dd-hh): "
        return input(prompt)

    @staticmethod
    def prompt_for_appointment() -> Optional[Appointment]:
        provider_name = Client.provider_prompt()
        time_slot_str = Client.timeslot_prompt()

        time_slot_list = time_slot_str.split('-')

        try:
            time_slot_ints = list(map(int, time_slot_list))
            str_format_ok = len(time_slot_ints) == 4
        except:
            str_format_ok = False

        if not str_format_ok:
            print("Invalid time slot.")
            return None

        ts = TimeSlot(time_slot_ints[0], time_slot_ints[1], time_slot_ints[2], time_slot_ints[3])
        appointment = Appointment(ServiceProvider(provider_name), ts)
        return appointment






