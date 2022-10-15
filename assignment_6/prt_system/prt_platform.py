from assignment_6.prt_system.config import *
from assignment_6.prt_system.helper import *


class PlatformState:
    def __init__(self):
        self.queues = dict()
        self.boarding_passenger = None
        self.trigger = False

    def enqueue(self, passenger, line):
        if line not in self.queues:
            self.queues[line] = Queue()
        self.queues[line].put(passenger)

    def dequeue(self, line):
        if line not in self.queues or self.queues[line].empty():
            return None
        return self.queues[
            line].get()  # Be sure to check when this is empty, since it will keep evaluating forever else


class Platform(AtomicDEVS, Logger):
    """
    Atomic DEVS, identifying a location in a Station where an unlimited amount of Passengers can wait to board a
    Trolley. For the purposes of this assignment, you can assume they queue on the Platform in a first-in-first-out
    order. For every line the Station serves, a different queue may be used for simplicity reasons.
    """

    def __init__(self, name):
        AtomicDEVS.__init__(self, name)
        Logger.__init__(self, name)

        self.state = PlatformState()

        self.new_passengers = self.addInPort(name="new_passengers")
        self.request_passengers = self.addInPort(name="requested_passenger")
        self.board = self.addOutPort(name="board_passenger")

    def board_passenger(self, line):
        passenger = self.state.dequeue(line)
        # Note: This boarding message gets also sent if the passenger is None, this way the Track knows there aren't
        #  any passengers left when he receives a None message
        # if passenger is not None:
        self.state.boarding_passenger = passenger
        self.state.trigger = True
        self.log(f"Passenger boarding: {passenger}")
        # TODO: Update timers?

    def extTransition(self, inputs):
        """
        External Transition Function.
        """
        self.log("External action received", 0)

        new_passenger = inputs.get(self.new_passengers)

        if new_passenger:
            self.state.enqueue(new_passenger, new_passenger.line)  # TODO determine the line
            self.log(f"Enqueued passenger: {new_passenger}", 0)

        requested_line = inputs.get(self.request_passengers)

        if requested_line is not None:
            self.board_passenger(requested_line)
            self.log(f"Boarding passenger")
        return self.state

    def timeAdvance(self):
        if self.state.trigger:
            return 0
        return INFINITY

    def intTransition(self):
        # Not actually triggering, just making sure the new passenger external request gets sent to the Track
        self.state.trigger = False
        return self.state

    def outputFnc(self):
        return {self.board: self.state.boarding_passenger}
