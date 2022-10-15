from assignment_6.prt_system.config import *
from assignment_6.prt_system.helper import *


class PassengerCollectionState(object):

    def __init__(self, station_name):
        self.curr_state = 'waiting'
        self.collected_passengers = []
        self.total_passengers = 0
        self.total_passengers_wrong_destination = 0
        self.total_travel_time_sum = 0
        self.station_name = station_name

    def collect_passenger(self, passengers):
        self.collected_passengers.extend(passengers)
        for passenger in passengers:
            self.total_passengers += 1
            self.total_travel_time_sum += passenger.get_travel_time()
            if passenger.destination != self.station_name:
                self.total_passengers_wrong_destination += 1


    def get_passenger(self):
        return self.collected_passengers

    def get_total_succesful_arrivals(self):
        return self.total_passengers-self.total_passengers_wrong_destination

    def get_avg_time(self):
        if self.total_passengers == 0:
            return 0
        return self.total_travel_time_sum/self.total_passengers



class Collector(AtomicDEVS, Logger):
    """
    Atomic DEVS that obtains Passengers. Should be used as a helper model to obtain the required statistics.
    """

    def __init__(self, name):
        AtomicDEVS.__init__(self, name)
        Logger.__init__(self, name)

        station_name = name.split(" ", 1)[1]
        self.state = PassengerCollectionState(station_name)

        self.input_port = self.addInPort(name="depart")

    def timeAdvance(self):
        # return 1
        return INFINITY

    def outputFnc(self):
        return {}

    def extTransition(self, inputs):
        passengers = inputs.get(self.input_port)

        if len(passengers) > 0:
            self.log("Collecting passenger")
            self.state.collect_passenger(passengers)
            self.log('Current Collected Passengers: %s' % len(self.state.collected_passengers))

        return self.state
