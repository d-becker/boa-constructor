# pylint: disable=missing-docstring
import socket

from typing import Callable, Dict, Optional

from bc.common.comm_util import Message, RequestGenerator, Transceiver
from bc.common.entities import Appointment, TimeSlot, ServiceProvider


def client_main():
    while True:
        task = main_prompt()

        # optn = {'1': req_gen.msg_list_booked_appointments,
        #         '2': req_gen.msg_list_available_appointments(provider),
        #         '3': req_gen.msg_list_basket,
        #         '4': req_gen.msg_add_appointment_to_basket,
        #         '5': req_gen.msg_remove_appointment_from_basket,
        #         '6': req_gen.msg_confirm_booking,
        #         '7': req_gen.msg_cancel_appointment}


class Client:
    def __init__(self):
        self.host, self.port = 'localhost', 9998 #TODO
        self.req_gen = RequestGenerator(1) #TODO

        self.task_handlers: Dict[str, Callable[[], None]] = {
            '1': self.handle_list_booked_appointments,
            '2': self.handle_list_available_appointments,
            '3': self.handle_list_basket,
            '4': self.handle_add_appointment_to_basket,
            '5': self.handle_remove_appointment_from_basket,
            '6': self.handle_confirm_booking,
            '7': self.handle_cancel_appointment
            }

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
            sock.connect((self.host, self.port))
            trans = Transceiver(sock)
            trans.send(request.to_bytes())
            ans = trans.receive()

            return Message.from_bytes(ans)

    def send_request_and_print_response(self, request: Message) -> None:
        response = self.send_request(request)
        self.print_response(response)

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
            q - quit\n
        '''

        task = input(prompt)
        return task

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

def generateMsg(req_gen: RequestGenerator, task) -> bytes:
    if task == '2':
        prompt = '''Please type in the name of a service provider.
            If you want to list all the available timeslots at every provider, please press ENTER.'''
        prov = input(prompt)
        if prov != '':
            req = optn[task](prov)
            return req.to_bytes()
    req = optn[task]()
    return req.to_bytes()

def main_old():
    providers = ['fodrasz', 'kozmetikus', 'manikur']
    while True:
        provider = input('Please enter a providers name:')
        if provider not in providers:
            print('{} is not an available option.')
        else:
            print('{} selected')


        prompt = '''Please choose an option:
            1 - list my appointments
            2 - list available appointments
            3 - list basket
            4 - add appointment to basket
            5 - remove appointment form basket
            6 - confirm booking
            7 - cancel appointment
            q - quit
        '''

        req_gen = RequestGenerator(1) #TODO
        optn = {'1': req_gen.msg_list_booked_appointments,
                '2': req_gen.msg_list_available_appointments(provider),
                '3': req_gen.msg_list_basket,
                '4': req_gen.msg_add_appointment_to_basket,
                '5': req_gen.msg_remove_appointment_from_basket,
                '6': req_gen.msg_confirm_booking,
                '7': req_gen.msg_cancel_appointment}
        while True:
            task = input(prompt)
            if task not in optn:
                print('{} is not an available option.'.format(task))
            elif task == 'q':
                break
            else:
                host, port = '', 1 #TODO
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.connect((host, port))
                    trans = Transceiver(sock)
                    msg = generateMsg(req_gen, task)
                    trans.send(msg)
                    ans = trans.receive()

                    ans_data = Message(ans).data()

                    ok = ans_data["OK"]
                    text = ans_data["text"]

                    if ok:
                        print('Your request had been confirmed.')
                    else:
                        print('Your request could not be confirmed due to the following error: ' +
                        text)


if __name__ == '__main__':
    main()







