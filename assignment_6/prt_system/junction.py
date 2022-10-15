from assignment_6.prt_system.config import *
from assignment_6.prt_system.helper import *


class JunctionState:
    def __init__(self):
        self.curr_state = 'initial'

        self.transfer_timer = 0

        self.queue = Queue()
        self.lastTrolley = None
        self.transferring_trolley = None

    def get_state(self):
        return self.curr_state

    def change_state(self, state):
        self.curr_state = state

    def enqueue(self, trolley):
        self.queue.put(trolley)

    def dequeue(self):
        trolley = self.queue.get()
        self.transferring_trolley = trolley
        return trolley

    def trolleyWaiting(self):
        return not self.queue.empty()


class Junction(AtomicDEVS, Logger):
    """"
    Atomic DEVS that identifies a merge of multiple Rails onto a single output. The Trolleys are merged according to
    their order of arrival. Furthermore, it takes 50 seconds for each Trolley to transfer the junction.
    """

    def __init__(self, name):
        AtomicDEVS.__init__(self, name)
        Logger.__init__(self, name)

        self.state = JunctionState()

        self.in1 = self.addInPort(name="In1")
        self.in2 = self.addInPort(name="In2")
        self.in3 = self.addInPort(name="In3")
        self.out = self.addOutPort(name='Out')

    def departure(self):
        trolley = self.state.dequeue()
        self.log(f"Departure: {trolley}")

    def extTransition(self, inputs):
        state = self.state.get_state()

        if state == 'transferring_start':
            self.state.transfer_timer += self.elapsed
        trigger = False
        if self.in1 in inputs:
            trolley = inputs.get(self.in1)
            if trolley:
                self.state.enqueue(trolley)
                self.log(f"Arrival on track1: {trolley}")
                trigger = True
        if self.in2 in inputs:
            trolley = inputs.get(self.in2)
            if trolley:
                self.state.enqueue(trolley)
                self.log(f"Arrival on track2: {trolley}")
                trigger = True
        if self.in3 in inputs:
            trolley = inputs.get(self.in3)
            if trolley:
                self.state.enqueue(trolley)
                self.log(f"Arrival on track3: {trolley}")
                trigger = True

        if trigger and state == 'initial':
            self.log("Transferring Starts")
            self.state.change_state('transferring_start')

        return self.state

    def intTransition(self):
        state = self.state.get_state()

        if state == 'initial':
            if self.state.queue.len() > 0:
                self.log("Transferring Starts")
                self.state.change_state('transferring_start')
            else:
                self.state.change_state('initial')
        elif state == 'transferring_start':
            if self.state.transferring_trolley is None:
                self.departure()
            self.state.change_state('transferring_end')
        elif state == 'transferring_end':
            self.state.transferring_trolley = None
            self.state.transfer_timer = 0
            if self.state.queue.len() == 0:
                self.state.change_state('initial')
            else:
                self.state.change_state('transferring_start')

        return self.state

    def outputFnc(self):
        state = self.state.get_state()

        if state == 'transferring_end' and self.state.transferring_trolley:
            return {self.out: self.state.transferring_trolley}
        elif state in ('initial', 'transferring_start'):
            # Working with an elif instead of else to be sure we don't miss any important cases
            return {}
        raise Exception(f"No values to output for state {state} :(")

    def timeAdvance(self):
        state = self.state.get_state()

        if state == 'transferring_start':
            if self.state.transfer_timer > 0:
                return TROLLEY_JUNCTION_WAIT_TIME - self.state.transfer_timer
            else:
                return TROLLEY_JUNCTION_WAIT_TIME  # seconds
        elif state == 'transferring_end':
            return 0
        elif state == 'initial':
            return INFINITY
        raise Exception(f"No time advance value set for state {state}")
