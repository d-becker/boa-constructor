"""
Communication utilities.
"""

import socket
import pickle

from enum import auto, Enum, unique
from typing import Any, Dict, Optional

from bc.common.entities import Appointment

class Transceiver:
    """
    A class that wraps a socket. It divides the received bytes into messages using a delimiter and
    adds a delimiter to sent messages.
    """

    def __init__(self, sock: socket.socket, delimiter: bytes = b'\xff'):
        self._delimiter = delimiter
        self._socket = sock
        self._buffer = bytearray()

    def receive(self) -> bytes:
        """
        Receive the next message. Blocks until the delimiter is found.
        """

        while self._delimiter not in self._buffer:
            self._buffer += self._socket.recv(4096)

        i = self._buffer.index(self._delimiter)
        res = self._buffer[:i]

        del self._buffer[:i+len(self._delimiter)]
        return res

    def send(self, message: bytes) -> None:
        """
        Send a message, appending the delimiter to it.
        """
        self._socket.sendall(message + self._delimiter)

@unique
class RequestType(Enum):
    """
    Client request types.
    """

    LOGIN = auto()
    LIST_BASKET = auto()
    LIST_BOOKED_APPOINTMENTS = auto()
    LIST_AVAILABLE_APPOINTMENTS = auto()
    ADD_APPOINTMENT_TO_BASKET = auto()
    REMOVE_APPOINTMENT_FROM_BASKET = auto()
    CONFIRM_BOOKING = auto()
    CANCEL_APPOINTMENT = auto()

class Message:
    """
    A class representing messages. This is used to abstract away how the data is handled.
    This class provides methods to convert the message to bytes and back, but does not handle
    message boundaries.
    """

    def __init__(self, msg_object: Any) -> None:
        self._msg_object = msg_object

    def data(self) -> Any:
        """
        Returns the underlying message object.
        """

        return self._msg_object

    def to_bytes(self) -> bytes:
        """
        Returns a `bytes` representation of the message.
        """

        return pickle.dumps(self._msg_object, protocol=0)

    @staticmethod
    def from_bytes(data: bytes) -> "Message":
        """
        Converts the `bytes` representation of a request into a `Message` object.
        """
        return Message(pickle.loads(data))

class RequestGenerator:
    """
    A class with methods for generating request `Message` objects.
    """

    @staticmethod
    def msg_login(username: str, password: str) -> Message:
        """
        Returns a login `Message` object.
        """

        dictionary = {
            "client_id": -1,
            "request_id": -1,
            "type": RequestType.LOGIN,
            "username": username,
            "password": password
            }

        return Message(dictionary)

    def __init__(self, client_id: int):
        self._client_id = client_id
        self._request_id = 0

    def msg_list_basket(self) -> Message:
        """
        Returns a request for listing the contents of the basket.
        """

        res = self._base_dict()
        res["type"] = RequestType.LIST_BASKET

        return Message(res)

    def msg_list_booked_appointments(self) -> Message:
        """
        Returns a request for listing the appointments booked by the client.
        """

        res = self._base_dict()
        res["type"] = RequestType.LIST_BOOKED_APPOINTMENTS

        return Message(res)

    def msg_list_available_appointments(self, service_provider: Optional[str]) -> Message:
        """
        Returns a request for listing available appointments of the given service provider or all
        service providers if `service_provider` is None.
        """

        res = self._base_dict()
        res["type"] = RequestType.LIST_AVAILABLE_APPOINTMENTS

        res["service_provider"] = service_provider

        return Message(res)

    def msg_add_appointment_to_basket(self, appointment: Appointment) -> Message:
        """
        Returns a request for adding an appointment to the basket.
        """

        res = self._base_dict()
        res["type"] = RequestType.ADD_APPOINTMENT_TO_BASKET

        res["appointment"] = appointment

        return Message(res)

    def msg_remove_appointment_from_basket(self, appointment: Appointment) -> Message:
        """
        Returns a request for removing an appointment from the basket.
        """

        res = self._base_dict()
        res["type"] = RequestType.REMOVE_APPOINTMENT_FROM_BASKET

        res["appointment"] = appointment

        return Message(res)

    def msg_confirm_booking(self) -> Message:
        """
        Returns a request for confirming the booking.
        """

        res = self._base_dict()
        res["type"] = RequestType.CONFIRM_BOOKING

        return Message(res)

    def msg_cancel_appointment(self, appointment: Appointment) -> Message:
        """
        Returns a request for cancelling the given appointment.
        """

        res = self._base_dict()
        res["type"] = RequestType.CANCEL_APPOINTMENT

        res["appointment"] = appointment

        return Message(res)

    def _base_dict(self) -> Dict[str, Any]:
        res = {
            "client_id": self._client_id,
            "request_id": self._request_id
            }
        self._request_id += 1

        return res

@unique
class ReplyType(Enum):
    """
    Server response types.
    """

    OK = auto()

    # Erroneous request, the server could not process it.
    ERROR = auto()

    # The server denied the request.
    DENIED = auto()

