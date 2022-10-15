from assignment_6.prt_system.config import *
from assignment_6.prt_system.helper import *
from assignment_6.prt_system.rail import Rail
from assignment_6.prt_system.track import Track
from assignment_6.prt_system.prt_platform import Platform
from assignment_6.prt_system.collector import Collector
from assignment_6.prt_system.light import Light
from assignment_6.prt_system.split import Split
from assignment_6.prt_system.trolley_generator import TrolleyGenerator
from assignment_6.prt_system.generator import Generator


class Station(CoupledDEVS, Logger):
    """
    Coupled DEVS model that contains a Generator, a Collector, a Platform, a Track, a Light and possibly a Split. The
    Station serves a set of n lines. For simplicity, there is a single input and n outputs (see the Split logic above).
    The figure below shows a shematic overview of how a Station is created with the given list of components.
    """

    def __init__(self, name, lines, generate_trollies=False, initial_trolley=None):
        CoupledDEVS.__init__(self, name)
        Logger.__init__(self, name)

        self.state = None # State contains only the start trolley if there should be one

        # Declare the submodels
        self.generator = self.addSubModel(Generator(name, lines, f"Passenger Generator {name}"))
        self.platform = self.addSubModel(Platform(f"Platform {name}"))
        self.track = self.addSubModel(Track(f"Track {name}", initial_trolley=initial_trolley))
        self.collector = self.addSubModel(Collector(f"Collector {name}"))
        self.light = self.addSubModel(Light(f"Light {name}"))
        self.split = self.addSubModel(Split(f"Split {name}"))

        # TODO: This should be just a connection to the rail
        self.trolley_gen = None
        if generate_trollies:
            self.trolley_gen = self.addSubModel(TrolleyGenerator(f"Trolley Generator {name}"))

        # Connect the ports
        # Start with generator
        # Connect platform
        self.connectPorts(self.generator.outport, self.platform.new_passengers)
        # Conntect track
        self.connectPorts(self.track.request_passengers, self.platform.request_passengers)
        self.connectPorts(self.platform.board, self.track.board)
        # Connect Collector
        self.connectPorts(self.track.depart, self.collector.input_port)
        # Connect Light
        self.connectPorts(self.track.light_req, self.light.request)
        self.connectPorts(self.light.dequeue, self.track.dequeue)
        # Connect Split
        self.connectPorts(self.track.trolley_depart, self.split.inport)

        if self.trolley_gen is not None:
            self.connectPorts(self.trolley_gen.outport, self.light.entry)

    #     # Define the interface
        self.entry = self.addInPort(self.light.entry)
        self.out1 = self.addOutPort(self.split.out1)
        self.out2 = self.addOutPort(self.split.out2)
        self.out3 = self.addOutPort(self.split.out3)

        self.connectPorts(self.entry, self.light.entry)
        self.connectPorts(self.split.out1, self.out1)
        self.connectPorts(self.split.out2, self.out2)
        self.connectPorts(self.split.out3, self.out3)

        # Ports for launching the initial trolley in the system
        # self.trolley_start = self.addOutPort("trolley_start")
        # self.connectPorts(self.trolley_start, self.light.entry)

    # def extTransition(self, inputs):
    #     # Don't know whether this is allowed
    #     print("Yeeehaaa")
    #     return self.light.extTransition(inputs)

    # def intTransition(self):
    #     self.state = None
    #     return self.state

    # def start_trolley(self, trolley):
    #     # This function can only be called when the simulation hasn't started yet
    #     # This lets a trolley start in the light
    #     self.state = trolley

    # def advanceTime(self):
    #     if self.state is not None:
    #         return 0
    #     else:
    #         return INFINITY

    # def outputFnc(self):
    #     return {self.trolley_start: self.state}
    #     # print("GOT HERE")
    #     # return {self.out1: self.split.out1, self.out2: self.split.out2}  # TODO: How to properly connect those outputs
