# pylint: disable=missing-docstring

import unittest

from pathlib import Path

from bc.server.server_util import ServerState, TimeSlotInfo, TimeSlotState, User
from bc.common.entities import ServiceProvider, TimeSlot

class TestServerState(unittest.TestCase):
    def test_load_users(self):
        users_file = Path(__file__).parent / "users.txt"
        state = ServerState()
        state.load_users(str(users_file))

        expected = [User(1, "User1", "pwd1"), User(2, "User2", "pwd2")]
        self.assertEqual(expected, state.users)

    def test_load_service_providers(self):
        filename = Path(__file__).parent / "service_providers.txt"
        state = ServerState()
        state.load_service_providers(filename)

        expected = {
            ServiceProvider("Haakon Doctorsen"): [
                TimeSlotInfo(TimeSlot(2019, 2, 20, 15), TimeSlotState.AVAILABLE, 0),
                TimeSlotInfo(TimeSlot(2019, 2, 20, 17), TimeSlotState.AVAILABLE, 0)],
            ServiceProvider("Knud Tennistrenersen"): [
                TimeSlotInfo(TimeSlot(2019, 2, 25, 15), TimeSlotState.AVAILABLE, 0),
                TimeSlotInfo(TimeSlot(2019, 2, 25, 17), TimeSlotState.AVAILABLE, 0),
                TimeSlotInfo(TimeSlot(2019, 2, 25, 19), TimeSlotState.AVAILABLE, 0)]
            }

        self.assertEqual(expected, state.service_provider_db)
