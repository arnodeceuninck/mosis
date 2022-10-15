#!/usr/bin/python3
# This file was automatically generated from drawio2cbd with the command:
#   /home/red/git/DrawioConvert/__main__.py EvenNumberGen.xml -av -F CBD -e LCG -t 30 -f

from CBD.src.lib.endpoints import SignalCollectorBlock
from EvenNumberGen import *
from CBD.simulator import Simulator
import matplotlib.pyplot as plt
from CBD.realtime.plotting import PlotManager, ScatterPlot, follow

fig = plt.figure(figsize=(15, 5), dpi=100)
ax = fig.add_subplot(1, 1, 1)

cbd = LCG("LCG")

manager = PlotManager()
manager.register("gen", sinGen.findBlock('collector')[0], (fig, ax), ScatterPlot())
manager.connect('gen', 'update', lambda d, axis=ax: axis.set_xlim(follow(d[0], 10.0, lower_bound=0.0)))

# Run the Simulation
sim = Simulator(cbd)
sim.setRealTime()
sim.setProgressBar()
sim.run(30.0)

while sim.is_running(): pass
