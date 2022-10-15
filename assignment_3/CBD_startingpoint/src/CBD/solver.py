import math
from .Core import CBD, InputPortBlock
from .util import PYTHON_VERSION

from CBD.lib.std import *

if PYTHON_VERSION == 3:
	# Python 2 complient
	from functools import reduce


# Superclass for possible additional solvers
class Solver:
	"""
	Superclass that can solve algebraic loops.

	Args:
		logger (Logger):    The logger to use.
	"""
	def __init__(self, logger):
		self._logger = logger

	def checkValidity(self, path, component):
		"""
		Checks the validity of an algebraic loop.

		Args:
			path (str):         The path of the top-level block.
			component (list):   The blocks in the algebraic loop.
		"""
		raise NotImplementedError()

	def constructInput(self, component, curIt):
		"""
		Constructs input for the solver.

		Args:
			component (list):   The blocks in the algebraic loop.
			curIt (int):        The current iteration of the simulation.

		See Also:
			:func:`solve`
		"""
		raise NotImplementedError()

	def solve(self, solverInput):
		"""
		Solves the algebraic loop.

		Args:
			solverInput:    The constructed input.

		See Also:
			:func:`constructInput`
		"""
		raise NotImplementedError()


class LinearSolver(Solver):
	"""
	Solves linear algebraic loops.
	"""
	def checkValidity(self, path, component):
		if not self.__isLinear(component):
			self._logger.fatal("Cannot solve non-linear algebraic loop.\nSelf: {}\nComponents: {}".format(path, component))

	def __isLinear(self, strongComponent):
		"""Determines if an algebraic loop describes a linear equation or not.

        Args:
            strongComponent (list): The detected loop, in a list (of BaseBlock instances)

        Returns:
            :class:`True` if the loop is linear, else :code:`False`.
        """
		# TO IMPLEMENT
		# Look at the lecture video from Recording_5 12/10/2020 at 35:40 for more details on how to check if it's linear

		def isKnownValue(block, strongComponent):
			# We have a strong component, so this will probably result in an infinite loop if there is no known value
			# if isinstance(block, (CBD.lib.std.InverterBlock, ...)):
			# 	for port, inputLink in block._linksIn.items():
			# 		if not isKnownValue(inputLink.block):
			# 			return False
			for block2 in strongComponent:
				if block == block2:
					return False
			return True

		for block in strongComponent:
			if block.getBlockType == "AdderBlock":
				# Can be two variables, no problem here
				continue
			elif block.getBlockType() == "NegatorBlock":
				# No problem here, because negation is just a the constant -1 multiplied with a variable
				continue
			elif block.getBlockType() == "ProductBlock":
				# One can be a constant, the other might be a variable
				found_var = False
				for port in block.getLinksIn():
					if not isKnownValue(block.getLinksIn()[port][0], strongComponent):
						if found_var:
							return False
						found_var = True
			elif block.getBlockType() in ["LessThanBlock", "EqualsBlock", "LessThanOrEqualsBlock", "NotBlock", "OrBlock", "AndBlock"]:
				# Logic operators are never linear
				return False
			elif isKnownValue(block, strongComponent):
				continue
		return True

	def constructInput(self, strongComponent, curIteration):
		"""
		Constructs input for a solver of systems of linear equations
		Input consists of two matrices:

			- M1: coefficient matrix, where each row represents an equation of the system
			- M2: result matrix, where each element is the result for the corresponding equation in M1
		"""
		# Initialize matrices with zeros
		size = len(strongComponent)
		M1 = Matrix(size, size)
		M2 = [0] * size

		# block -> index of block
		indexdict = dict()

		for i, block in enumerate(strongComponent):
			indexdict[block] = i

		# Get low-level dependency
		resolveBlock = lambda possibleDep, output_port: possibleDep if not isinstance(possibleDep, CBD) else possibleDep.getBlockByName(output_port)

		# Get list of low-level dependencies from n inputs
		def getBlockDependencies2(block):
			return (resolveBlock(b, output_port) for (b, output_port) in [block.getBlockConnectedToInput(x) for x in block.getInputPortNames()])

		for i, block in enumerate(strongComponent):
			if block.getBlockType() == "AdderBlock":
				for external in [x for x in getBlockDependencies2(block) if x not in strongComponent]:
					M2[i] -= external.getSignal()[curIteration].value
				M1[i, i] = -1

				for compInStrong in [x for x in getBlockDependencies2(block) if x in strongComponent]:
					M1[i, indexdict[compInStrong]] += 1
			elif block.getBlockType() == "ProductBlock":
				# M2 can stay 0
				M1[i, i] = -1
				fact = reduce(lambda x, y: x * y, [x.getSignal()[curIteration].value for x in getBlockDependencies2(block) if x not in strongComponent])
				for compInStrong in [x for x in getBlockDependencies2(block) if x in strongComponent]:
					M1[i, indexdict[compInStrong]] += fact
			elif block.getBlockType() == "NegatorBlock":
				# M2 can stay 0
				M1[i, i] = -1
				possibleDep, output_port = block.getBlockConnectedToInput("IN1")
				M1[i, indexdict[resolveBlock(possibleDep, output_port)]] = - 1
			elif block.getBlockType() == "InputPortBlock":
				# M2 can stay 0
				M1[i, i] = 1
				possibleDep, output_port = block.parent.getBlockConnectedToInput(block.getBlockName())
				M1[i, indexdict[resolveBlock(possibleDep, output_port)]] = - 1
			elif block.getBlockType() == "OutputPortBlock" or block.getBlockType() == "WireBlock":
				# M2 can stay 0
				M1[i, i] = 1
				dblock = block.getDependencies(0)[0]
				if isinstance(dblock, CBD):
					oport = block.getLinksIn()['IN1'].output_port
					dblock = dblock.getBlockByName(oport).getLinksIn()['IN1'].block
				M1[i, indexdict[dblock]] = - 1
			elif block.getBlockType() == "DelayBlock":
				# If a delay is in a strong component, this is the first iteration
				assert curIteration == 0
				# And so the dependency is the IC
				# M2 can stay 0 because we have an equation of the type -x = -ic <=> -x + ic = 0
				M1[i, i] = -1
				possibleDep, output_port = block.getBlockConnectedToInput("IC")
				dependency = resolveBlock(possibleDep, output_port)
				assert dependency in strongComponent
				M1[i, indexdict[dependency]] = 1
			else:
				self._logger.fatal("Unknown element '{}', please implement".format(block.getBlockType()))
		return M1, M2

	def solve(self, solverInput):
		M1, M2 = solverInput
		n = M1.rows
		indxc = [0] * n
		indxr = [0] * n
		ipiv = [0] * n
		icol = 0
		irow = 0
		for i in range(n):
			big = 0.0
			for j in range(n):
				if ipiv[j] != 1:
					for k in range(n):
						if ipiv[k] == 0:
							nb = math.fabs(M1[j, k])
							if nb >= big:
								big = nb
								irow = j
								icol = k
						elif ipiv[k] > 1:
							raise ValueError("GAUSSJ: Singular Matrix-1")
			ipiv[icol] += 1
			if irow != icol:
				for l in range(n):
					M1[irow, l], M1[icol, l] = M1[icol, l], M1[irow, l]
				M2[irow], M2[icol] = M2[icol], M2[irow]
			indxr[i] = irow
			indxc[i] = icol
			if M1[icol, icol] == 0.0:
				raise ValueError("GAUSSJ: Singular Matrix-2")
			pivinv = 1.0 / M1[icol, icol]
			M1[icol, icol] = 1.0
			for l in range(n):
				M1[icol, l] *= pivinv
			M2[icol] *= pivinv
			for ll in range(n):
				if ll != icol:
					dum = M1[ll, icol]
					M1[ll, icol] = 0.0
					for l in range(n):
						M1[ll, l] -= M1[icol, l] * dum
					M2[ll] -= M2[icol] * dum

		for l in range(n - 1, 0, -1):
			if indxr[l] != indxc[l]:
				for k in range(n):
					M1[k, indxr[l]], M1[k, indxc[l]] = M1[k, indxc[l]], M1[k, indxr[l]]

		return solverInput[1]


class Matrix:
	"""Custom, efficient matrix class. This class is used for efficiency purposes.

		- Using a while/for loop is slow.
		- Using :class:`[[0] * n] * n` will have n references to the same list.
		- Using :class:`[[0] * size for _ in range(size)]` can be 5 times slower
		  than this class!

	Numpy could be used to even further increase efficiency, but this increases the
	required dependencies for external hardware systems (that may not provide these options).

	Note:
		Internally, the matrix is segmented into chunks of 500.000.000 items.
	"""
	def __init__(self, rows, cols):
		self.rows = rows
		self.cols = cols
		self.size = rows * cols
		self.__max_list_size = 500 * 1000 * 1000
		self.data = [[0] * ((rows * cols) % self.__max_list_size)]
		for r in range(self.size // self.__max_list_size):
			self.data.append([0] * self.__max_list_size)

	def __getitem__(self, idx):
		absolute = idx[0] * self.cols + idx[1]
		outer = absolute // self.__max_list_size
		inner = absolute % self.__max_list_size
		return self.data[outer][inner]

	def __setitem__(self, idx, value):
		absolute = idx[0] * self.cols + idx[1]
		outer = absolute // self.__max_list_size
		inner = absolute % self.__max_list_size
		self.data[outer][inner] = value

	def __str__(self):
		res = ""
		for row in range(self.rows):
			if len(res) > 0:
				res += "\n"
			res += "["
			for col in range(self.cols):
				res += "\t%8.4f" % self[row, col]
			res += "\t]"
		return res
