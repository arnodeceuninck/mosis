from assignment_6.prt_system.config import *
from assignment_6.prt_system.helper import *


class Generator(AtomicDEVS, Logger):
    """"
    Atomic DEVS that generates Passengers according to a normal distributed inter-arrival process with a mean of 5
    minutes and a standard deviation of 1 minute. For each Passenger, a random destination is chosen. This destination
    does not have to be reachable from the starting point.
    Code based on the generator from the queue_example_classic
    """

    def __init__(self, station_name, lines, name="Passenger Generator"):
        AtomicDEVS.__init__(self, name)
        Logger.__init__(self, name)
        assert lines is not None

        self.state = {"station_name": station_name, "lines": lines}
        self.state["current_passenger"] = self.random_passenger()

        # self.state["passengers_left"] = 10 # Used for setting a limit on the number of passengers to generate
        self.outport = self.addOutPort("generated_passenger")

    def random_passenger(self):
        lines = self.state["lines"]
        line = random.choice(lines)
        return Passenger(orig=self.state["station_name"], line=line)

    def get_random_next_time(self):
        avg = minutes_to_seconds(GENERATOR_AVG_MINUTES)
        standard_deviation = minutes_to_seconds(GENERATOR_DEVIATION_MINUTES)
        time = RANDOM_STATE.normal(loc=avg, scale=standard_deviation)
        assert isinstance(time, float)
        return time

    def timeAdvance(self):
        next_time = self.get_random_next_time()
        if self.state:
            self.log(f"Next passenger in {int(next_time)}s", 0)
            return next_time
        else:
            self.log("Stopped generating passengers")
            # State should normaly never be set to false, but just leaving this hear in case we wan't to be able to
            #  disable the Generator in the future.
            return INFINITY

    def outputFnc(self):
        # Our message is the generated passenger
        return {self.outport: self.state["current_passenger"]}

    def intTransition(self):
        # On transition, generate a new random passenger
        passenger = self.random_passenger()
        self.state["current_passenger"] = passenger
        self.log(f"Generated a new passenger: {passenger}", 0)
        # self.state["passengers_left"] -= 1
        # if not self.state["passengers_left"]:
        #     self.state = False
        return self.state
