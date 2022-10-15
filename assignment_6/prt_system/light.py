from assignment_6.prt_system.config import *
from assignment_6.prt_system.helper import *


class LightState:
    def __init__(self):
        self.queue = Queue()
        self.lastTrolley = None
        self.track_waiting = False  # True if the track already sent a request, but no response got sent
        self.trigger = False

    def enqueue(self, trolley):
        self.queue.put(trolley)

    def dequeue(self):
        if self.queue.empty():
            return None
        self.lastTrolley = self.queue.get()
        return self.lastTrolley


class Light(AtomicDEVS, Logger):
    """"
    Simple first-come-first-served queue that releases elements upon requests.
    """

    def __init__(self, name):
        AtomicDEVS.__init__(self, name)
        Logger.__init__(self, name)

        self.state = LightState()

        self.entry = self.addInPort(name="trolley entry")
        self.request = self.addInPort(name="req")
        self.dequeue = self.addOutPort(name='deq')

    def dequeue_trolley(self):
        # This function should only get called if a request for a trolley has already been sent by the Track
        trolley = self.state.dequeue()
        if trolley is None:
            # If we don't have a trolley yet, remember that the track is waiting for a trolley
            self.state.track_waiting = True
            self.log("Got request, waiting for a trolley to arrive")
        else:
            self.state.track_waiting = False
            self.state.trigger = True  # Fire an internal transition, to send the updated output to the Track
            self.log(f"Trolley left: {trolley}")

    def intTransition(self):
        self.state.trigger = False
        return self.state

    def extTransition(self, inputs):
        self.log("Received external action", 0)
        if self.entry in inputs:
            trolley = inputs.get(self.entry)
            self.state.enqueue(trolley)
            self.log(f"Trolley arrived: {trolley}")

            if self.state.track_waiting:
                # Immediately dequeue the trolley, since the track is still waiting
                self.dequeue_trolley()

        if self.request in inputs:
            # A new trolley got requested
            self.dequeue_trolley()

        return self.state

    def outputFnc(self):
        return {self.dequeue: self.state.lastTrolley}

    def timeAdvance(self):
        if self.state.trigger:
            return 0
        return INFINITY