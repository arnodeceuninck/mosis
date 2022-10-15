"""
This module contains all the logic for Runge-Kutta preprocessing.
"""
from CBD.Core import CBD
from CBD.lib.std import *
from CBD.converters.CBDDraw import draw

class RKPreprocessor:
	r"""
	Preprocesses a model to allow for Runge-Kutta approximation. This may be used to solve
	systems/initial-value problems in the form of

	.. math::
		\dfrac{dy}{dt} = f(t, y)

	Both normal approximation as well as adaptive stepsize can be done with this preprocessor.

	Args:
		tableau (CBD.preprocessing.butcher.ButcherTableau): The tableau for which RK approximation
							may be done. When this is a normal tableau, mere approximation will
							happen. When it is an extended tableau, the scale factor for the delta
							will also be computed.
		atol (float):       The absolute tolerance for precision in approximating, given that the
							tableau is an extended tableau. Defaults to 1e-8.
		hmin (float):       Minimal value for the delta, given that the tableau is an extended
							tableau. When non-extended, this will identify the clock delta.
							Defaults to 1e-40.
		hmax (float):       Maximal value for the delta, given that the tableau is an extended
							tableau. This value will also be used as the initial delta.
							Defaults to 1e-1.
		safety (float):     Safety factor for the error computation. Must be in (0, 1], preferrably
							on the high end of the range. For RKF45, commonly :math:`2^{-1/4} \approx 0.84`
							is used. Defaults to 0.9.
	"""
	def __init__(self, tableau, atol=1e-8, hmin=1e-40, hmax=1e-1, safety=0.9):
		assert atol > 0, "Tolerance must be a positive value"
		self._tableau = tableau
		self._tolerance = atol
		self._h_range = hmin, hmax
		self._safety = safety

	def preprocess(self, original):
		"""
		Do the actual preprocessing on a model.

		The model will be cloned and than flattened, such that the groups limited by
		:class:`CBD.lib.std.IntegratorBlock` and other memory blocks are collected
		as the initial-value problem they represent. From there, a new CBD model will
		be constructed, representative of the Runge-Kutta approximation with a given
		Butcher Tableau.

		When there are no :class:`CBD.lib.std.IntegratorBlock` available in the model,
		the original model will be returned.

		Args:
			original (CBD.Core.CBD): A CBD model to get the RK approximating model for.

		Warning:
			Currently, this fuction will yield undefined behaviour if the original model
			has input ports with a name that matches :code:`(IN\\d+|((rel_)?time))`,
			output ports that match :code:`OUT\\d+` and non-clock steering blocks with
			prefix :code:`"clock"`.
		"""
		# TODO: rename colliding blocks (e.g. change the capitalization or add a prefix for RK-system)
		# 1. Detect IVP based on integrators
		IVP, plinks = self.create_IVP(original)

		if len(plinks) == 0:
			return original

		# 2. Create an RK-model, based on the given tableau
		RK = self.create_RK(IVP)
		# draw(RK, "test.dot")

		# 3. Substitute the RK-model collection in the original CBD
		outputs = original.getSignals().keys()
		inputs = original.getInputPortNames()
		new_model = CBD(original.getBlockName(), inputs, outputs)
		new_model.addBlock(RK)
		for inp in inputs:
			if RK.hasBlock(inp):
				new_model.addConnection(inp, RK, inp)
		old_clock = original.getClock()
		new_model.addBlock(Clock("clock", old_clock.getTime(0) - old_clock.getRelativeTime(0)))
		new_model.addConnection("clock", RK, 'time', 'time')
		new_model.addConnection("clock", RK, 'rel_time', 'rel_time')
		if RK.hasBlock("h_new"):
			# TODO: take delta from original
			new_model.addBlock(ConstantBlock("HIC", self._h_range[1]))
			new_model.addBlock(DelayBlock("HDelay"))
			new_model.addConnection(RK, "HDelay", output_port_name="h_new")
			new_model.addConnection("HIC", "HDelay", input_port_name="IC")
			new_model.addConnection("HDelay", "clock", input_port_name="h")
			new_model.addConnection("clock", RK, input_port_name="h", output_port_name='delta')
		else:
			# TODO: take delta from original
			new_model.addBlock(ConstantBlock("clock-delta", self._h_range[0]))
			new_model.addConnection("clock-delta", "clock", "h")
			new_model.addConnection("clock-delta", RK, "h")
		for y in outputs:
			itg, mop = original.getBlockByName(y).getBlockConnectedToInput("IN1")
			if itg.getBlockName() in plinks:
				p = plinks[itg.getBlockName()]
				new_model.addConnection(RK, y, output_port_name='OUT%d' % p)
				ic, icop = itg.getBlockConnectedToInput("IC")
				collection = self.collect(ic, finish=[IntegratorBlock, Clock, TimeBlock])
				if not new_model.hasBlock(ic.getBlockName()):
					new_model.addBlock(ic.clone())
				for block in collection:
					if not new_model.hasBlock(block.getBlockName()):
						new_model.addBlock(block.clone())
				for block in collection:
					cs = block.getInputPortNames()
					for c in cs:
						cb, op = block.getBlockConnectedToInput(c)
						if cb.getBlockName() in plinks:
							raise ValueError("Too complex Initial Condition for integrator %s" % cb.getBlockName())
						elif cb.getBlockType() == "TimeBlock":
							new_model.addConnection("clock", block.getBlockName(), c, "time")
						elif cb.getBlockType() == "Clock":
							new_model.addConnection("clock", block.getBlockName(), c, op)
						else:
							new_model.addConnection(cb.getBlockName(), block.getBlockName(), c, op)
						new_model.addConnection(cb.getBlockName(), block.getBlockName(), c, op)
				new_model.addConnection(ic.getBlockName(), RK, "IC%d" % p, icop)
			else:
				# parallel process
				collection = self.collect(original.getBlockByName(y), finish=[IntegratorBlock, Clock, TimeBlock])
				for block in collection:
					if not new_model.hasBlock(block.getBlockName()):
						new_model.addBlock(block.clone())
				for block in collection:
					cs = block.getInputPortNames()
					for c in cs:
						cb, op = block.getBlockConnectedToInput(c)
						if cb.getBlockName() in plinks:
							new_model.addConnection(RK, block.getBlockName(), c, "OUT%d" % plinks[cb.getBlockName()])
						elif cb.getBlockType() == "TimeBlock":
							new_model.addConnection("clock", block.getBlockName(), c, "time")
						elif cb.getBlockType() == "Clock":
							new_model.addConnection("clock", block.getBlockName(), c, op)
						else:
							new_model.addConnection(cb.getBlockName(), block.getBlockName(), c, op)
				new_model.addConnection(itg.getBlockName(), y, output_port_name=mop)

		return new_model

	def collect(self, start, sport=None, finish=None):
		"""
		Breadth-first search collection of all blocks, starting from the start block and
		ending when it can't anymore or when it must finish.

		Args:
			start (CBD.Core.BaseBlock): The block to start from. This block will be excluded
										from the collection.
			sport (iter):               The set of ports on the start block to use. When
										:code:`None` or omitted, all ports will be used.
										Note that only the start block can have a specification
										for the allowed ports.
			finish (iter):              A set of block types (not strings, the actual types!) to
										exclude from the collection, halting a branch whenever
										one of these has been reached.
		"""
		if finish is None:
			finish = []
		collection = [x[1].block for x in start.getLinksIn().items() if \
		              ((sport is not None and x[0] in sport) or (sport is None)) \
		                and not isinstance(x[1].block, tuple(finish))]
		n_collection = [x.getBlockName() for x in collection]
		for block in collection:
			ccoll = self.collect(block, None, finish)
			for child in ccoll:
				cname = child.getBlockName()
				if cname not in n_collection:
					n_collection.append(cname)
					collection.append(child)
		return collection

	def create_IVP(self, original):
		"""
		Detects the set of equations that make up the initial-value problem and
		constructs a CBD submodel that contains them. Multiple equations, branches
		and extra inputs are all taken into account.

		For every integrator, the IVP will contain an input and an output port,
		who will be linked as such.

		Args:
			original:   The model to create the IVP for. This model will **not** be
						altered by this fuction.

		Returns:
			Tuple of :code:`IVP, plinks` where :code:`IVP` identifies the CBD for the
			IVP equations and :code:`plinks` a dictionary of
			:code:`IntegratorBlock name -> index`.
		"""
		model = original.clone()
		model.flatten(ignore=[IntegratorBlock, Clock])
		blocks = model.getBlocks()
		IVP = CBD("IVP", ["time", "rel_time"], [])
		i = 0
		plinks = {}
		iblocks = []
		for block in blocks:
			if isinstance(block, DelayBlock):
				raise RuntimeError("Impossible to construct Runge-Kutta model for Delay Differential Equations!")
			if isinstance(block, IntegratorBlock):
				# Identify all integrators and give them their in- and outputs
				i += 1
				IVP.addInputPort("IN%d" % i)
				IVP.addOutputPort("OUT%d" % i)

				# Links for future reference
				plinks[block.getBlockName()] = i
				iblocks.append(block)
		for block in iblocks:
			collection = self.collect(block, ["IN1"], [IntegratorBlock, TimeBlock, Clock])

			# First add the blocks
			for child in collection:
				if child.getBlockType() == "InputPortBlock":
					IVP.addInputPort(child.getBlockName())
				elif child.getBlockType() == "OutputPortBlock":
					IVP.addOutputPort(child.getBlockName())
				else:
					IVP.addBlock(child.clone())

			# Next, link the blocks
			for child in collection:
				for name_input, link in child.getLinksIn().items():
					lbn = link.block.getBlockName()
					lop = link.output_port
					if not IVP.hasBlock(lbn):
						# Both the TimeBlock and the Clock's time output will be explicitly inputted,
						# hence, it is the predefined port
						if link.block.getBlockType() == "TimeBlock":
							lbn = 'time'
						elif link.block.getBlockType() == "Clock":
							lbn = lop
						elif lbn in plinks:
							# Other integrator input
							p = plinks[lbn]
							lbn = "IN%d" % p
						else:
							# DelayBlock or Clock outputs that have not been linked yet
							lbn = name_input + "-" + child.getBlockName()
							IVP.addInputPort(lbn)
						lop = None
					IVP.addConnection(lbn, child.getBlockName(), name_input, lop)
			# Link the output
			p = plinks[block.getBlockName()]
			fin = block.getBlockConnectedToInput("IN1")
			fname = fin.block.getBlockName()
			if fname in plinks:
				fname = "IN%d" % plinks[fname]
			IVP.addConnection(fname, "OUT%d" % p, None, fin.output_port)
		return IVP, plinks

	def create_RK(self, f):
		"""
		Creates the CBD for determining a Runge-Kutta weighed sum in the form of

		.. math::
			y_{n+1} = y_n + \sum_{i=1}^s b_i k_i

		Args:
			f (CBD.Core.CBD):   The CBD representing the actual IVP for which the
								RK approximation must be done.
		"""
		# TODO: optimizations:
		#  - adder "YSum_2_?" is not required for higher order, since it is
		#    always followed by a subtraction of the same y_n-value
		RK = CBD("RK", ["h", "time", "rel_time"])
		fy = range(1, len(f.getSignals()) + 1)
		weights = list(reversed(self._tableau.getWeights()))
		s = len(weights[0])
		for y in fy:
			RK.addInputPort("IC%d" % y)
			RK.addOutputPort("OUT%d" % y)
			RK.addBlock(DelayBlock("delay_%d" % y))
			RK.addConnection("IC%d" % y, "delay_%d" % y, input_port_name='IC')
			RK.addConnection("delay_%d" % y, "OUT%d" % y)
		inpnames = [x for x in f.getInputPortNames() if x not in ["time", "rel_time"] + ["IN%d" % x for x in fy]]
		for inp in inpnames:
			RK.addInputPort(inp)
		for q in range(len(weights)):
			for y in fy:
				RK.addBlock(AdderBlock("RKSum_%d_%d" % (q + 1, y), s))
				RK.addBlock(AdderBlock("YSum_%d_%d" % (q + 1, y)))
				RK.addConnection("RKSum_%d_%d" % (q + 1, y), "YSum_%d_%d" % (q + 1, y))
				if q == 0 or q != len(weights) - 1:
					RK.addConnection("YSum_%d_%d" % (q + 1, y), "delay_%d" % y, input_port_name='IN1')
				RK.addConnection("delay_%d" % y, "YSum_%d_%d" % (q + 1, y))
		for i in range(s):
			j = i + 1
			RK.addBlock(self.create_K(j, f.clone()))
			for inp in inpnames:
				RK.addConnection(inp, "RK-K_%d" % j, inp)
			for y in fy:
				RK.addConnection("delay_%d" % y, "RK-K_%d" % j, input_port_name='IN%d' % y)
			for p in range(len(weights)):
				q = p + 1
				RK.addBlock(ConstantBlock("B%d_%d" % (q, j), weights[p][i]))
				for y in fy:
					RK.addBlock(ProductBlock("Mult%d_%d_%d" % (q, y, j)))
					RK.addConnection("B%d_%d" % (q, j), "Mult%d_%d_%d" % (q, y, j))
					RK.addConnection("RK-K_%d" % j, "Mult%d_%d_%d" % (q, y, j), output_port_name="OUT%d" % y)
					RK.addConnection("Mult%d_%d_%d" % (q, y, j), "RKSum_%d_%d" % (q, y))
			RK.addConnection("h", "RK-K_%d" % j, "h")
			RK.addConnection("time", "RK-K_%d" % j, "time")
			RK.addConnection("rel_time", "RK-K_%d" % j, "rel_time")
			for s in range(i):
				RK.addConnection("RK-K_%d" % (s+1), "RK-K_%d" % j, "k_%d" % (s+1))

		# Error Computation
		if len(weights) == 2:
			RK.addOutputPort("h_new")
			RK.addBlock(self.create_Error(len(fy)))
			for y in fy:
				for q in range(len(weights)):
					RK.addConnection("YSum_1_%d" % y, "error", "y_%d" % y)
					RK.addConnection("YSum_2_%d" % y, "error", "z_%d" % y)
			RK.addConnection("h", "error", input_port_name="h")
			RK.addConnection("error", "h_new", output_port_name='h_new')

		return RK

	def create_K(self, s, f):
		r"""
		Creates the CBD for determining the :math:`k_s`-value in the Runge-Kutta
		approximation computation. The generic formula is:

		.. math::
			k_s = h\cdot f\left(t_n + c_s\cdot h, y_n + \sum_{i=1}^{s-1}a_{s, i} k_i\right)

		Args:
			s (int):            The :math:`s`-value of the :math:`k_s` to compute.
			f (CBD.Core.CBD):   The CBD representing the actual IVP for which the
								RK approximation must be done.
		"""
		input_ports = ["h", "time", "rel_time"] + ["k_%d" % (i+1) for i in range(s-1)]
		fy = [x for x in f.getInputPortNames() if x not in ["time", "rel_time"]]
		input_ports += fy
		K = CBD("RK-K_%d" % s, input_ports, [])
		K.addBlock(f)

		# Time parameter
		K.addBlock(ConstantBlock("C", self._tableau.getNodes()[s-1]))
		K.addBlock(ProductBlock("CMult"))
		K.addBlock(AdderBlock("CSum"))
		K.addConnection("h", "CMult")
		K.addConnection("C", "CMult")
		K.addConnection("time", "CSum")
		K.addConnection("CMult", "CSum")
		K.addConnection("CSum", f.getBlockName(), "time")
		K.addConnection("rel_time", f.getBlockName(), "rel_time")

		# Y parameters
		if s - 1 > 0:
			K.addBlock(AdderBlock("KSum", s - 1))
			for i in range(s-1):
				j = i + 1
				K.addBlock(ConstantBlock("A_%d" % j, self._tableau.getA(s-1, j)))
				K.addBlock(ProductBlock("Mult_%d" % j))
				K.addConnection("A_%d" % j, "Mult_%d" % j)
				K.addConnection("k_%d" % j, "Mult_%d" % j)
				K.addConnection("Mult_%d" % j, "KSum")
			for y in fy:
				if y.startswith("IN"):
					K.addBlock(AdderBlock("YSum-%s" % y))
					K.addConnection(y, "YSum-%s" % y)
					K.addConnection("KSum", "YSum-%s" % y)
					K.addConnection("YSum-%s" % y, f.getBlockName(), y)
				else:
					K.addConnection(y, f.getBlockName(), y)
		else:
			for y in fy:
				K.addConnection(y, f.getBlockName(), y)

		# Finishing Up
		outputs = f.getSignals().keys()
		for j, y in enumerate(outputs):
			i = j + 1
			K.addOutputPort("OUT%d" % i)
			K.addBlock(ProductBlock("FMult_%d" % i))
			K.addConnection("h", "FMult_%d" % i)
			K.addConnection(f.getBlockName(), "FMult_%d" % i, output_port_name=y)
			K.addConnection("FMult_%d" % i, "OUT%d" % i)

		return K

	def create_Error(self, vlen):
		r"""
		Creates the error computation block, which computes:

		.. math::
			h_{new} = h_{old}\cdot clamp\left(S\cdot\left(\dfrac{\epsilon\cdot h_{old}}
			{\vert z_{n+1} - y_{n+1}\vert}\right)^{\dfrac{1}{q}}, 0.1, 4.0\right)

		Where :math:`\epsilon` is the provided error tolerance, :math:`q` the lowest order of the computation,
		:math:`z_{n+1}` the higher-order (more precise) value and :math:`y_{n+1}` the lower-order computation
		that will also be outputted. When :math:`y` and :math:`z` consist of multiple elements, a pessimistic
		approach is used, obtaining the maximal error.

		See Also:
			`Press, William H., H. William, Saul A. Teukolsky, A. Saul, William T. Vetterling, and Brian P. Flannery.
			2007. "Numerical recipes 3rd edition: The art of scientific computing", Chapter 16, pp. 714-722.
			Cambridge University Press. <https://people.cs.clemson.edu/~dhouse/courses/817/papers/adaptive-h-c16-2.pdf>`_
		"""
		Err = CBD("error", ["h"] + ["y_%d" % (i+1) for i in range(vlen)] + ["z_%d" % (i+1) for i in range(vlen)],
		          ["h_new", "error"])

		Err.addBlock(ConstantBlock("Tol", self._tolerance))
		Err.addBlock(ConstantBlock("Eps", 1e-20))
		Err.addBlock(MaxBlock("Max", vlen+1))
		Err.addConnection("Eps", "Max")
		Err.addConnection("Max", "error")
		for i in range(vlen):
			j = i + 1
			Err.addBlock(NegatorBlock("Neg_%i" % j))
			Err.addBlock(AdderBlock("Sum_%i" % j))
			Err.addBlock(AbsBlock("Abs_%i" % j))
			Err.addConnection("y_%d" % j, "Neg_%d" % j)
			Err.addConnection("Neg_%d" % j, "Sum_%d" % j)
			Err.addConnection("z_%d" % j, "Sum_%d" % j)
			Err.addConnection("Sum_%d" % j, "Abs_%d" % j)
			Err.addConnection("Abs_%d" % j, "Max")

		Err.addBlock(InverterBlock("hinv"))
		Err.addConnection("h", "hinv")
		Err.addBlock(ProductBlock("R"))
		Err.addConnection("Max", "R")
		Err.addConnection("hinv", "R")
		Err.addBlock(InverterBlock("Rinv"))
		Err.addConnection("R", "Rinv")
		Err.addBlock(ProductBlock("RinvMult"))
		Err.addConnection("Rinv", "RinvMult")
		Err.addConnection("Tol", "RinvMult")
		Err.addBlock(RootBlock("Root"))
		Err.addBlock(ConstantBlock("q", self._tableau.getOrder()))
		Err.addConnection("RinvMult", "Root", input_port_name='IN1')
		Err.addConnection("q", "Root", input_port_name='IN2')
		Err.addBlock(ConstantBlock("S", self._safety))
		Err.addBlock(ProductBlock("SMult"))
		Err.addConnection("S", "SMult")
		Err.addConnection("Root", "SMult")
		Err.addBlock(ClampBlock("Clamp", 0.1, 4.0))
		Err.addConnection("SMult", "Clamp")
		Err.addBlock(ProductBlock("HMult"))
		Err.addConnection("h", "HMult")
		Err.addConnection("Clamp", "HMult")
		Err.addBlock(ClampBlock("HClamp", self._h_range[0], self._h_range[1]))
		Err.addConnection("HMult", "HClamp")
		Err.addConnection("HClamp", "h_new")

		return Err


if __name__ == '__main__':
	from CBD.preprocessing.butcher import ButcherTableau as BT
	from CBD.converters.CBDDraw import draw
	DELTA_T = 0.1

	class Test(CBD):
		def __init__(self, name):
			super().__init__(name, [], ['v', 'x'])

			self.addBlock(ConstantBlock('x0', 0))
			self.addBlock(ConstantBlock('v0', 0))
			self.addBlock(ConstantBlock('k', 0.15))
			self.addBlock(ConstantBlock("five", 5))
			self.addBlock(NegatorBlock("neg"))
			self.addBlock(AdderBlock("sum", 3))
			self.addBlock(ProductBlock("mult"))
			self.addBlock(IntegratorBlock("Iv"))
			self.addBlock(IntegratorBlock("Ix"))

			self.addConnection("five", "sum")
			self.addConnection("v0", "neg")
			self.addConnection("neg", "sum")
			self.addConnection("sum", "mult")
			self.addConnection("k", "mult")
			self.addConnection("mult", "Iv")
			self.addConnection("Iv", "sum")
			self.addConnection("Iv", "v")
			self.addConnection("Iv", "Ix")
			self.addConnection("Ix", "x")
			self.addConnection("v0", "Iv", input_port_name='IC')
			self.addConnection("x0", "Ix", input_port_name='IC')

			self.addFixedRateClock("clock", 0.1)
			self.addConnection("clock-clock", "Iv", output_port_name="delta", input_port_name='delta_t')
			self.addConnection("clock-clock", "Ix", output_port_name="delta", input_port_name='delta_t')

	test = Test("Test")
	# test.addFixedRateClock("clock", 0.1)
	prep = RKPreprocessor(BT.RKF45(), atol=2e-5, hmin=1e-8, safety=.84)
	model = prep.preprocess(test)
	draw(model, "test.dot")
	# model = Test("Test")

	from CBD.simulator import Simulator
	sim = Simulator(model)
	sim.setDeltaT(0.2)
	sim.run(1.4)

	s = model.getSignal("v")
	L = len(s)
	errs = model.findBlock("RK.error")[0].getSignal("error")
	hs = model.findBlock("RK.error")[0].getSignal("h_new")
	# errs = hs = s

	# print([x for _, x in model.findBlock("RK.myDelay")[0].getSignal("OUT1")])

	import numpy as np
	print("+------------+------------+------------+------------+------------+------------+")
	print("|    TIME    |    VALUE   |     TAN    |    ERROR   |   OFFSET   |    DELTA   |")
	print("+------------+------------+------------+------------+------------+------------+")
	for i in range(L):
		t, v = s[i]
		actual = np.tan(t)
		error = abs(actual - v)
		print("| {t:10.7f} | {v:10.7f} | {h:10.7f} | {e:10.7f} | {o:10.7f} | {d:10.7f} |"
		      .format(t=t, v=v, h=actual, e=error, o=errs[i].value, d=hs[i].value))
	print("+------------+------------+------------+------------+------------+------------+")

	import matplotlib.pyplot as plt

	fig, ax = plt.subplots()
	ax.plot(np.arange(0.0, 1.4, 0.01), [np.tan(t) for t in np.arange(0.0, 1.4, 0.01)], label="tan(t)")
	ax.plot([t for t, _ in s], [v for _, v in s], label="estimate")
	ax.legend()
	plt.show()
