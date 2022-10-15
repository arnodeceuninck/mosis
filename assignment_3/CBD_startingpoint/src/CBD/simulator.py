import sys
import time
import threading
from . import naivelog
from .depGraph import createDepGraph
from .solver import LinearSolver
from .realtime.threadingBackend import ThreadingBackend, Platform
from .util import PYTHON_VERSION, hash64
from .scheduling import TopologicalScheduler
from .tracers import Tracers
from .lib.std import Clock

_TQDM_FOUND = True
try:
	from tqdm import tqdm
except ImportError:
	_TQDM_FOUND = False


class Simulator:
	"""
	Simulator for a CBD model. Allows for execution of the simulation.
	This class implements the semantics of CBDs.

	Args:
		model (CBD):    A :class:`CBD` model to simulate.

	:Defaults:
		The following properties further define the internal mechanisms of
		the simulator. As a handy look-up table, all defaults are listed
		in the table below. Take a look at the :code:`See Also` column for
		more info on the property.

	.. list-table::
	   :widths: 20 40 40
	   :header-rows: 1

	   * - Property
	     - Default
	     - See Also
	   * - real-time?
	     - :code:`False`
	     - :func:`setRealTime`
	   * - real-time scale
	     - 1.0
	     - :func:`setRealTime`
	   * - termination time
	     - :code:`float('inf')`
	     - :func:`setTerminationTime`
	   * - termination condition
	     - :code:`None`
	     - :func:`setTerminationCondition`
	   * - scheduler
	     - :class:`CBD.scheduling.TopologicalScheduler`
	     - :func:`setScheduler`
	   * - threading platform (subsystem)
	     - :class:`CBD.realtime.threadingPython.threadingPython`
	     - :func:`setRealTimePlatform`, :func:`setRealTimePlatformThreading`,
	       :func:`setRealTimePlatformTk`, :func:`setRealTimePlatformGameLoop`
	   * - progress bar?
	     - :code:`False`
	     - :func:`setProgressBar`
	   * - strong component system solver
	     - :class:`CBD.solver.LinearSolver`
	     - N/A
	"""
	def __init__(self, model):
		self.model = model

		self.__deltaT = 1.0
		self.__realtime = False
		self.__finished = True
		self.__stop_requested = False

		# scale of time in the simulation.
		self.__realtime_scale = 1.0
		# maximal amount of events with delay 0
		self.__realtime_counter_max = 100
		# current amount of events
		self.__realtime_counter = self.__realtime_counter_max
		# Starting time of the simulation
		self.__realtime_start_time = 0.0

		self.__termination_time = float('inf')
		self.__termination_condition = None

		# simulation data [dep graph, strong components, curIt]
		self.__sim_data = [None, None, 0]

		# self.__stepsize_backend = Fixed(self.__deltaT)
		self.__scheduler = TopologicalScheduler()

		self.__threading_backend = None
		self.__threading_backend_subsystem = Platform.PYTHON
		self.__threading_backend_args = []

		self.__progress = False
		self.__progress_event = None
		self.__progress_finished = True
		self.__logger = naivelog.getLogger("CBD")
		self.__tracer = Tracers()

		self.__lasttime = None

		self.__events = {
			"started": [],
			"finished": [],
			"prestep": [],
			"poststep": [],
			"clock_update": []
		}
		
		# TODO: make this variable, given more solver implementations
		# self.__solver = SympySolver(self.__logger)
		self.__solver = LinearSolver(self.__logger)

	def run(self, term_time=None):
		"""
		Simulates the model.

		Args:
			term_time (float):  When not :code:`None`, overwrites the
								termination time with the new value.
		"""
		self.__finished = False
		self.__stop_requested = False
		if term_time is not None:
			self.__termination_time = term_time

		if self.getClock() is None:
			self.model.addFixedRateClock("clock", self.__deltaT)

		self.__sim_data = [None, None, 0]
		self.__progress_finished = False
		if self.__threading_backend is None:
			# If there is still a backend, it is the same, so keep it!
			self.__threading_backend = ThreadingBackend(self.__threading_backend_subsystem,
		                                                self.__threading_backend_args)

		if _TQDM_FOUND and self.__progress and self.__termination_time < float('inf'):
			# Setup progress bar if possible
			thread = threading.Thread(target=self.__progress_update)
			thread.daemon = True
			thread.start()

		if self.__realtime:
			self.__realtime_start_time = time.time()
			self.__lasttime = 0.0

		self.signal("started")
		if self.__realtime:
			self.__threading_backend.wait(0.0, self.__runsim)
		else:
			self.__runsim()

	def __finish(self):
		"""
		Terminate the simulation.
		"""
		self.__finished = True
		if not self.__progress:
			# Whenever the progress bar is initialized, wait until it ends
			self.__progress_finished = True
		self.__tracer.stopTracers()
		self.signal("finished")

	def __check(self):
		"""
		Checks if the simulation still needs to continue.
		This is done based on the termination time and condition.

		Returns:
			:code:`True` if the simulation needs to be terminated and
			:code:`False` otherwise.
		"""
		ret = self.__stop_requested
		if self.__termination_condition is not None:
			ret = self.__termination_condition(self.model, self.__sim_data[2])
		return ret or self.__termination_time <= self.getTime()

	def stop(self):
		"""
		Requests a termination of the current running simulation.
		"""
		self.__stop_requested = True

	def is_running(self):
		"""
		Returns :code:`True` as long as the simulation is running.
		This is a convenience function to keep real-time simulations
		alive, or to interact from external sources.
		"""
		return not self.__progress_finished and not self.__finished

	def getClock(self):
		"""
		Gets the simulation clock.

		See Also:
			- :func:`getTime`
			- :func:`getRelativeTime`
			- :func:`getDeltaT`
			- :func:`setDeltaT`
			- :class:`CBD.lib.std.Clock`
		"""
		return self.model.getClock()

	def getTime(self):
		"""
		Gets the current simulation time.

		See Also:
			- :func:`getClock`
			- :func:`getRelativeTime`
			- :func:`getDeltaT`
			- :func:`setDeltaT`
			- :class:`CBD.lib.std.Clock`
		"""
		return self.getClock().getTime(self.__sim_data[2])

	def getRelativeTime(self):
		"""
		Gets the current simulation time, ignoring a starting offset.

		See Also:
			- :func:`getClock`
			- :func:`getTime`
			- :func:`getDeltaT`
			- :func:`setDeltaT`
			- :class:`CBD.lib.std.Clock`
		"""
		return self.getClock().getRelativeTime(self.__sim_data[2])

	def getDeltaT(self):
		"""
		Gets the delta in-between iteration steps.

		See Also:
			- :func:`getClock`
			- :func:`getTime`
			- :func:`getRelativeTime`
			- :func:`setDeltaT`
			- :class:`CBD.lib.std.Clock`
		"""
		clock = self.getClock()
		return clock.getInputSignal(input_port='h').value

	def setDeltaT(self, delta_t):
		"""
		Sets the delta in-between iteration steps.

		Args:
			delta_t (float):    The delta.

		Note:
			If the model has a :class:`CBD.lib.std.Clock` block instance, calling
			this function will have no effect. It is merely meant to be used for
			fixed step simulations.

		Note:
			While unnecessary, this function is kept for backwards compatibility.

		See Also:
			- :func:`getClock`
			- :func:`getTime`
			- :func:`getRelativeTime`
			- :func:`getDeltaT`
			- :class:`CBD.lib.std.Clock`
			- :func:`setStepSize`
		"""
		self.__deltaT = delta_t

	def setScheduler(self, scheduler):
		"""
		Sets the scheduler for the simulation. It will identify the
		order of the components in a computation.

		Args:
			scheduler (CBD.scheduling.Scheduler):   The scheduler to use.
		"""
		self.__scheduler = scheduler

	def setBlockRate(self, block_path, rate):
		"""
		Sets the rate for a specific block. Independent of the stepsize, the
		rate will identify that a certain block must only execute every
		:code:`r` time.

		Note:
			Blocks for which no rate has been set will always be computed.

		Args:
			block_path (str):   The path of the block to set a rate of.
			rate (float):       The rate of the block.
		"""
		self.__scheduler.setRate(block_path, rate)

	def setRealTime(self, enabled=True, scale=1.0):
		"""
		Makes the simulation run in (scaled) real time.

		Args:
			enabled (bool): When :code:`True`, realtime simulation will be enabled.
							Otherwise, it will be disabled. Defaults to :code:`True`.
			scale (float):  Optional scaling for the simulation time. When greater
							than 1, the simulation will run slower than the actual
							time. When < 1, it will run faster.
							E.g. :code:`scale = 2.0` will run twice as long.
							Defaults to :code:`1.0`.
		"""
		self.__realtime = enabled
		# Scale of 2 => twice as long
		self.__realtime_scale = scale

	def setProgressBar(self, enabled=True):
		"""
		Uses the `tqdm <https://tqdm.github.io/>`_ package to display a progress bar
		of the simulation.

		Args:
			enabled (bool): Whether or not to enable/disable the progress bar.
							Defaults to :code:`True` (= show progress bar).

		Note:
			A progressbar hijacks printing to the console, hence no output shall be
			shown.

		Raises:
			AssertionError: if the :code:`tqdm` module cannot be located.
		"""
		assert _TQDM_FOUND, "Module tqdm not found. Progressbar is not possible."
		self.__progress = enabled

	def setTerminationCondition(self, func):
		"""
		Sets the system's termination condition.

		Args:
			func:   A function that takes the model and the current iteration as input
					and produces :code:`True` if the simulation needs to terminate.

		Note:
			When set, the progress bars (see :func:`setProgressBar`) may not work as intended.

		See Also:
			:func:`setTerminationTime`
		"""
		# TODO: allow termination condition to set progressbar update value?
		self.__termination_condition = func

	def setTerminationTime(self, term_time):
		"""
		Sets the termination time of the system.

		Args:
			term_time (float):  Termination time for the simulation.
		"""
		self.__termination_time = term_time

	def setRealTimePlatform(self, subsystem, *args):
		"""
		Sets the realtime platform to a platform of choice.
		This allows more complex/efficient simulations.

		Calling this function automatically sets the simulation to realtime.

		Args:
			subsystem (Platform):   The platform to use.
			args:                   Optional arguments for this platform.
									Currently, only the TkInter platform
									makes use of these arguments.

		Note:
			To prevent misuse of the function, please use one of the wrapper
			functions when you have no idea what you're doing.

		See Also:
			- :func:`setRealTimePlatformThreading`
			- :func:`setRealTimePlatformTk`
			- :func:`setRealTimePlatformGameLoop`
		"""
		self.setRealTime(True)
		self.__threading_backend = None
		self.__threading_backend_subsystem = subsystem
		self.__threading_backend_args = args

	def setRealTimePlatformThreading(self):
		"""
		Wrapper around the :func:`setRealTimePlatform` call to automatically
		set the Python Threading backend.

		Calling this function automatically sets the simulation to realtime.

		See Also:
			- :func:`setRealTimePlatform`
			- :func:`setRealTimePlatformTk`
			- :func:`setRealTimePlatformGameLoop`
		"""
		self.setRealTimePlatform(Platform.THREADING)

	def setRealTimePlatformGameLoop(self):
		"""
		Wrapper around the :func:`setRealTimePlatform` call to automatically
		set the Game Loop backend. Using this backend, it is expected the user
		will periodically call the :func:`realtime_gameloop_call` method to
		update the simulation step. Timing is still maintained internally.

		Calling this function automatically sets the simulation to realtime.

		See Also:
			- :func:`setRealTimePlatform`
			- :func:`setRealTimePlatformThreading`
			- :func:`setRealTimePlatformTk`
			- :func:`realtime_gameloop_call`
			- :doc:`examples/RealTime`
		"""
		self.setRealTimePlatform(Platform.GAMELOOP)

	def setRealTimePlatformTk(self, root):
		"""
		Wrapper around the :func:`setRealTimePlatform` call to automatically
		set the TkInter backend.

		Calling this function automatically sets the simulation to realtime.

		Args:
			root:   TkInter root window object (tkinter.Tk)

		See Also:
			- :func:`setRealTimePlatform`
			- :func:`setRealTimePlatformThreading`
			- :func:`setRealTimePlatformGameLoop`
		"""
		self.setRealTimePlatform(Platform.TKINTER, root)

	def realtime_gameloop_call(self, time=None):
		"""
		Do a step in the realtime-gameloop platform.

		Args:
			time (float):   Simulation time to be passed on. Only to be used
							for the alternative gameloop backend.

		Note:
			This function will only work for a :attr:`Platform.GAMELOOP` or a
			:attr:`Platform.GLA` simulation, after the :func:`run` method has
			been called.

		See Also:
			- :func:`setRealTimePlatform`
			- :func:`setRealTimePlatformGameLoop`
			- :func:`run`
		"""
		self.__threading_backend.step(time)

	def _do_single_step(self):
		"""
		Does a single simulation step.

		Danger:
			Do **not** use this function to forcefully progress the simulation!
			All functionalities for validly simulating and executing a system
			that are provided through other parts of the interface should be
			sufficient to do a viable simulation. This function should only be
			used by the inner workings of the simulator and its functional parts.
		"""
		self.signal("prestep")
		curIt = self.__sim_data[2]
		self.__tracer.traceNewIteration(curIt, self.getTime())
		# Efficiency reasons: dep graph only changes at these times
		#   in the given set of library blocks.
		# TODO: Must be set to "every time" instead.
		if curIt < 2 or self.__sim_data[0] is None:
			self.__sim_data[0] = createDepGraph(self.model, curIt)
			# self.__sim_data[1] = self.__sim_data[0].getStrongComponents(curIt)
		self.__sim_data[1] = self.__scheduler.obtain(self.__sim_data[0], curIt, self.getTime(), self.getRelativeTime())
		self.__computeBlocks(self.__sim_data[1], self.__sim_data[0], self.__sim_data[2])
		self.__sim_data[2] += 1
		self.signal("poststep")

	def _rewind(self):
		self.__sim_data[2] -= 1
		self.model._rewind()

	def __realtimeWait(self):
		"""
		Wait until next realtime event.

		Returns:
			:code:`True` if a simulation stop is required and
			:code:`False` otherwise.
		"""
		current_time = time.time() - self.__realtime_start_time
		next_sim_time = min(self.__termination_time, self.__lasttime + self.getDeltaT())

		# Scaled Time
		next_sim_time *= self.__realtime_scale

		# Subtract the time that we already did our computation
		wait_time = next_sim_time - current_time
		self.__lasttime = next_sim_time / self.__realtime_scale

		if wait_time <= 0.0:
			# event is overdue => force execute
			self.__realtime_counter -= 1
			if self.__realtime_counter < 0:
				# Too many overdue events at a time
				self.__realtime_counter = self.__realtime_counter_max
				self.__threading_backend.wait(0.01, self.__runsim)
				return True
			return False

		self.__realtime_counter = self.__realtime_counter_max
		self.__threading_backend.wait(wait_time, self.__runsim)
		return True

	def __runsim(self):
		"""
		Do the actual simulation.
		"""
		self.__realtime_counter = self.__realtime_counter_max
		while True:
			if self.__check():
				self.__finish()
				break

			# self._update_clock()
			self._do_single_step()

			if self.__threading_backend_subsystem == Platform.GLA:
				self.__threading_backend.wait(self.getDeltaT(), self.__runsim)
				break

			if self.__realtime and self.__realtimeWait():
				# Next event has been scheduled, kill this process
				break

	def __computeBlocks(self, sortedGraph, depGraph, curIteration):
		"""
		Compute the new state of the model.

		Args:
			sortedGraph:        The set of strong components.
			depGraph:           A dependency graph.
			curIteration (int): Current simulation iteration.
		"""
		for component in sortedGraph:
			if not self.__hasCycle(component, depGraph):
				block = component[0]  # the strongly connected component has a single element
				if curIteration == 0 or self.__scheduler.mustCompute(block, self.getTime()):
					block.compute(curIteration)
					self.__tracer.traceCompute(curIteration, block)
			else:
				# Detected a strongly connected component
				self.__solver.checkValidity(self.model.getPath(), component)
				solverInput = self.__solver.constructInput(component, curIteration)
				solutionVector = self.__solver.solve(solverInput)
				for block in component:
					if curIteration == 0 or self.__scheduler.mustCompute(block, self.getTime()):
						blockIndex = component.index(block)
						block.appendToSignal(solutionVector[blockIndex])
						self.__tracer.traceCompute(curIteration, block)

	def __hasCycle(self, component, depGraph):
		"""
		Determine whether a component is cyclic or not.

		Args:
			component (list):   The set of strong components.
			depGraph:           The dependency graph.
		"""
		assert len(component) >= 1, "A component should have at least one element"
		if len(component) > 1:
			return True
		else:  # a strong component of size one may still have a cycle: a self-loop
			if depGraph.hasDependency(component[0], component[0]):
				return True
			else:
				return False

	def __progress_update(self):
		"""
		Updates the progress bar.
		"""
		assert _TQDM_FOUND, "Module tqdm not found. Progressbar is not possible."
		end = self.__termination_time
		pbar = tqdm(total=end, bar_format='{desc}: {percentage:3.0f}%|{bar}| {n:.2f}/{total_fmt} '
		                                  '[{elapsed}/{remaining}, {rate_fmt}{postfix}]')
		last = 0.0
		while not self.__finished:
			now = self.getTime()
			# print(end, now, last)
			pbar.update(min(now, end) - last)
			last = now
			time.sleep(0.5)     # Only update every half a second
		if last < end:
			pbar.update(end - last)
		pbar.close()
		# TODO: prints immediately after break pbar...
		self.__progress_finished = True

	def connect(self, name, function):
		"""
		Connect an event with an additional function.

		The functions will be called in the order they were connected to the
		events, with the associated arguments. The accepted signals are:

		- :code:`started`:              Raised whenever the simulation setup has
										completed, but before the actual simulation
										begins.
		- :code:`finished`:             Raised whenever the simulation finishes.
		- :code:`prestep`:              Raised before a step is done.
		- :code:`poststep`:             Raised after a step is done.
		- :code:`clock_update(delta)`:  Raised whenever the clock updates. It takes
										the (new) delta for the simulation.

		Args:
			name (str):     The name of the signal to raise.
			function:       A function that will be called with the optional arguments
							whenever the event is raised.

		Warning:
			The more computationally expensive the set of connected signals is, the less
			precise real-time simulation will be. A signal is meant to have a little hook
			on when certain events happen. It is **not** meant for complex data analysis.
		"""
		if name not in self.__events:
			raise ValueError("Invalid signal '%s' in Simulator." % name)
		self.__events[name].append(function)

	def signal(self, name, *args):
		"""
		Raise a signal with a specific name and arguments.

		The accepted signals are:

		- :code:`started`:              Raised whenever the simulation setup has
										completed, but before the actual simulation
										begins.
		- :code:`finished`:             Raised whenever the simulation finishes.
		- :code:`prestep`:              Raised before a step is done.
		- :code:`poststep`:             Raised after a step is done.
		- :code:`clock_update(delta)`:  Raised whenever the clock updates. It takes
										the (new) delta for the simulation.

		Note:
			Normally, users do not need to call this function.

		Args:
			name (str):     The name of the signal to raise.
			*args:          Additional arguments to pass to the connected events.

		See Also:
			:func:`connect`
		"""
		if name not in self.__events:
			raise ValueError("Invalid signal '%s' in Simulator." % name)
		for evt in self.__events[name]:
			evt(*args)

	def setCustomTracer(self, *tracer):
		"""
		Sets a custom tracer.

		Args:
			*tracer:    Either a single instance of a subclass of
						:class:`CBD.tracers.baseTracer.BaseTracer` or three elements
						:code:`filename` (str), :code:`classname` (str) and
						:code:`args` (tuple) to allow instantiation similar to
						`PythonPDEVS <http://msdl.cs.mcgill.ca/projects/DEVS/PythonPDEVS>`_.

		Note:
			Calling this function multiple times with the same arguments will continuously add
			new tracers. Thus output to multiple files is possible, though more inefficient than
			simply (manually) copying the file at the end.
		"""
		if len(tracer) == 1:
			self.__tracer.registerTracer(tracer[0])
		elif len(tracer) == 3:
			self.__tracer.registerTracer(tracer)
		else:
			raise ValueError("Invalid amount of arguments for custom tracer.")

	def setVerbose(self, filename=None):
		"""
		Sets the verbose tracer.

		Args:
			filename (str): The file to which the trace must be written.
							When :code:`None`, the trace will be written to
							the console.

		Note:
			Calling this function multiple times will continuously add new tracers. Thus output
			to multiple files is possible, though more inefficient than simply (manually) copying
			the file at the end.

		Danger:
			Using multiple verbose tracers with the same filename will yield errors and undefined
			behaviour.
		"""
		self.setCustomTracer("tracerVerbose", "VerboseTracer", (filename,))
