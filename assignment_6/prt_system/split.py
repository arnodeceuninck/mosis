from assignment_6.prt_system.config import *
from assignment_6.prt_system.helper import *


class SplitState:
    def __init__(self):
        self.lastPort = None
        # TODO: Do I really need a seperate lastOut1 and 2, or can I just use one lastOut
        self.lastOut1 = None
        self.lastOut2 = None
        self.lastOut3 = None
        self.trigger = False

    def toOut1(self, trolley):
        self.lastPort = "out1"
        self.lastOut1 = trolley

    def toOut2(self, trolley):
        self.lastPort = "out2"
        self.lastOut2 = trolley

    def toOut3(self, trolley):
        self.lastPort = "out3"
        self.lastOut3 = trolley


class Split(AtomicDEVS, Logger):
    """
    Opposite of the Junction. There is a single input, but a set of outputs that allow a Trolley to deviate w.r.t. their
    line number. For instance, the user can define that lines 1 and 2 will be outputted on the right branch and line 3
    will be outputted on the left branch. The Trolleys should automatically follow this logic without any delay. This
    block is not a required component, but will help when creating the Station.
    """

    # TODO: Should this even be an AtomicDEVS? I don't see yet how we are going to use this state

    def __init__(self, name):
        AtomicDEVS.__init__(self, name)
        Logger.__init__(self, name)

        self.state = SplitState()
        self.inport = self.addInPort(name="In")
        self.out1 = self.addOutPort(name='Out1')
        self.out2 = self.addOutPort(name='Out2')
        self.out3 = self.addOutPort(name='Out3')

    def extTransition(self, inputs):
        self.log("External transition received")

        trolley = inputs.get(self.inport)
        # TODO: How do I determine which track a trolley must take?
        #  Check all trolleys on the line? Currently only supporting line 0, so always take track 1
        if trolley.line == 1:
            self.state.toOut1(trolley)
            self.log(f"Sent to track1: {trolley}")
        elif trolley.line == 2:
            self.state.toOut2(trolley)
            self.log(f"Sent to track2: {trolley}")
        elif trolley.line == 3:
            self.state.toOut3(trolley)
            self.log(f"Sent to track3: {trolley}")
        self.state.trigger = True
        return self.state

    def outputFnc(self):
        if self.state.lastPort == "out1":
            return {self.out1: self.state.lastOut1}
        elif self.state.lastPort == "out2":
            return {self.out2: self.state.lastOut2}
        elif self.state.lastPort == "out3":
            return {self.out3: self.state.lastOut3}
        else:
            return {}

    def intTransition(self):
        self.state.trigger = False
        return self.state

    def timeAdvance(self):
        if self.state.trigger:
            return 0
        return INFINITY
