from CBD.Core import CBD
from CBD.lib.std import GenericBlock
from CBD.lib.endpoints import SignalCollectorBlock

class SinGen(CBD):
	def __init__(self, name="SinGen"):
		CBD.__init__(self, name, input_ports=[], output_ports=[])

		# Create the blocks
		self.addFixedRateClock("clock", 0.1)
		self.addBlock(GenericBlock("sin", block_operator="sin"))
		self.addBlock(SignalCollectorBlock("collector"))

		# Connect the blocks
		self.addConnection("clock-clock", "sin", output_port_name='time')
		self.addConnection("sin", "collector")

sinGen = SinGen("SinGen")

from CBD.realtime.plotting import PlotManager, LinePlot, follow
from CBD.simulator import Simulator
import matplotlib.pyplot as plt
# from matplotlib.animation import PillowWriter
#
fig = plt.figure(figsize=(5, 5), dpi=100)
ax = fig.add_subplot(111)
ax.set_ylim((-1, 1))    # The sine wave never exceeds this range

manager = PlotManager()
manager.register("sin", sinGen.findBlock('collector')[0], (fig, ax), LinePlot(color='red'))
manager.connect('sin', 'update', lambda d, axis=ax: axis.set_xlim(follow(d[0], 10.0, lower_bound=0.0)))

sim = Simulator(sinGen)
sim.setVerbose("test.txt")
sim.setRealTime()
sim.run(20.0)

# writer = PillowWriter(fps=25)
# manager.get('sin').get_animation().save("demo_sine.gif", writer=writer)
#
plt.show()
