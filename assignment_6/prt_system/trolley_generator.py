from assignment_6.prt_system.config import *
from assignment_6.prt_system.helper import *


class TrolleyGenerator(AtomicDEVS, Logger):
    """"
    Not described in the assigment. This generates random trolleys.
    """

    def __init__(self, name="Trolley Generator"):
        AtomicDEVS.__init__(self, name)
        Logger.__init__(self, name)

        self.state = {"current_trolley": self.random_trolley(), "generated_trollies": []}
        self.state["trollies_left"] = 1  # Used for setting a limit on the number of trollies to generate
        self.outport = self.addOutPort("generated_trolley")

    def random_trolley(self):
        trolley = Trolley()
        # for i in range(5):
        #     trolley.add_passenger(Passenger())

        return trolley

    def timeAdvance(self):
        # next_time = minutes_to_seconds(20)
        next_time = 0 # Only generating 1 trolly, this can be generated immediately
        if self.state["trollies_left"]:
            self.log(f"Next trolley in {int(next_time)}s", 1)
            return next_time
        else:
            self.log("Done generating trollies")
            return INFINITY

    def outputFnc(self):
        # Our message is the generated trolley
        return {self.outport: self.state["current_trolley"]}

    def intTransition(self):
        # On transition, generate a new random passenger
        trolley = self.random_trolley()
        self.state["current_trolley"] = trolley
        self.log(f"Generated a new trolley: {trolley}")
        self.state["generated_trollies"].append(trolley)
        self.state["trollies_left"] -= 1
        return self.state
