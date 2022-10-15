"""
Set of classes that allow the computation of a new delta.
"""
from copy import deepcopy

class StepSize:
	"""
	Base class for all step size changers.

	Warning:
		This class should not be instantiated by the user.

	Args:
		delta_t (numeric):  The (starting) delta of the simulation.
	"""
	def __init__(self, delta_t):
		self.delta_t = delta_t

	def setDeltaT(self, new_delta_t):
		"""
		Updates the delta.

		Args:
			new_delta_t (numeric):  The new delta.
		"""
		self.delta_t = new_delta_t

	def getNextStepSize(self, sim):
		"""
		Obtains the next step size of the simulation, based on the current state.

		Args:
			sim (CBD.simulator.Simulator):  The simulation to compute the step size of.
		"""
		raise NotImplementedError()


class Fixed(StepSize):
	"""
	A fixed step size. This is the default in a simulation.
	Does **not** change the delta itself. External processes
	may alter the delta without any issues when this class
	is used.

	:Example:
		In the figure below, the data from `this CSV file <./_static/data.csv>`_
		is plotted as a blue line. Additionally, the red circles indicate the points when new data
		is computed.

	.. image:: _figures/stepsize/fixed.png
         :width: 500

	Args:
		delta_t (numeric):  The (starting) delta of the simulation.
	"""
	def getNextStepSize(self, sim):
		return self.delta_t


class Euler2(StepSize):
	"""
	Euler 2-Step algorithm for changing the step size.

	This algorithm looks at the simulation value at :code:`dt` time in the future and computes the
	interpolated value between this point and the current point at time :code:`dt / 2`. This
	interpolated value is now compared against the simulation result at time :code:`dt / 2`. Whenever
	the absolute error exceeds :code:`epsilon`, the step size is reduced. Otherwise, a new interpolated
	simulation value of :code:`dt * 2` is compared as before. When this second error is too large,
	:code:`dt` is the best delta for the current step. If not, :code:`dt` is increased.

	Whenever :code:`dt` is increased/decreased, the :func:`getNextStepSize` is called recursively to
	find the best :code:`dt` as fast as possible. Increasing happens by doubling :code:`dt`, whereas
	decreasing happens using the following formula:

	.. math::
		\delta t_{new} = \delta t_{old}\cdot\dfrac{0.9\cdot\epsilon}{error}

	Note:
		When there are multiple simulation outputs, the most pessimistic one (the highest error) will be
		used as a point of reference.

	:Example:
		In the figure below, the data from `this CSV file <./_static/data.csv>`_
		is plotted as a blue line. Additionally, the red circles indicate the points when new data
		is computed.

	.. image:: _figures/stepsize/euler2.png
         :width: 500

	Args:
		delta_t (numeric):  The initial delta (:code:`dt`).
		epsilon (numeric):  The maximal acceptable absolute error

	See Also:
		`Professor Joel Feldman's notes on variable step size algorithms. <http://www.math.ubc.ca/~feldman/math/vble.pdf>`_
	"""
	def __init__(self, delta_t, epsilon):
		StepSize.__init__(self, delta_t)
		self.epsilon = epsilon

	def getNextStepSize(self, sim):
		sim.setStepSize(Fixed(self.delta_t))
		sim._update_clock()
		sim._do_single_step()
		A1 = deepcopy(sim.model.getSignals())

		sim._step_back()

		sim.setDeltaT(self.delta_t / 2)
		sim._update_clock()
		sim._do_single_step()
		A2 = deepcopy(sim.model.getSignals())

		sim._step_back()
		sim.setStepSize(self)
		sim.setDeltaT(self.delta_t)

		r_max = float('-inf')
		for port in A1.keys():
			r_max = max(r_max, abs(self.inp(A1, port) - A2[port][-1].value))
		if r_max > self.epsilon:
			self.delta_t *= .9 * self.epsilon / r_max
			return self.getNextStepSize(sim)

		# No error => can we go larger?
		sim.setStepSize(Fixed(self.delta_t * 2))
		sim._update_clock()
		sim._do_single_step()
		A3 = deepcopy(sim.model.getSignals())

		sim._step_back()
		sim.setStepSize(self)
		sim.setDeltaT(self.delta_t)

		r_max = float('-inf')
		for port in A1.keys():
			r_max = max(r_max, abs(self.inp(A3, port) - A1[port][-1].value))
		if r_max > self.epsilon:
			return self.delta_t
		self.delta_t *= 2
		return self.getNextStepSize(sim)

	@staticmethod
	def inp(A1, port):
		"""
		Find the midpoint-interpolation value of two sequential values.

		Args:
			A1 (dict):  Signal dictionary to look at.
			port (str): Name of the port to compare.
		"""
		return A1[port][-2].value - (A1[port][-2].value - A1[port][-1].value) / 2

from CBD.lib.io import Interpolation
class Euler2Alt(StepSize):
	def __init__(self, delta_t, epsilon):
		StepSize.__init__(self, delta_t)
		self.epsilon = epsilon
		self.t = []

	def getNextStepSize(self, sim):
		S = deepcopy(sim.model.getSignals())
		self.t.append(sim.getTime())
		h = self.delta_t
		A1 = {}
		A2 = {}
		for p in S.keys():
			y = S[p]
			yk = y[-1]
			tk = self.t[-1]

			A1[p] = yk + h * self.f(y, tk)
			A2[p] = yk + h/2 * self.f(y, tk) + h/2 * self.f(y, tk + h/2)


	def f(self, y, t):
		if t > self.t[-1]:
			return y[-1]
		xx = 0
		for x in self.t:
			if x > t:
				break
			xx += 1
		return Interpolation.interpolate((self.t[xx], y[xx]), (self.t[xx+1], y[xx+1]), t, Interpolation.LINEAR)


class RKF45(StepSize): pass


class ButcherTableau:
	r"""
	Mnemonic device to store the Runge-Kutta matrix, weights and nodes in
	the computation of generic RK methods. The extended tableau also allows
	for the error computation for adaptive step sizes. The general form of
	a Butcher Tableau is shown below, where:

	* :math:`s` identifies the number of stages;
	* :math:`a_{ij}, 1 \leq j < i \leq s` represents a coefficient in the
	  Runge-Kutta matrix;
	* :math:`b_i` and :math:`b^*_i` correspond to the weights of a higher
	  and a lower order method, respectively; and
	* :math:`c_i` specifies the nodes.

	.. math::

		\begin{array}
			{c|ccccc}
			0\\
			c_2 & a_{2,1}\\
			c_3 & a_{3,1} & a_{3,2} \\
			\vdots & \vdots & & \ddots\\
			c_s & a_{s,1} & a_{s,2} & \cdots & a_{s,s-1}\\
			\hline
			& b_1 & b_2 & \cdots & b_{s-1} & b_s\\
			& b^*_1 & b^*_2 & \cdots & b^*_{s-1} & b^*_s\\
		\end{array}

	Args:
		rows (iter):    Sequence of tuples :math:`(c_i, [a_{i, j}\vert 1 \leq j < i])`.
						When :code:`None`, nothing will be added.
		weights (iter): Sequence of sequences of weights :math:`[b_{i}\vert i \leq s]`.
						When :code:`None`, no weights will be added.

	Note:
		Upon instantiation, the first (empty) row will be added automatically with a
		node of 0.
	"""
	def __init__(self, rows=None, weights=None):
		self._matrix = []
		self._weights = []
		self._nodes = [0]

		if rows is not None:
			for node, mtx in rows:
				self.addRow(node, mtx)
			if weights is not None:
				for w in weights:
					self.addWeights(w)

	def addRow(self, node, elems):
		r"""
		Adds a :math:`c_i` and :math:`a_{i, j}` to the tableau.

		Args:
			node (numeric): The :math:`c_i`-value.
			elems (iter):   :math:`a_{i, j}`, :math:`\forall j < i`; i.e. the
							sequence of matrix elements that correspond to the node.
		"""
		if len(self._nodes) != len(elems):
			raise ValueError("Inconsistent matrix! Expected row with %d elements!" % len(self._nodes))
		self._nodes.append(node)
		self._matrix.append(elems)

	def addWeights(self, *weights):
		"""
		Adds a row of weights to the bottom of the matrix.

		Args:
			*weights:   A sequence of the weights. I.e. :math:`b_{i}`, where :math:`1 \leq i \leq s`.
		"""
		if len(self._matrix) == 0 or (len(self._matrix[-1]) + 1) != len(weights):
			raise ValueError("Trying to set weights on incomplete matrix")
		if len(self._weights) == 2:
			raise ValueError("Maximal amount of weight rows (2) reached")
		if abs(sum(weights) - 1) > 1e-6:
			raise ValueError("Inconsistent Butcher Tableau for Runge-Kutta approximation. "
			                 "The sum of the weights must equal 1.")
		self._weights.append(weights)

	def getNodes(self):
		"""
		Obtains the nodes, i.e. the :math:`c_i`-values.
		"""
		return self._nodes

	def getWeights(self):
		"""
		Obtains the weight lists, i.e. the :math:`b_i` and :math:`b^*_i`-values.
		"""
		return self._weights

	def getA(self, i, j):
		"""
		Obtains an element from the Runge-Kutta matrix.

		Args:
			i (int):    The row (1-indexed).
			j (int):    The column (1-indexed).
		"""
		return self._matrix[i - 1][j - 1]

	def getOrder(self, wix=-1):
		"""
		Computes the order of the Tableau.
		The order is the amount of non-zero weights.

		Args:
			wix (id):   The weight index. Defaults to :code:`-1` (i.e.
						the last weight row of the tableau).
		"""
		return int(round(sum([1 for i in self._weights[wix] if abs(i) < 1e-16])))

	@staticmethod
	def Heun():
		r"""
		Creates and returns the Butcher Tableau for Heun's method.
		The Tableau is as follows:

		.. math::

			\begin{array}
				{c|cc}
				0\\
				1 & 1\\
				\hline
				& 1/2 & 1/2
			\end{array}
		"""
		tab = ButcherTableau()
		tab.addRow(1, [1])
		tab.addWeights(1/2, 1/2)
		return tab

	@staticmethod
	def HeunEuler():
		r"""
		Creates and returns the extended Butcher Tableau for Heun's method,
		combined with the Euler method.
		The Tableau is as follows:

		.. math::

			\begin{array}
				{c|cc}
				0\\
				1 & 1\\
				\hline
				& 1/2 & 1/2\\
				& 1 & 0
			\end{array}
		"""
		tab = ButcherTableau.Heun()
		tab.addWeights(1, 0)
		return tab

	@staticmethod
	def Ralston():
		r"""
		Creates and returns the Butcher Tableau for Ralston's method for 2nd order
		accuracy. The Tableau is as follows:

		.. math::

			\begin{array}
				{c|cc}
				0\\
				2/3 & 2/3\\
				\hline
				& 1/4 & 3/4
			\end{array}
		"""
		tab = ButcherTableau()
		tab.addRow(2/3, [2/3])
		tab.addWeights(1/4, 3/4)
		return tab

	@staticmethod
	def RalstonEuler():
		r"""
		Creates and returns the extended Butcher Tableau for Ralston's method,
		combined with the Euler method.
		The Tableau is as follows:

		.. math::

			\begin{array}
				{c|cc}
				0\\
				2/3 & 2/3\\
				\hline
				& 1/4 & 3/4\\
				& 1 & 0
			\end{array}
		"""
		tab = ButcherTableau.Ralston()
		tab.addWeights(1, 0)
		return tab

	@staticmethod
	def Midpoint():
		r"""
		Creates and returns the Butcher Tableau for the midpoint method.
		The Tableau is as follows:

		.. math::

			\begin{array}
				{c|cc}
				0\\
				1/2 & 1/2\\
				\hline
				&   0 &   1
			\end{array}
		"""
		tab = ButcherTableau()
		tab.addRow(1/2, [1/2])
		tab.addWeights(0, 1)
		return tab

	@staticmethod
	def MidpointEuler():
		r"""
		Creates and returns the extended Butcher Tableau for the midpoint method,
		combined with the Euler method.
		The Tableau is as follows:

		.. math::

			\begin{array}
				{c|cc}
				0\\
				1/2 & 1/2\\
				\hline
				& 0 & 1\\
				& 1 & 0
			\end{array}
		"""
		tab = ButcherTableau.Midpoint()
		tab.addWeights(1, 0)
		return tab

	@staticmethod
	def RK4():
		r"""
		Creates and returns the Butcher Tableau for the default RK
		algorithm.
		The Tableau is as follows:

		.. math::

			\begin{array}
				{c|cc}
				0\\
				1/2 & 1/2\\
				1/2 &   0 & 1/2\\
				1   &   0 &   0 &   1\\
				\hline
				    & 1/6 & 1/3 & 1/3 & 1/6
			\end{array}
		"""
		tab = ButcherTableau()
		tab.addRow(1/2, [1/2])
		tab.addRow(1/2, [1/2, 1/2])
		tab.addRow(  1, [  0,   0, 1])
		tab.addWeights(1/6, 1/3, 1/3, 1/6)
		return tab

	@staticmethod
	def RK4Alt():
		r"""
		Creates and returns the Butcher Tableau for an alternative RK
		algorithm. It is also called the 3/8-rule.
		The Tableau is as follows:

		.. math::

			\begin{array}
				{c|cc}
				0\\
				1/3 &  1/3\\
				2/3 & -1/3 &   1\\
				1   &    1 &  -1 &   1\\
				\hline
				    & 1/8 & 3/8 & 3/8 & 1/8
			\end{array}
		"""
		tab = ButcherTableau()
		tab.addRow(1/3, [ 1/3])
		tab.addRow(2/3, [-1/3, 1])
		tab.addRow(  1, [   1, -1, 1])
		tab.addWeights(1/8, 3/8, 3/8, 1/8)
		return tab

	@staticmethod
	def RKF45():
		r"""
		Creates and returns the extended Butcher Tableau for the
		Runge-Kutta-Fehlberg algorithm of 4th and 5th order.
		The Tableau is as follows:

		.. math::

			\begin{array}
				{c|cc}
				    0\\
				  1/4 &       1/4\\
				  3/8 &      3/32 &       9/32\\
				12/13 & 1932/2197 & -7200/2197 &  7296/2197\\
				    1 &   439/216 &         -8 &   3680/513 &   -845/4104\\
				  1/2 &     -8/27 &          2 & -3544/2565 &   1859/4104 & -11/40\\
				\hline
				      &    16/135 &          0 & 6656/12825 & 28561/56430 &  -9/50 & 2/55\\
				      &    25/216 &          0 &  1408/2565 &   2197/4104 &   -1/5 &    0
			\end{array}
		"""
		tab = ButcherTableau()
		tab.addRow(  1/4, [      1/4])
		tab.addRow(  3/8, [     3/32,       9/32])
		tab.addRow(12/13, [1932/2197, -7200/2197,  7296/2197])
		tab.addRow(    1, [  439/216,         -8,   3680/513,   -845/4104])
		tab.addRow(  1/2, [    -8/27,          2, -3544/2565,   1859/4104, -11/40])
		tab.addWeights(       16/135,          0, 6656/12825, 28561/56430,  -9/50, 2/55)
		tab.addWeights(       25/216,          0,  1408/2565,   2197/4104,   -1/5,    0)
		return tab

	@staticmethod
	def DOPRI():
		r"""
		Creates and returns the extended Butcher Tableau for the
		`Dormand-Prince method <https://www.sciencedirect.com/science/article/pii/0771050X80900133?via%3Dihub>`_.
		This is the default method in the :code:`ode45` solver for MATLAB and GNU Octave, among others.
		The Tableau is as follows:

		.. math::

			\begin{array}
				{c|cc}
				   0\\
				 1/5 &         1/5\\
				3/10 &        3/40 &        9/40\\
				 4/5 &       44/45 &      -56/15 &       32/9\\
				 8/9 &  19372/6561 & -25360/2187 & 64448/6561 & -212/729\\
				   1 &   9017/3168 &     -355/33 & 46732/5247 &   49/176 &   -5103/18656\\
				   1 &      35/384 &           0 &   500/1113 &  125/192 &    -2187/6784 &    11/84\\
				\hline
				      &     35/384 &           0 &   500/1113 &  125/192 &    -2187/6784 &    11/84 &    0\\
				      & 5179/57600 &           0 & 7571/16695 &  393/640 & -92097/339200 & 187/2100 & 1/40
			\end{array}
		"""
		tab = ButcherTableau()
		tab.addRow( 1/5, [        1/5])
		tab.addRow(3/10, [       3/40,        9/40])
		tab.addRow( 4/5, [      44/45,      -56/15,       32/9])
		tab.addRow( 8/9, [ 19372/6561, -25360/2187, 64448/6561, -212/729])
		tab.addRow(   1, [  9017/3168,     -355/33, 46732/5247,   49/176,   -5103/18656])
		tab.addRow(   1, [     35/384,           0,   500/1113,  125/192,    -2187/6784,    11/84])
		tab.addWeights(        35/384,           0,   500/1113,  125/192,    -2187/6784,    11/84,    0)
		tab.addWeights(    5179/57600,           0, 7571/16695,  393/640, -92097/339200, 187/2100, 1/40)
		return tab

	RKDP = DOPRI
	"Alias of :func:`DOPRI`."

	DormandPrince = DOPRI
	"Alias of :func:`DOPRI`."

	@staticmethod
	def RKCK():
		r"""
		Creates and returns the extended Butcher Tableau for the
		`Cash-Karp method <https://dl.acm.org/doi/10.1145/79505.79507>`_ for 4th and 5th order
		accurate solutions.
		The Tableau is as follows:

		.. math::

			\begin{array}
				{c|cc}
				   0\\
				 1/5 &         1/5\\
				3/10 &        3/40 &    9/40\\
				 3/5 &        3/10 &   -9/10 &         6/5\\
				   1 &      -11/54 &     5/2 &      -70/27 &        35/27\\
				 7/8 &  1631/55296 & 175/512 &   575/13824 & 44275/110592 &  253/4096\\
				\hline
				      &     37/378 &       0 &     250/621 &      125/594 &         0 & 512/1771\\
				      & 2825/27648 &       0 & 18575/48384 &  13525/55296 & 277/14336 &      1/4
			\end{array}
		"""
		tab = ButcherTableau()
		tab.addRow( 1/5, [       1/5])
		tab.addRow(3/10, [       3/40,    9/40])
		tab.addRow( 3/5, [       3/10,   -9/10,         6/5])
		tab.addRow(   1, [     -11/54,     5/2,      -70/27,        35/27])
		tab.addRow( 7/8, [ 1631/55296, 175/512,   575/13824, 44275/110592,  253/4096])
		tab.addWeights(        37/378,       0,     250/621,      125/594,         0, 512/1771)
		tab.addWeights(    2825/27648,       0, 18575/48384,  13525/55296, 277/14336,      1/4)
		return tab

	CashKarp = RKCK
	"Alias of :func:`RKCK`."

	@staticmethod
	def BogackiShampine():
		r"""
		Creates and returns the extended Butcher Tableau for the
		`Bogacki-Shampine method <https://doi.org/10.1016%2F0893-9659%2889%2990079-7>`_ for 3th order
		accurate solutions.

		It is implemented in the :code:`ode23` function in MATLAB.

		The Tableau is as follows:

		.. math::

			\begin{array}
				{c|cc}
				  0\\
				1/2 &  1/2\\
				3/4 &    0 & 3/4\\
				  1 &  2/9 & 1/3 & 4/9\\
				\hline
				    &  2/9 & 1/3 & 4/9 &   0\\
					& 7/24 & 1/4 & 1/3 & 1/8
			\end{array}
		"""
		tab = ButcherTableau()
		tab.addRow(1/2, [ 1/2])
		tab.addRow(3/4, [   0, 3/4])
		tab.addRow(  1, [ 2/9, 1/3, 4/9])
		tab.addWeights(   2/9, 1/3, 4/9,   0)
		tab.addWeights(  7/24, 1/4, 1/3, 1/8)
		return tab


class RungeKutta(StepSize):
	r"""
	Applies the Runge-Kutta algorithm on a specific :class:`ButcherTableau`.

	Internally, a set of :math:`k_i` values will be computed, based on the
	tableau. From there, an error :math:`e` can be obtained. If this error
	exceeds :attr:`epsilon`, :math:`\delta t` is increased. The formulas
	are as follows:

	.. math::
		\begin{align}
			k_i &= f\left(t_n + h\cdot c_i, y_n + h\sum_{j=1}^{s-1}\left(a_{i,j}\cdot k_j\right)\right)\\
			e &= h\sum_{i=1}^s \left(b_i - b^*_i\right) k_i\\
			\delta t_{new} &= \delta t_{old}\cdot\dfrac{0.9\cdot\epsilon}{e}
		\end{align}

	Args:
		delta_t (numeric):          Initial delta.
		tableau (ButcherTableau):   The tableau to use.
		tol1 (numeric):             Smallest allowed error value when decreasing delta.
		tol2 (numeric):             Largest allowed error value when increasing delta.
		min_change (numeric):       Minimal change for the delta to experience.
		max_change (numeric):       Maximal change for the delta to experience.

	Note:
		If there are multiple outputs in a model, the most pessimistic view
		will be used, i.e. the largest error.

	See Also:
		https://en.wikipedia.org/wiki/Runge%E2%80%93Kutta_methods
	"""
	def __init__(self, delta_t, tableau, tol1, tol2, min_change=0.3, max_change=2):
		StepSize.__init__(self, delta_t)
		self._tableau = tableau
		self._tol1 = tol1
		self._tol2 = tol2
		self._change = min_change, max_change
		self._prev = None

	def getNextStepSize(self, sim):
		A1 = sim.model.getSignals()

		K = []
		for n in self._tableau.getNodes():
			K.append(self.derivative(sim, n * self.delta_t))

		E = {}
		b, b_ = self._tableau.getWeights()
		s = len(b)
		for k in A1.keys():
			e = 0
			for i in range(s):
				e += K[i][k] * (b[i] - b_[i])
			E[k] = abs(e)
		TE = max(E.values())

		# TODO: going larger => HOW?
		# TODO: update formulas in docs
		if TE > self._tol1:
			self.delta_t *= 0.9 * min(max((self._tol1 / TE) ** (1 / (s - 1)), self._change[0]), self._change[1])
			# self.delta_t *= 0.9 * ((self._epsilon / TE) ** (1/(s-1)))
			if self._prev is None or abs(self._prev - self.delta_t) > 1e-6:
				self._prev = self.delta_t
				return self.getNextStepSize(sim)
		if TE < self._tol2:
			self.delta_t /= 0.9 * min(max((TE / self._tol2) ** (1 / (s - 1)), self._change[0]), self._change[1])
			# self.delta_t = self.delta_t * 2 + self._tol2
			return self.getNextStepSize(sim)

		self._prev = None
		return self.delta_t

	def derivative(self, sim, delta):
		"""
		Computes the derivative; i.e. the :math:`f(t, y)`-function, which is the derivative definition
		for an initial-value problem. The derivative is computed as a backwards euler difference
		between :math:`t+\delta` and :math:`t`.

		Args:
			sim (CBD.simulator.Simulator):  The simulation to compute the step size of.
			delta (numeric):                The :math:`\delta` value of the next point.

		Note:
			Given that a CBD model represents the integrated version of the :math:`f(t, y)`-function,
			the :math:`y` parameter will be assumed to be set implicitly. It is henceforth ignored.
		"""
		A1 = _copy_state(sim.model.getSignals())

		sim.setStepSize(Fixed(delta))
		sim._update_clock()
		sim._do_single_step()
		A2 = _copy_state(sim.model.getSignals())

		sim._step_back()

		sim.setStepSize(self)

		res = {}
		for key in A2.keys():
			if delta <= 1e-6:
				res[key] = 0
			else:
				res[key] = (A2[key][-1].value - A1[key][-1].value)

		return res


def _copy_state(D):
	"""
	Helper function that is an efficient version of deepcopy,
	by only getting the required data. The data is a dictionary
	of :code:`id -> list`, where the two last items of the list
	are of importance.

	Args:
		D (dict):   A dictionary of lists.
	"""
	return {k: v[-2:] for k, v in D.items()}

from .simulator import Simulator
