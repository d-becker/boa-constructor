"""
This module contains the server.
"""

from enum import auto, Enum, unique

from bc.common.entities import TimeSlot

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
