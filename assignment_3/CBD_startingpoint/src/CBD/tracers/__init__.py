"""
The tracers module provides an interface for tracing simulation data.
"""
from CBD.tracers.baseTracer import BaseTracer

class Tracers:
	"""
	Collection object for multiple tracers.

	Note:
		This class will maintain and keep track of the UID of a tracer.
		Don't set this yourself!
	"""
	def __init__(self):
		self.uid = 0
		self.tracers = {}

	def registerTracer(self, tracer, recover=False):
		"""
		Registers a specific tracer to use.

		Args:
			tracer:         Either a tuple of :code:`(file, classname, [args])`,
							similar to `PythonPDEVS <http://msdl.cs.mcgill.ca/projects/DEVS/PythonPDEVS>`_;
							or an instance of a subclass of :class:`CBD.tracers.baseTracer.BaseTracer`.
			recover (bool): Whether or not this is a recovered registration; i.e. whether or not the trace
			                file should be appended. Defaults to :code:`False`.
		"""
		if isinstance(tracer, tuple) and len(tracer) == 3:
			try:
				exec("from CBD.tracers.%s import %s" % tracer[:2])
			except:
				exec("from %s import %s" % tracer[:2])
			self.tracers[self.uid] = eval("%s(%i, *%s)" % (tracer[1], self.uid, tracer[2]))
		elif isinstance(tracer, BaseTracer):
			tracer.uid = self.uid
			self.tracers[self.uid] = tracer
		self.tracers[self.uid].startTracer(recover)
		self.uid += 1

	def deregisterTracer(self, uid):
		"""
		Stops and removes a specific tracer.

		Args:
			uid (int):  The tracer id to stop.
		"""
		if uid in self.tracers:
			self.tracers[uid].stopTracer()
			del self.tracers[uid]

	def stopTracers(self):
		"""
		Stops all tracers.
		"""
		for tracer in self.tracers.values():
			tracer.stopTracer()

	def getById(self, uid):
		"""
		Obtains a specific tracer.

		Args:
			uid (int):  The tracer id to obtain.

		Raises:
			ValueError: If the tracer does not exist.
		"""
		if uid in self.tracers:
			return self.tracers[uid]
		raise ValueError("No such tracer %d." % uid)

	def traceNewIteration(self, curIt, time):
		"""
		Traces a new iteration start.

		Args:
			curIt (int):    The current iteration.
			time (numeric): The current simulation time.
		"""
		for tracer in self.tracers.values():
			tracer.traceNewIteration(curIt, time)

	def traceCompute(self, curIteration, block):
		"""
		Traces the computation of a specific block.

		Args:
			curIteration (int):         The current iteration.
			block (CBD.Core.BaseBlock): The block for which a compute just happened.
		"""
		for tracer in self.tracers.values():
			tracer.traceCompute(curIteration, block)
