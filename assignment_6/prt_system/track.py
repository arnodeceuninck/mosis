from assignment_6.prt_system.config import *
from assignment_6.prt_system.helper import *


class TrackState:

    def __init__(self):
        self.curr_state = 'initial'
        self.trolley = None
        self.all_passengers_boarded = False
        self.trigger = False
        self.unboarding_passengers = []
        self.current_time = 0.0

    def get_state(self):
        return self.curr_state

    def change_state(self, state):
        self.curr_state = state


class Track(AtomicDEVS, Logger):
    # TODO: Atomic or coupled DEVS?
    """
    Atomic or Coupled DEVS, identifying the location where Trolleys arrive at the Station. There can only be one Trolley
    per Track. A Trolley always halts for 1 minute at each Station (50% of the time before and 50% after
    boarding/disembarking). After its first wait, all Passengers that must exit at this Station disembark the Trolley,
    followed by the boarding of all people that need to enter that Trolley (as long as there are people waiting and
    there is room in the Trolley). Next, it waits the second time, before exiting the station. The Track communicates
    the lines it services to the Platform, such that people that have a destination station located on that line can
    board the Trolley. Only one Passenger can enter/exit the Trolley every 10 seconds.
    There should also be a 20% chance that a Person exits in the wrong station.
    """

    def __init__(self, name, initial_trolley=None):
        AtomicDEVS.__init__(self, name)
        Logger.__init__(self, name)

        self.state = TrackState()

        self.dequeue = self.addInPort(name='deq')
        self.board = self.addInPort(name="board")

        self.depart = self.addOutPort(name="depart")
        self.request_passengers = self.addOutPort(name="request_passengers")
        self.trolley_depart = self.addOutPort(name='trolley_depart')
        self.light_req = self.addOutPort(name="req")

        if initial_trolley is not None:
            self.attachNewTrolley(initial_trolley)

    def intTransition(self):
        self.state.current_time += self.timeAdvance()
        self.state.trigger = False
        self.log("Trigger disabled", 0)

        state = self.state.get_state()

        if state == 'initial':
            # By running the intTransition here, the light will evaluate this output and notice that the track is
            #  waiting for a trolley
            self.state.change_state('empty')
        elif state == 'trolley_arrived':
            self.state.change_state('first_wait')
        elif state == 'first_wait':
            self.log("First wait finished")
            # Starting unboarding now
            station_name = self.full_name.split('.')[1]
            self.state.unboarding_passengers = self.state.trolley.unboard_passengers(station_name)

            for i in range(len(self.state.unboarding_passengers)):
                # We're unboarding them all at once, but they're all unboarded some seconds after each other
                #  so we add the seconds here and set the unboarding time
                elapsed_time = self.state.current_time
                unboarding_time = elapsed_time + BOARDING_TIME_SECONDS * (i+1)
                self.state.unboarding_passengers[i].set_unboarding_time(unboarding_time)

            if len(self.state.unboarding_passengers) != 0:
                self.log("Start unboarding")
                self.state.change_state('unboarding')
            else:
                self.state.change_state('request_board')
        elif state == 'unboarding':
            self.state.unboarding_passengers = []
            self.state.change_state('boarding')
        elif state == 'boarding':
            if self.state.trolley.capacity_left > 0 and not self.state.all_passengers_boarded:
                self.state.change_state('request_board')
            else:
                self.state.all_passengers_boarded = False
                self.state.change_state('boarding_done')
        elif state == 'boarding_done':
            self.state.change_state('end_wait')
        elif state == 'end_wait':
            self.log("Finishing up")
            self.state.trolley = None
            self.state.trigger = True
            self.state.change_state('empty')
        self.log(f"Current state: {self.state.get_state()}", 0)

        return self.state

    def attachNewTrolley(self, trolley):
        self.state.change_state('trolley_arrived')
        self.state.trolley = trolley
        self.state.trolley.log_capacity(self.state.current_time)  # Log the capacity on every arrival
        self.log(f"Trolley arrived: {trolley}")

    def extTransition(self, inputs):
        self.log("Received external action", 0)
        self.state.current_time += self.elapsed

        state = self.state.get_state()

        if state == 'empty':
            self.state.trolley = None
            new_trolley = inputs.get(
                self.dequeue)  # TODO: We're just asking a new trolley from the input here, without first sending a request for a new one
            if new_trolley:
                self.attachNewTrolley(new_trolley)
        elif state in 'request_board':
            new_passenger = inputs.get(self.board)
            if new_passenger:
                new_passenger.set_boarding_time(self.state.current_time)
                self.state.trolley.add_passenger(new_passenger)
                self.state.change_state(
                    'boarding')  # TODO: Somehow, this code doesn't get executed, the code in outputFunc does however
                self.log(f"Boarding passenger: {new_passenger}")
                self.log(f"Trolley capacity: {self.state.trolley.get_load()}/{self.state.trolley.max_capacity}")
            else:
                # The platform sent None back, meaning everyone is on the trolley
                self.state.all_passengers_boarded = True
                self.log("All passengers have been boarded")
                self.state.change_state('boarding_done')
        self.log(f"Currently in state {self.state.get_state()}")
        return self.state

    def timeAdvance(self):
        state = self.state.get_state()

        if self.state.trigger:
            # self.log("TRIGGERREEEEED", 0)
            return 0

        # self.log(f"Setting new trigger time with state {state}", 0)

        if state == 'empty':
            return INFINITY
        elif state == 'first_wait':
            return TRACK_WAITING_TIME_SECONDS / 2
        elif state == 'unboarding':
            return len(self.state.unboarding_passengers) * BOARDING_TIME_SECONDS
        elif state == 'boarding':
            return BOARDING_TIME_SECONDS
        elif state == 'end_wait':
            # self.log("Waiting the final wait time...")
            return TRACK_WAITING_TIME_SECONDS / 2
        elif state in ('initial', 'trolley_arrived', 'request_board', 'boarding_done'):
            # All states to immediately skip, which are just to send a request to an output port
            return 0
        raise Exception(f"No time advance value set for state {state}")

    def outputFnc(self):
        """
        Output Funtion.
        """
        # Send messages (events) to a subset of the atomic-DEVS'
        # output ports by means of the 'poke' method, i.e.:
        # The content of the messages is based (typically) on current State.
        state = self.state.get_state()
        if state == 'empty' or state == 'initial':
            self.log("Requesting a new trolley")
            return {self.light_req: 'request_trolley'}
        elif state == "unboarding":
            departed_passengers = self.state.unboarding_passengers.copy()
            return {self.depart: departed_passengers}
        elif state in ("request_board", "boarding"):
            self.log("Sending boarding request")
            return {self.request_passengers: self.state.trolley.line}
        elif state == "end_wait":
            self.log("Trolley leaving track")
            return {self.trolley_depart: self.state.trolley}
        elif state in ('trolley_arrived', 'first_wait', 'boarding_done'):
            # Working with an elif instead of else to be sure we don't miss any important cases
            return {}
        raise Exception(f"No values to output for state {state} :(")
