"""
Module representing entities.
"""

class ServiceProvider:
    """
    A class representing a service provider.
    """

    def __init__(self, name: str) -> None:
        self._name = name

    def name(self) -> str:
        """
        Returns the name of the service provider.
        """
        return self._name

class TimeSlot:
    """
    A class representing a time slot.
    """

    def __init__(self, year: int, month: int, day: int, hour: int) -> None:
        TimeSlot._check_date_and_time(month, day, hour)

        self._year = year
        self._month = month
        self._day = day
        self._hour = hour

    def year(self) -> int:
        """
        Returns the year of this `TimeSlot`.
        """
        return self._year

    def month(self) -> int:
        """
        Returns the month of this `TimeSlot`.
        """
        return self._month

    def day(self) -> int:
        """
        Returns the day of this `TimeSlot`.
        """
        return self._day

    def hour(self) -> int:
        """
        Returns the hour of this `TimeSlot`.
        """
        return self._hour

    @staticmethod
    def _check_date_and_time(month: int, day: int, hour: int) -> None:
        if hour < 0 or hour > 24:
            raise ValueError("Incorrect hour: {}.".format(hour))

        if day < 0:
            raise ValueError("Incorrect day: {}.".format(day))

        if month == 2:
            if day > 28:
                raise ValueError("Incorrect day: {}.".format(day))
        if month in (4, 6, 9, 11):
            if day > 30:
                raise ValueError("Incorrect day: {}.".format(day))
        if day > 31:
            raise ValueError("Incorrect day: {}.".format(day))

class Appointment:
    """
    A class representing the appointment.
    """

    def __init__(self, service_provider: ServiceProvider, time_slot: TimeSlot) -> None:
        self._service_provider = service_provider
        self._time_slot = time_slot

    def service_provider(self) -> ServiceProvider:
        """
        Returns the service provider of this appointment.
        """

        return self._service_provider

    def time_slot(self) -> TimeSlot:
        """
        Returns the time slot of this appointment.
        """

        return self._time_slot
