from trolley_generator import Collector
from pypdevs.simulator import Simulator

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: THIS FILE ISN'T USED ANYMORE, PLEASE USE experiment_2.py INSTEAD!!!!!
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
if __name__ == '__main__':
    collector = Collector('test')

    sim = Simulator(collector)

    def terminate_whenStateIsReached(clock, model):
        return model.trafficLight.state.get() == "manual"


    sim.setTerminationCondition(terminate_whenStateIsReached)

    sim.setVerbose(None)
    sim.setClassicDEVS()
    sim.setTerminationTime(500)
    sim.simulate()
