from bc.common.comm_util import *
import socket

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

if __name__ == '__main__':
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
            '2': req_gen.msg_list_available_appointments,
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
