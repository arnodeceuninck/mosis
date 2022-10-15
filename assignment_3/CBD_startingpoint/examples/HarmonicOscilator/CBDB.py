#!/usr/bin/python3
# This file was automatically generated from drawio2cbd with the command:
#   ../../drawio2cbd.py Harmonic.xml CBDB.py -e ErrorB -t 1000 -T 0.01

from CBD.Core import CBD
from CBD.simulator import Simulator
from CBD.lib.std import *
DELTA_T = 0.01


class IntegratorBlock(CBD):
	def __init__(self, block_name):
		super().__init__(block_name, input_ports=["IC", "IN1", "delta_t"], output_ports=["OUT1"])
		self.addBlock(ProductBlock("mul"))
		self.addBlock(AdderBlock("sum"))
		self.addBlock(AdderBlock("sum_ic"))
		self.addBlock(DelayBlock("delay"))
		self.addBlock(NegatorBlock("neg"))

		self.addConnection("IN1", "mul")
		self.addConnection("delta_t", "mul")
		self.addConnection("mul", "sum")
		self.addConnection("delay", "sum")
		self.addConnection("sum", "delay")
		self.addConnection("IC", "sum_ic")
		self.addConnection("neg", "sum_ic")
		self.addConnection("sum_ic", "delay", input_port_name="IC")
		self.addConnection("mul", "neg")
		self.addConnection("sum", "OUT1")



import matplotlib.pyplot as plt


def plot_signals(block, signals, title):
	times = []
	outputs = []

	for signal in signals:
		tvpl = block.getSignal(signal)
		times = [t for t, _ in tvpl]
		outputs.append([v for _, v in tvpl])

	# Plot
	plt.figure()
	plt.title(title)
	plt.xlabel('time')
	plt.ylabel('N')
	for i in range(len(signals)):
		plt.plot(times, outputs[i], label=signals[i])
	plt.legend()
	plt.show()




class HarmonicB(CBD):
	def __init__(self, block_name):
		CBD.__init__(self, block_name, input_ports=['dt'], output_ports=['x'])
		
		# Create the blocks
		self.addBlock(DerivatorBlock(block_name='deriv1'))
		self.addBlock(DerivatorBlock(block_name='deriv2'))
		self.addBlock(ConstantBlock(block_name='zero', value=(0)))
		self.addBlock(ConstantBlock(block_name='one', value=(1)))
		self.addBlock(NegatorBlock(block_name='neg'))
		
		# Connect the blocks
		self.addConnection('dt', 'deriv1', input_port_name='delta_t')
		self.addConnection('dt', 'deriv2', input_port_name='delta_t')
		self.addConnection('deriv1', 'deriv2')
		self.addConnection('one', 'deriv1', input_port_name='IC')
		self.addConnection('zero', 'deriv2', input_port_name='IC')
		self.addConnection('deriv2', 'neg')
		self.addConnection('neg', 'deriv1')
		self.addConnection('neg', 'x')


class HarmonicA(CBD):
	def __init__(self, block_name):
		CBD.__init__(self, block_name, input_ports=['dt'], output_ports=['x'])
		
		# Create the blocks
		self.addBlock(IntegratorBlock(block_name='int2'))
		self.addBlock(IntegratorBlock(block_name='int1'))
		self.addBlock(ConstantBlock(block_name='zero', value=(0)))
		self.addBlock(ConstantBlock(block_name='one', value=(1)))
		self.addBlock(NegatorBlock(block_name='neg'))
		
		# Connect the blocks
		self.addConnection('dt', 'int2', input_port_name='delta_t')
		self.addConnection('dt', 'int1', input_port_name='delta_t')
		self.addConnection('zero', 'int2', input_port_name='IC')
		self.addConnection('one', 'int1', input_port_name='IC')
		self.addConnection('int2', 'x')
		self.addConnection('int2', 'neg')
		self.addConnection('neg', 'int1')
		self.addConnection('int1', 'int2')


class ErrorA(CBD):
	def __init__(self, block_name, dt=(DELTA_T)):
		CBD.__init__(self, block_name, input_ports=[], output_ports=['e', 'real', 'A'])
		
		# Create the blocks
		self.addBlock(SinBlock(block_name='sin'))
		self.addBlock(NegatorBlock(block_name='neg'))
		self.addBlock(AdderBlock(block_name='sum'))
		self.addBlock(AbsBlock(block_name='abs'))
		self.addBlock(IntegratorBlock(block_name='int'))
		self.addBlock(ConstantBlock(block_name='dt', value=(dt)))
		self.addBlock(ConstantBlock(block_name='zero', value=(0)))
		self.addBlock(HarmonicA(block_name='harmonic'))
		
		# Connect the blocks
		self.addConnection('sin', 'sum')
		self.addConnection('neg', 'sum')
		self.addConnection('sum', 'abs')
		self.addConnection('zero', 'int', input_port_name='IC')
		self.addConnection('dt', 'int', input_port_name='delta_t')
		self.addConnection('abs', 'int')
		self.addConnection('int', 'e')
		self.addConnection('harmonic', 'neg', output_port_name='x')
		self.addConnection('dt', 'harmonic', input_port_name='dt')
		self.addConnection('sin', 'real')
		self.addConnection('harmonic', 'A', output_port_name='x')


class SinBlock(CBD):
	def __init__(self, block_name):
		CBD.__init__(self, block_name, input_ports=[], output_ports=['OUT1'])
		
		# Create the blocks
		self.addBlock(TimeBlock(block_name='time'))
		self.addBlock(GenericBlock(block_name='sin', block_operator=("sin")))
		
		# Connect the blocks
		self.addConnection('time', 'sin')
		self.addConnection('sin', 'OUT1')


class ErrorB(CBD):
	def __init__(self, block_name, dt=(DELTA_T)):
		CBD.__init__(self, block_name, input_ports=[], output_ports=['e', 'B', 'real'])
		
		# Create the blocks
		self.addBlock(SinBlock(block_name='sin'))
		self.addBlock(NegatorBlock(block_name='neg'))
		self.addBlock(AdderBlock(block_name='sum'))
		self.addBlock(AbsBlock(block_name='abs'))
		self.addBlock(IntegratorBlock(block_name='int'))
		self.addBlock(ConstantBlock(block_name='dt', value=(dt)))
		self.addBlock(ConstantBlock(block_name='zero', value=(0)))
		self.addBlock(HarmonicB(block_name='harmonic'))
		
		# Connect the blocks
		self.addConnection('sin', 'sum')
		self.addConnection('neg', 'sum')
		self.addConnection('sum', 'abs')
		self.addConnection('zero', 'int', input_port_name='IC')
		self.addConnection('dt', 'int', input_port_name='delta_t')
		self.addConnection('abs', 'int')
		self.addConnection('int', 'e')
		self.addConnection('harmonic', 'neg', output_port_name='x')
		self.addConnection('dt', 'harmonic', input_port_name='dt')
		self.addConnection('harmonic', 'B', output_port_name='x')
		self.addConnection('sin', 'real')


if __name__ == '__main__':
	outputs = []
	signals = []
	for dt in [0.1, 0.01, 0.001]:
		# cbdB = ErrorB("ErrorB", dt=dt)
		# # Run the simulation
		# cbdB.run(int(10/dt), delta_t=dt)
		# tvpl = cbdB.getSignal("e")
		# outputs.append(tvpl)
		# signals.append("B " + str(dt))
		# plot_signals(cbdB, ['real', 'B'], f'Value B ({dt})')

		cbdA = ErrorA("ErrorA", dt=dt)
		# Run the simulation
		sim = Simulator(cbdA)
		sim.setDeltaT(dt)
		sim.run(int(10/dt))
		tvpl = cbdA.getSignal("e")
		outputs.append(tvpl)
		signals.append("A " + str(dt))
		plot_signals(cbdA, ['real', 'A'], f'Value A ({dt})')

	plt.figure()
	plt.title("Error")
	plt.xlabel('time')
	plt.ylabel('N')
	for i in range(3):
		time = [x for x, _ in outputs[i]]
		value = [x for _, x in outputs[i]]
		plt.plot(time, value, label=signals[i])
	plt.legend()
	plt.show()

