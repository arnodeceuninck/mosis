from CBD.Core import CBD
from CBD.lib.std import TimeBlock, GenericBlock
from CBD.lib.endpoints import SignalCollectorBlock

class SinGen(CBD):
	def __init__(self, name="SinGen"):
		CBD.__init__(self, name, input_ports=[], output_ports=[])

		# Create the blocks
		self.addBlock(TimeBlock("time"))
		self.addBlock(GenericBlock("sin", block_operator="sin"))
		self.addBlock(SignalCollectorBlock("collector"))

		# Connect the blocks
		self.addConnection("time", "sin")
		self.addConnection("sin", "collector")

sinGen = SinGen("SinGen")

from CBD.realtime.plotting import PlotManager, Backend, LinePlot, follow
from CBD.simulator import Simulator

from bokeh.plotting import figure, curdoc
from bokeh.client import push_session

fig = figure(plot_width=500, plot_height=500, y_range=(-1, 1))
curdoc().add_root(fig)

manager = PlotManager(Backend.BOKEH)
manager.register("sin", sinGen.findBlock('collector')[0], fig, LinePlot(color='red'))

def set_xlim(limits):
	lower, upper = limits
	fig.x_range.start = lower
	fig.x_range.end = upper
manager.connect('sin', 'update', lambda d: set_xlim(follow(d[0], 10.0, lower_bound=0.0)))

session = push_session(curdoc())
session.show()
import time
time.sleep(2)



sim = Simulator(sinGen)
sim.setRealTime()
sim.setDeltaT(0.1)
sim.run(20.0)

# NOTE: currently, there can be 'flickering' of the plot
while manager.is_opened():
	session.push()
	time.sleep(0.1)
