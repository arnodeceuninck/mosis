#!/usr/bin/python3

from CBD.Core import CBD
from CBD.lib.std import *
from CBD.lib.endpoints import SignalCollectorBlock
from CBD.realtime.plotting import PlotManager, LinePlot, follow
from CBD.simulator import Simulator
# import time
import matplotlib.pyplot as plt

import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

DELTA_T = 0.01

class SinGen(CBD):
	def __init__(self, block_name):
		CBD.__init__(self, block_name, input_ports=[], output_ports=[])

		# Create the Blocks
		self.addBlock(GenericBlock("sin", block_operator=("sin")))
		self.addBlock(TimeBlock("time"))
		self.addBlock(SignalCollectorBlock("plot", int(10.0 / DELTA_T) + 10))
		self.addBlock(ConstantBlock("A", 1.0))
		self.addBlock(ConstantBlock("B", 1.0))
		self.addBlock(ProductBlock("amp"))
		self.addBlock(ProductBlock("per"))

		# Create the Connections
		self.addConnection("B", "per")
		self.addConnection("time", "per")
		self.addConnection("per", "sin")
		self.addConnection("A", "amp")
		self.addConnection("sin", "amp")
		self.addConnection("amp", "plot")

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
# manager.connect('sin', 'update', lambda d, axis=ax: axis.set_ylim((min(d[1]), max(d[1]))))
manager.connect('sin', 'update', lambda d, axis=ax: axis.set_ylim(follow(d[1], lower_lim=-1.0, upper_lim=1.0)))


label = tk.Label(root, text="y = 1.00 * sin(1.00 * t)")
label.grid(column=1, row=2)

def set_amplitude(val):
	cbd.findBlock("A")[0].setValue(float(val))
	update_label()

def set_period(val):
	cbd.findBlock("B")[0].setValue(float(val))
	update_label()

def update_label():
	label["text"] = "y = {:.2f} * sin({:.2f} * t)".format(cbd.findBlock("A")[0].getValue(),
	                                                      cbd.findBlock("B")[0].getValue())

amplitude = tk.Scale(root, label="Amplitude", length=1200, orient=tk.HORIZONTAL, from_=0, to=5, resolution=0.1,
                     command=set_amplitude)
amplitude.set(1.0)
amplitude.grid(column=1, row=3)
period = tk.Scale(root, label="Period", length=1200, orient=tk.HORIZONTAL, from_=0, to=5, resolution=0.01,
                  command=set_period)
period.set(1.0)
period.grid(column=1, row=4)

if __name__ == '__main__':
	# Run the Simulation
	# sim_time = 100.0
	sim = Simulator(cbd)
	sim.setRealTime()
	# sim.setProgressBar()
	sim.setDeltaT(DELTA_T)
	sim.setRealTimePlatformTk(root)
	sim.run()
	root.mainloop()
