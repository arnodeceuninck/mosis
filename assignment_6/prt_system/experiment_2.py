from assignment_6.prt_system.station import Station
from assignment_6.prt_system.prt_model import PRTModel
from pypdevs.simulator import Simulator
from pypdevs.DEVS import *

if __name__ == '__main__':
    # This didn't work so I placed the TrolleyGenerator inside the station
    # class GeneratingStation(CoupledDEVS):
    #     def __init__(self):
    #         CoupledDEVS.__init__(self, "GeneratingStation")
    #         trolleyGenerator = TrolleyGenerator()
    #         station = Station("University Square")
    #         self.station = self.addSubModel(station)
    #         self.gen = self.addSubModel(trolleyGenerator)
    #         self.connectPorts(self.gen.outport, self.station.entry)
    #

    model = PRTModel("test")
    sim = Simulator(model)
    sim.setClassicDEVS()
    sim.setVerbose("output.txt")
    # sim.setActivityTrackingVisualisation(True)
    sim.setTerminationTime(24 * 60 * 60)
    sim.simulate()

    model.statistics()
