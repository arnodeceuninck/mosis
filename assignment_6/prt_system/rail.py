from assignment_6.prt_system.config import *
from assignment_6.prt_system.helper import *


class RailState:
    def __init__(self, distance, line_num, src, dst):
        self.curr_state = 'initial'

        self.src = src
        self.dst = dst
        self.line_num = line_num
        self.distance = distance  # km
        self.trolley_queue = Queue()
        self.dispatched_trolley = None

        self.trigger = False

    def add_trolley(self, new_trolley):
        self.trolley_queue.put(new_trolley)
        # TODO: Compute using distance and velocity the time this Trolley is on the track

    def dispatch_trolley(self):
        self.dispatched_trolley = self.trolley_queue.get()

    def get_state(self):
        return self.curr_state

    def change_state(self, state):
        self.curr_state = state


class Rail(AtomicDEVS, Logger):
    """
    Atomic DEVS, identifying a segment over which trolleys can travel (in a single direction). They have a certain
    distance, which can be combined with a Trolley's velocity to obtain the transit time for this Rail. Trolleys cannot
    pass each other and there must be at least a 10 second delay between the departure of two Trolleys. For instance, a
    faster Trolley A will leave the Rail 10 seconds after the slower Trolley B if B is in front of A. For simplicity,
    there can be an infinite amount of Trolleys on a Rail.
    """

    def __init__(self, name, distance, line_num, src, dst):
        AtomicDEVS.__init__(self, name)
        Logger.__init__(self, name)

        self.state = RailState(distance, line_num, src, dst)

        self.in1 = self.addInPort(name="In1")
        self.out = self.addOutPort(name='Out')

    def intTransition(self):
        self.log("Internal transitions")

        self.state.trigger = False

        state = self.state.get_state()

        if state == 'initial':
            if self.state.trolley_queue.len() > 0:
                self.log("Dispatching Starts")
                self.state.change_state('dispatch')
            else:
                self.state.change_state('initial')
        elif state == 'dispatch':
            self.state.dispatched_trolley = None
            if self.state.trolley_queue.len() == 0:
                self.state.change_state('initial')
            else:
                self.state.dispatch_trolley() # TODO: Is this right?

        return self.state

    def extTransition(self, inputs):
        self.log("Received external action", 0)

        state = self.state.get_state()

        new_trolley = inputs.get(self.in1)
        if new_trolley:
            self.log(f"Trolley Entered: {new_trolley}", 4)
            self.log(f"Passengers in trolley: {new_trolley.psgr_str()}", 4)
            self.state.add_trolley(new_trolley)
            self.state.change_state('dispatch')
            self.state.trigger = True

        return self.state

    def timeAdvance(self):
        if self.state.trigger:
            return 0

        state = self.state.get_state()

        if state == 'dispatch' and self.state.dispatched_trolley:
            computed_travel_time_hours = self.state.distance / self.state.dispatched_trolley.velocity
            computed_travel_time_seconds = computed_travel_time_hours * 3600
            if computed_travel_time_seconds > MIN_RAIL_TROLLEY_WAIT_SECONDS:
                return computed_travel_time_seconds
            else:
                return MIN_RAIL_TROLLEY_WAIT_SECONDS
        elif state == 'initial':  # sanity check where we should not have any undefined state
            return INFINITY
        raise Exception(f"No time advance value set for state {state}")

    def outputFnc(self):
        state = self.state.get_state()
        if state == 'dispatch':
            return {self.out: self.state.dispatched_trolley}
        elif state in ('initial'):
            # Working with an elif instead of else to be sure we don't miss any important cases
            return {}
        raise Exception(f"No values to output for state {state} :(")
