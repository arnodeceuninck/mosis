from pypdevs.DEVS import *
from pypdevs.infinity import INFINITY
from numpy import random

from assignment_6.prt_system.config import *

# Seeding is discouraged, since this seeds for all functions/library using this random function. This is why
# using a random_state instead is recommended. // numpy.random.seed(0)
# src: https://stackoverflow.com/questions/5836335/consistently-create-same-random-numpy-array
RANDOM_STATE = random.RandomState(RANDOM_SEED)


class Queue:

    def __init__(self):
        self.contents = []

    def empty(self):
        return len(self.contents) == 0

    def qsize(self):
        return len(self.contents)

    def put(self, item):
        self.contents.append(item)

    def get(self):
        return self.contents.pop()

    def len(self):
        return self.qsize()

    def first(self):
        return self.contents[-1]

    def __str__(self):
        output = "Q("
        for psgr in self.contents:
            output += str(psgr)
        output += ")"
        return output


def get_next_station(current_station):
    return current_station + 1  # TODO


def minutes_to_seconds(time_in_minutes):
    return time_in_minutes * 60


class Logger:
    def __init__(self, name):
        self.name = name
        self.log_history = ""

    def log(self, message, log_level=3):
        if log_level < MIN_LOG_LEVEL:
            return
        log_message = f"{self.name} - {message}"
        self.log_history += f"{log_message}\n"
        print(log_message)


class Passenger:
    """
    Identifies the passengers that travel around in the PRT. Upon creation, they are given an origin and a desired
    destination station.
    """

    def __init__(self, orig=None, dst=None, line=0):
        # TODO: If any of those two is None, this should be set to a random value
        if orig is None:
            # Orig should never be random, since the passengers get generated at a specific station
            # orig = random.choice(STATIONS[0]).name
            raise Exception("Origin not defined")
        if dst is None:
            # Destination should be different from the origin station, but must be on the same line
            dst = orig
            while orig == dst:
                dst = RANDOM_STATE.choice([x for x in STATIONS if line in x.lines]).name

        self.current_station = orig
        self.destination = dst
        self.line = line  # TODO: How should I determine the line of a passenger? -> First randomly choose a line, then randomly choose a destination on that line; currently only line 0 is supported
        self.trolley_enter_time = None
        self.trolley_left_time = None

    def set_boarding_time(self, time):
        self.trolley_enter_time = time

    def set_unboarding_time(self, time):
        self.trolley_left_time = time

    def get_travel_time(self):
        return self.trolley_left_time-self.trolley_enter_time

    def get_current(self):
        return self.current_station

    def get_destination(self):
        return self.destination

    def __str__(self):
        return f"Passenger({self.current_station}->{self.destination} via line {self.line})"


class Trolley:
    """
    Identifies the trolleys that transport passengers around over the PRT. They have a maximal capacity of 10 people and
    a parametrized velocity. Additionally, they can only serve one of the three lines.
    """

    def __init__(self, line=1, velocity=None):
        if velocity is None:
            velocity = TROLLEY_DEFAULT_VELOCITY
        self.velocity = velocity

        self.line = line
        # self.station = STATIONS[station]
        self.max_capacity = TROLLEY_MAX_CAPACITY
        self.capacity_left = TROLLEY_MAX_CAPACITY
        self.capacity_log = []

        self.passengers = list()  # Stored as a dict with the passenger destination as key

    def get_load(self):
        return len(self.passengers)

    def get_passenger_list(self):
        return self.passengers

    def psgr_str(self):
        output = ""
        for psgr in self.get_passenger_list():
            output += f"{psgr} "
        return output

    def add_passenger(self, passenger):
        if self.capacity_left <= 0:
            raise Exception(f"No room for passengers left: {self}")

        self.capacity_left -= 1

        self.passengers.append(passenger)
        assert self.capacity_left == self.get_capacity_left()

    def get_capacity_left(self):
        return self.max_capacity - len(self.passengers)

    def should_unboard(self, station_name, passenger):
        if passenger.destination == station_name:
            return True
        exit_at_wrong_station = RANDOM_STATE.choice([True, False], p=[WRONG_STATION_UNBOARD_CHANCE, 1-WRONG_STATION_UNBOARD_CHANCE])
        if exit_at_wrong_station:
            return True
        return False

    def log_capacity(self, time):
        # print(f"f({time})={self.get_load()}") # This gets outputted, but doesn't get updated in the references we have of the trollies
        self.capacity_log.append((time, self.get_load()))

    def unboard_passengers(self, station_name):
        passengers_left = []
        passengers_to_unboard = []
        for passenger in self.passengers:
            if self.should_unboard(station_name, passenger):
                self.capacity_left += 1
                passengers_to_unboard.append(passenger)
            else:
                passengers_left.append(passenger)
        self.passengers = passengers_left
        assert self.capacity_left == self.get_capacity_left()
        return passengers_to_unboard

    def __str__(self):
        return f"Trolley(line={self.line}, v={self.velocity}, n={self.get_load()})"
