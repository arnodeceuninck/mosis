#!/usr/bin/python3
# This file was automatically generated from drawio2cbd with the command:
#   /home/red/git/DrawioConvert/__main__.py SinGen.xml -fav -F CBD -e SinGen -E delta=0.1

from CBD.realtime.plotting import PlotManager, LinePlot, follow
from CBD.simulator import Simulator
from SinGen import *
import time
import matplotlib.pyplot as plt
from matplotlib import style

style.use('ggplot')

import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

DELTA_T = 0.1

fig = plt.figure(figsize=(15, 5), dpi=100)
ax = fig.add_subplot(111)
ax.set_ylim((-1, 1))

cbd = SinGen("SinGen")

root = tk.Tk()

canvas = FigureCanvasTkAgg(fig, master=root)  # A Tk DrawingArea
canvas.draw()
canvas.get_tk_widget().grid(column=1, row=1)

manager = PlotManager()
manager.register("sin", cbd.findBlock("plot")[0], (fig, ax), LinePlot())
manager.connect('sin', 'update', lambda d, axis=ax: axis.set_xlim(follow(d[0], 10.0, lower_bound=0.0)))

# plt.show(block=False)

# def term(*_):
# 	plt.draw()
# 	plt.pause(0.01)
# 	return not manager.is_opened()

# Run the Simulation
sim_time = 100.0
sim = Simulator(cbd)
sim.setRealTime()
sim.setProgressBar()
sim.setDeltaT(DELTA_T)
sim.setRealTimePlatformTk(root)
# sim.setTerminationCondition(term)
sim.run(sim_time)
root.mainloop()

# while sim.is_running():
# # 	plt.draw()
# # 	plt.pause(0.01)
#
# 	# Game Loop (time managing must be done by the user):
# 	before = time.time()
# 	sim.realtime_gameloop_call()
# 	time.sleep(DELTA_T - (before - time.time()))


# PLOT THE DURATION LOG
log = sim.getDurationLog()
fig2 = plt.figure()
ax2 = fig2.subplots()
ax2.set_title("Block Computation [Plotting Manager + TkInter] (T = {:.2f}, dt = {:.2f})".format(sim_time, DELTA_T))
ax2.set_xlabel("Iterations")
ax2.set_ylabel("Time")
# ax2.plot([-1, len(log)], [DELTA_T, DELTA_T], c='red')
# ax2.plot([-1, len(log)], [0.01, 0.01], c='green')
ax2.bar(range(len(log)), log)
# plt.show()
