"""
Verbose tracer for the CBD Simulator.
"""

from .baseTracer import BaseTracer
from .color import COLOR

class VerboseTracer(BaseTracer):
	"""
	Verbose tracer for the CBD Simulator.
	"""
	def traceNewIteration(self, curIt, time):
		txt1 = COLOR.colorize("Iteration: ", COLOR.BOLD)
		txt2 = COLOR.colorize("{:>5}".format(curIt), COLOR.GREEN)
		txt3 = COLOR.colorize("; Time: ", COLOR.BOLD)
		txt4 = COLOR.colorize("{:>10.3}".format(time), COLOR.RED)
		rem = "_" * (self.width - 11 - 5 - 8 - 10)
		if curIt > 0:
			self.trace("\n\n")
		self.traceln("__", txt1, txt2, txt3, txt4, rem)

	def traceCompute(self, curIt, block):
		text = "\n " + COLOR.colorize(block.getPath(), COLOR.ITALIC, COLOR.CYAN) + ":"
		inps = block.getLinksIn().items()
		deps = [x.getBlockName() for x in block.getDependencies(curIt)]
		if len(inps) > 0:
			text += "\n\tINPUT VALUES:"
			for inp, (other, out) in inps:
				if other in deps:
					text += "\n\t\t{:>10} -> {:<10} : {}"\
						.format(other.getBlockName() + "." + out, inp,
					            COLOR.colorize(str(block.getInputSignal(curIt, inp).value), COLOR.YELLOW))
		outs = block.getSignals().items()
		if len(outs) > 0:
			if len(inps) > 0:
				text += "\n"
			text += "\n\tOUTPUT VALUES:"
			for out, vals in outs:
				text += "\n\t\t{:<24} : {}".format(out, COLOR.colorize(str(vals[-1].value), COLOR.YELLOW))
		self.traceln(text)
