"""
This module contains utilities for the server.
"""

from enum import auto, Enum, unique
from typing import Any, Dict, List

from bc.common.entities import ServiceProvider, TimeSlot

@unique
class TimeSlotState(Enum):
    """
    An enum of the possible states of TimeSlots.
    """
    AVAILABLE = auto()
    IN_BASKET = auto()
    RESERVED = auto()

class TimeSlotInfo:
    """
    A class that stores information about the availability of a TimeSlot.
    """

    def __init__(self, time_slot: TimeSlot, state: TimeSlotState, owner: int) -> None:
        """
        Args:
            time_slot: The TimeSlot object.
            state: The state of the TimeSlot.
            owner: If state is IN_BASKET or RESERVED, this is the client id of the owner, otherwise
                it is unused.
        """

        self.time_slot = time_slot
        self.state = state
        self.owner = owner

    def __eq__(self, other: Any) -> bool:
        return (self.time_slot == other.time_slot
                and self.state == other.state
                and self.owner == other.owner)

class User:
    """
    A struct representing user information.
    """
    def __init__(self, user_id: int, username: str, password: str) -> None:
        """
        Do not use plain test passwords in real programs.
        """
        self.user_id = user_id
        self.username = username
        self.password = password

    def __eq__(self, other: Any) -> bool:
        return (self.user_id == other.user_id
                and self.username == other.username
                and self.password == other.password)

    def __repr__(self) -> str:
        return "User({}, {}, {})".format(self.user_id, self.username, self.password)

class ServerState:
    """
    A class that keeps the state of the server.
    """

    def __init__(self) -> None:
        self.service_provider_db: Dict[ServiceProvider, List[TimeSlotInfo]] = dict()
        self.users: List[User] = []

        # Keys are user ids, values are ip addresses.
        self.connected_users: Dict[int, str] = dict()

    def load_users(self, filename: str) -> None:
        """
        Loads the users from the given file.
        """

        result = []
        with open(filename) as users_file:
            for line in users_file:
                record = line.strip().split(";")
                if len(record) == 0:
                    # Empty line
                    continue

                if len(record) != 3:
                    raise ValueError("Expected 3 fields in the record, found {}."
                                     .format(len(record)))
                user_id = int(record[0])
                username = record[1]
                password = record[2]
                result.append(User(user_id, username, password))
        self.users = result

    def load_service_providers(self, filename: str) -> None:
        """
        Loads the service provider database from the given file.
        """

        result = dict()
        with open(filename) as sp_file:
            for line in sp_file:
                record = line.strip().split(";")
                if len(record) == 0:
                    # Empty line.
                    continue
                name = record[0]
                service_provider = ServiceProvider(name)
                time_slots = map(ServerState._parse_time_slot, record[1:])
                time_slot_infos = map(
                    lambda time_slot: TimeSlotInfo(time_slot, TimeSlotState.AVAILABLE, 0),
                    time_slots)
                result[service_provider] = list(time_slot_infos)

        self.service_provider_db = result


    @staticmethod
    def _parse_time_slot(timeslot_str: str) -> TimeSlot:
        # Format: yyyy-mm-dd-hh.
        record = [int(element) for element in timeslot_str.split("-")]
        if len(record) != 4:
            raise ValueError("Invalid time slot string: {}.".format(timeslot_str))

        year = record[0]
        month = record[1]
        day = record[2]
        hour = record[3]

        return TimeSlot(year, month, day, hour)
