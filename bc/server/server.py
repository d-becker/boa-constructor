from myExceptions import *

days = ['M', 'Tu', 'W', 'Th', 'F']

class beautyParlor:

    def __init__(self, *args):
        self.__serviceProviders = args
        self.__table = {p: {d: {h+8: '' for h in range(12)} for d in days} for p in args}
        self.__users = {}

    def registration(self, username, password):
        if username in self.__users:
            raise UserExists()
        self.__users.update[username] = password

    def show_appointments(self, provider):
        if provider not in self.__serviceProviders:
            raise NoProvider()
        return {d: [h+8 for h in range(12) if self.__table[provider][d][h] == ''] for d in days}

    def book(self, user, provider, day, hour):
        if provider not in self.__serviceProviders:
            raise NoProvider()
        if self.__table[provider][day][hour] != '':
            raise AlreadyBooked
        self.__table[provider][day][hour] = user

    def erase(self, provider, day, hour):
        if provider not in self.__serviceProviders:
            raise NoProvider()
        if self.__table[provider][day][hour] == '':
            pass # dontsuk meg el, hogy kell-e ide exception
        self.__table[provider][day][hour] = ''
