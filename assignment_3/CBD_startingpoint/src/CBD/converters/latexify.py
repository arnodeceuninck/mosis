"""
A module that allows the construction of LaTeX-equations from a CBD model,
as a whole (one equation per block and per connection) or as a simplified
version (by means of substitution).
"""

from copy import deepcopy

class CBD2Latex:
	"""
	Creates a corresponding set of LaTeX-equations for a CBD model.

	Args:
		model (CBD.Core.CBD):    The model to create the equations for.

	Keyword Arguments:
		show_steps (bool):      When :code:`True`, all intermediary steps will
								be shown. Defaults to :code:`False`.
		ignore_path (bool):     When :code:`True`, the name of the original model
								will be removed from all path names. This name is
								a common prefix over the system.
								Defaults to :code:`True`.
		escape_nonlatex (bool): When :code:`True`, non-latex characters are escaped
								from the rendered result. Defaults to :code:`True`.
		time_variable (str):    The name for the variable that represents the time
								(i.e., the current iteration). Defaults to :code:`'i'`.
		render_latex (bool):    When :code:`True`, the :func:`render` method will
								output a latex-formatted string. Otherwise, simple
								text formatting is done. Defaults to :code:`True`.
		time_format (str):      How the time must be formatted when rendered. By default,
								it will be placed in parentheses at the end. Use
								:code:`{time}` to identify the time constant.
		delta_t (str):          Representation of the used delta in the render. This will
								be appended to values that have been computed for a delay
								block. This is only to be used when the time does not
								identify the iteration, but the actual simulation time.
								Defaults to the empty string.
		replace_par (bool):     When :code:`True`, the parentheses will be replaced by the
								much cleaner :code:`\\left(` and :code:`\\right)`, if rendered
								in LaTeX-format. Defaults to :code:`True`.
		type_formats (dict):    A dictionary of :code:`{ operationType -> callable }` that
								allows for the remapping of mathematical descriptions based,
								where :code:`operationType` identifies the operation to remap
								and :code:`callable` a function that takes the name/symbol and
								the arguments as input and produces a string representation.
		path_sep (str):         The separator to use for the paths. Defaults to :code:`"."`.
		merge_sums (bool):      Whether or not multiple additions of the same sub-equation should
								be merged into a product. Defaults to :code:`True`.
		merge_prods (bool):     Whether or not multiple products of the same sub-equation should
								be merged into a power. Defaults to :code:`True`.
		merge_negs (bool):      Whether or not all negations in a product should be merged into a
								single negation. Defaults to :code:`True`.
	"""

	DEFAULT_CONFIG = {
		"show_steps": False,
		"ignore_path": True,
		"escape_nonlatex": True,
		"time_variable": 'i',
		"render_latex": True,
		"time_format": "({time})",
		"delta_t": "",
		"replace_par": True,
		"type_formats": {},
		"path_sep": '.',

		# Fnc settings
		"merge_sums": True,
		"merge_prods": True,
		"merge_negs": True
	}
	"""Default configuration setup."""

	def __init__(self, model, **kwargs):
		self.model = model
		self.config = self.DEFAULT_CONFIG

		for k in kwargs:
			if k in self.config:
				self.config[k] = kwargs[k]

		self.equations = {}
		self.outputs = [self._rename(self.model.getPath(self.config['path_sep']) + self.config['path_sep'] + x) for x in self.model.getSignals().keys()]
		self._collect_equations()
		self._step = 0

	def _rename(self, name):
		return CBD2Latex.rename(name, self.config, self.model)

	@staticmethod
	def rename(name, config, model):
		"""Makes the name of a path accurate.

		Args:
			name (str):     The name to convert.
			config (dict):  Configuration dictionary (see above).
			model (CBD):    The parent CBD model.
		"""
		if config["ignore_path"]:
			mname = model.getPath(config['path_sep']) + config['path_sep']
			if name.startswith(mname):
				name = name[len(mname):]
		if config["escape_nonlatex"]:
			name = name.replace("_", r"\_")
		return name

	@staticmethod
	def get_block_data(block, model, conf=None):
		config = CBD2Latex.DEFAULT_CONFIG
		if conf is not None:
			for k, v in conf.items():
				config[k] = v

		TF = config["type_formats"]
		func = _BLOCK_MAP.get(block.getBlockType(), None)
		if func is None:
			func = block.getBlockType()
			if func in ["OutputPortBlock", "InputPortBlock", "WireBlock"]:
				return None
		if isinstance(func, str):
			func = lambda b, p, f=func: (p("OUT1"), Fnc(f, [CBD2Latex.rename(p("%s") % x, config, model) for x in block.getInputPortNames()]))
		res = func(block, lambda x: CBD2Latex.rename(block.getPath(config['path_sep']) + config['path_sep'] + x, config, model))
		if isinstance(res, tuple):
			f = res[1]
			if isinstance(f, Fnc):
				f.fmt = TF
			elif isinstance(f, str):
				f = f.format(time=config['time_variable'])
			return res[0], f
		elif isinstance(res, list):
			for r in res:
				f = r[1]
				if isinstance(f, Fnc):
					f.fmt = TF
				return res[0], f

	def _collect_equations(self):
		"""
		Loads the equations from the model in.

		See Also:
			`Cláudio Gomes, Joachim Denil and Hans Vangheluwe. 2016. "Causal-Block Diagrams",
			Technical Report <https://repository.uantwerpen.be/docman/irua/d28eb1/151279.pdf>`_
		"""
		# Add all blocks
		for block in self.model.getBlocks():
			f = self.get_block_data(block, self.model, self.config)
			if f is not None:
				self.equations[f[0]] = f[1]

		# Add all connections
		for block in self.model.getBlocks():
			tp = block.getBlockType()
			path = block.getPath(self.config['path_sep'])
			for k, v in block.getLinksIn().items():
				if tp == "OutputPortBlock":
					self.equations[self._rename(path)] = [self._rename(v.block.getPath(self.config['path_sep']) + self.config['path_sep'] + v.output_port)]
				else:
					self.equations[self._rename(path + self.config['path_sep'] + k)] = self._rename(v.block.getPath(self.config['path_sep']) + self.config['path_sep'] + v.output_port)

	def render(self, rl=True):
		"""
		Creates the LaTeX string for the model, based on the current level of simplifications.

		Args:
			rl (bool):      Identifies if the rendering must result in a LaTeX-renderable string.
							This argument basically overwrites the :attr:`render_latex` config
							attribute. When :code:`None`, the value from the config is used.
							Defaults to :code:`True`.
		"""
		latex = ""
		if rl is None:
			rl = self.config["render_latex"]

		fmt = self.config["time_format"]
		TF = self.config["type_formats"]
		dt = self.config["delta_t"]
		tvar = self.config["time_variable"]
		rpar = self.config["replace_par"]

		def apply_eq(var, val, ltx):
			"""
			Applies a dictionary of equations.

			Args:
				var:    Lefthand-side of the equation.
				val:    Righthand-side of the equation, i.e. the function.
				ltx:    Latex-string to format var and val in.
			"""
			if isinstance(val, Fnc):
				val = deepcopy(val)
				val.apply_time(t=tvar, fmt=fmt, dt=dt)
				val = val.latex(rl, tvar)
				if len(val) > 2:
					while val[0] == "(" and val[-1] == ")":
						val = val[1:-1]
				if rl and rpar:
					val = val.replace("(", "\\left(").replace(")", "\\right)")
			return ltx.format(v=var, val=val, time=tvar)

		for variable, value in self.equations.items():
			x = "\t{v}%s = {val}\n" % fmt
			if rl:
				x = "\t" + (r"{v}%s &=& {val}\\" % fmt) + "\n"
			if not isinstance(value, list):
				value = [value]
			latex += apply_eq(variable, Fnc('+', value, TF), x)

		ic = self.create_ic()
		for variable, value in ic.items():
			x = "\t{v} = {val}\n"
			if rl:
				x = "\t" + r"{v} &=& {val}\\" + "\n"
			latex += apply_eq(variable, value, x)

		if rl:
			return "\\left\\{\\begin{array}{lcl}\n%s\\end{array}\\right." % latex
		return latex

	def eq(self):
		"""
		Obtains the current set of equations in a format that can be parsed by
		the :mod:`CBD.converters.eq2CBD` converter.
		This allows model simplifications and optimizations.
		"""
		res = ""
		for k, v in self.equations.items():
			res += "{} = {}\n".format(k, str(v))
		return res

	def create_ic(self):
		"""
		Creates the equations for the initial conditions of a system.
		"""
		# Maximal depth is the amount of nested delay blocks
		stop = [0]
		for e in self.equations.values():
			if isinstance(e, Fnc):
				stop.append(e.get_delay_depth())
		stop = max(stop)

		created = {}
		for i in range(stop):
			eqs = deepcopy(self.equations)
			for k, e in eqs.items():
				if isinstance(e, Fnc) and e.name in _MEMORY:
					eqs[k] = Fnc('+', [e])
					eqs[k].apply_time(t=i, fmt=self.config["time_format"], dt=self.config["delta_t"])
					eqs[k].apply_delay(i)
					for c, v in created.items():
						eqs[k].apply(c, v)

					old = None
					while old != eqs[k]:
						old = eqs[k]
						if isinstance(eqs[k], Fnc):
							eqs[k] = eqs[k].simplify(self.config["merge_sums"], self.config["merge_prods"], self.config["merge_negs"])
					created["%s%s" % (k, self.config["time_format"].format(time=i))] = eqs[k]
		return created

	def simplify_links(self):
		"""
		First step to execute is a link simplification. Generally, there are more links
		than blocks, so this function will take care of the largest simplification.
		"""
		links = set()
		numeric = set()
		for k, v in self.equations.items():
			if isinstance(v, str):
				links.add(k)
			elif isinstance(v, (int, float)):
				numeric.add(k)
		for k, v in self.equations.items():
			if isinstance(v, Fnc):
				for link in links:
					v.apply(link, self.equations[link])
				for num in numeric:
					v.apply(num, self.equations[num])
		for link in links | numeric:
			del self.equations[link]

	def substitute(self):
		"""
		Combines multiple equations into one, based on the requested output, by
		means of substitution. This function will be called multiple times: once
		for each "step" in the simplification.

		See Also:
			:func:`simplify`
		"""
		outputs = self.outputs
		to_delete = set()
		for output in outputs:
			if output not in self.equations: continue
			v = self.equations[output]
			if isinstance(v, list):
				v = v[0]
				self.equations[output] = self.equations[v]
				to_delete.add(v)
			elif isinstance(v, Fnc):
				for k, e in self.equations.items():
					if k not in outputs:
						v.apply(k, e)
						to_delete.add(k)
			for f in self.equations.values():
				if isinstance(f, Fnc):
					if v not in outputs:
						f.apply(v, output)
			deps = self.get_dependencies_for(output)
			for dep in deps:
				if dep in to_delete:
					to_delete.remove(dep)
		for k, f in self.equations.items():
			if isinstance(f, Fnc):
				self.equations[k] = f.simplify(self.config["merge_sums"], self.config["merge_prods"], self.config["merge_negs"])
		for td in to_delete:
			del self.equations[td]

	def get_dependencies_for(self, variable, visited=tuple()):
		"""
		Tries to obtain all dependencies of a specific variable, to prevent
		accidental removal. This will be done via a depth-first search.

		Args:
			variable (str): The variable to get the dependencies for.
			visited (iter): A collection of all variables that have been
							checked.
		"""
		value = self.equations.get(variable, None)
		if isinstance(value, Fnc):
			deps = value.dependencies()
		else:
			deps = []
		i = 0
		vis = list(visited)
		while i < len(deps):
			if deps[i] not in visited:
				vis.append(deps[i])
				n_deps = self.get_dependencies_for(deps[i], vis)
				for dep in n_deps:
					if dep not in deps:
						deps.append(dep)
			i += 1
		return deps

	def simplify(self, steps=-1):
		"""
		Simplifies the system of equations to become a more optimal solution.

		Args:
			steps (int):        When positive, this indicates the amount of steps
								that must be taken. When negative, the equations
								will be simplified until a convergence (i.e. no
								possible changes) is reached. Defaults to -1.

		See Also:
			- :func:`simplify_links`
			- :func:`substitute`
		"""
		if self.config["show_steps"]:
			self._trace("INITIAL SYSTEM")
		self.simplify_links()
		txt = " substituted all connections and constant values"
		peq = None
		i = 0
		while peq != self.equations:
			if 0 <= steps <= i: break
			peq = self.equations.copy()
			if self.config["show_steps"]:
				self._trace(txt)
			self.substitute()
			i += 1
			txt = ""

	def _trace(self, text=""):
		"""Traces a step in the solution.

		Args:
			text (str): Additional text to print.
		"""
		if self._step == 0:
			print("" + text + ":")
		else:
			print("STEP %d:" % self._step, text)
		print(self.render(None))
		self._step += 1

class Fnc:
	"""
	An identifier of a function within the context of the equation system.
	This class is a helper class to be used by the :class:`CBD2Latex` class.

	Args:
		name (str):     The name of the function.
		args (list):    The ordered list of arguments to be applied by the
						function.
		fmt:            A function that takes a name/symbol and a set of
						arguments, allowing it to return a custom string
						representation for the given function. When
						:code:`None`, the default representation will be
						used.
	"""
	def __init__(self, name, args, fmt=None):
		self.name = name
		self.args = list(args)
		self.fmt = {} if fmt is None else fmt

	def __repr__(self):
		return "%s%s" % (self.name, self.args)

	def __str__(self):
		f = self.fmt.get(self.name, None)
		if f is not None:
			return f(self.name, self.args)
		if self.name in ['+', '*', '^', '%', '<', '<=', '==', 'or', 'and']:
			return " {} ".format(self.name).join(["({})".format(str(x)) for x in self.args])
		elif self.name in ['-', '!']:
			return "({}({}))".format(self.name, str(self.args[0]))
		elif self.name == '~':
			return "(1/({}))".format(str(self.args[0]))
		else:
			return "{}({})".format(self.name, ", ".join([str(x) for x in self.args]))

	def __hash__(self):
		return hash((self.name, tuple(self.args)))

	def __eq__(self, other):
		return isinstance(other, Fnc) and self.name == other.name and self.args == other.args

	def apply(self, name, value):
		"""
		Recursively replaces all references of a variable by its value.

		Args:
			name (str): The variable to replace.
			value:      The value to replace the variable by.
		"""
		for i, elem in enumerate(self.args):
			if isinstance(elem, str):
				if elem == name:
					self.args[i] = value
			elif isinstance(elem, Fnc):
				elem.apply(name, value)

	def apply_delay(self, time=-1):
		"""
		Applies a delay to the function and all its children.
		Can be used to remove delays from the system.

		Calling :func:`apply_time` followed by :func:`apply_delay`
		with the same time solves the system for that time.

		Args:
			time (int): The time whence to apply the delay.
		"""
		if self.name in _MEMORY:
			if time == 0:
				return self.args[1]
			elif time > 0:
				if isinstance(self.args[0], Fnc):
					return self.args[0].apply_delay(time - 1)
				return self.args[0]
		else:
			for i, a in enumerate(self.args):
				if isinstance(a, Fnc):
					self.args[i] = a.apply_delay(time)
			return self

	def simplify(self, merge_sums, merge_prods, merge_negs):
		"""
		Simplifies the function w.r.t. its meaning.

		Args:
			merge_sums (bool):  Whether or not multiple additions of the same
								sub-equation should be merged into a product.
			merge_prods (bool): Whether or not multiple products of the same
								sub-equation should be merged into a power.
			merge_negs (bool):  Whether or not all negations in a product should
								be merged into a single negation.
		"""
		nargs = []
		for a in self.args:
			if isinstance(a, Fnc):
				nargs.append(a.simplify(merge_sums, merge_prods, merge_negs))
			else:
				nargs.append(a)
		name = self.name
		if name == '+':
			val = 0
			occ = {}
			nargs = []
			for a in self.args:
				if isinstance(a, (int, float)):
					val += a
				elif a in occ:
					occ[a] += 1
				else:
					occ[a] = 1
			if val != 0:
				nargs.append(val)
			for a, c in occ.items():
				if c == 1:
					nargs.append(a)
				else:
					if merge_sums:
						nargs.append(Fnc("*", [a, c], self.fmt))
					else:
						for i in range(c):
							nargs.append(a)
			if len(nargs) == 1:
				return nargs[0]
			if len(nargs) == 0:
				return 0
		elif name == '*':
			val = 1
			occ = {}
			nargs = []
			negs = 0
			for a in self.args:
				if merge_negs and isinstance(a, Fnc) and a.name == '-':
					negs += 1
					a = a.args[0]
				if isinstance(a, (int, float)):
					val *= abs(a)
					if a < 0:
						negs += 1
				elif a in occ:
					occ[a] += 1
				else:
					occ[a] = 1
			if val == 0:
				return 0
			if len(nargs) > 1 and merge_negs and negs % 2 == 1:
				val *= -1
			if val != 1:
				nargs.append(val)
			for a, c in occ.items():
				if c == 1:
					nargs.append(a)
				else:
					if merge_prods:
						nargs.append(Fnc("^", [a, c], self.fmt))
					else:
						for i in range(c):
							nargs.append(a)
			if merge_negs and negs % 2 == 1:
				return Fnc("-", [Fnc(name, nargs, self.fmt)], self.fmt)
			if len(nargs) == 1:
				return nargs[0]
		elif name == '^':
			if self.args[1] == 1:
				return self.args[0]
			if self.is_numeric():
				return self.args[0] ** self.args[1]
		elif name == 'root':
			if self.args[1] == 1:
				return self.args[0]
			if self.is_numeric():
				return self.args[0] ** (1.0 / self.args[1])
		elif name == '-':
			if self.is_numeric():
				return -self.args[0]
			ar = self.args[0]
			if isinstance(ar, Fnc) and ar.name == '-':
				return ar.args[0]
		elif name == '%':
			if self.args[1] == 1:
				return self.args[0]
			if self.is_numeric():
				return self.args[0] % self.args[1]
		elif name == '~':
			if self.is_numeric():
				return 1.0/self.args[0]
		elif name == 'abs':
			if self.is_numeric():
				return abs(self.args[0])
		elif name == 'int':
			if self.is_numeric():
				return int(self.args[0])
		elif name == 'clamp':
			if self.is_numeric():
				return min(max(self.args[0], self.args[1]), self.args[2])
		elif name == 'max':
			if self.is_numeric():
				return max(self.args[0], self.args[1])
		elif name == 'min':
			if self.is_numeric():
				return min(self.args[0], self.args[1])
		elif name == '<':
			if self.is_numeric():
				return int(self.args[0] < self.args[1])
		elif name == '<=':
			if self.is_numeric():
				return int(self.args[0] <= self.args[1])
		elif name == '==':
			return int(self.args[0] == self.args[1])
		elif name == '!':
			if self.is_numeric():
				return 0 if self.args[0] else 1
		elif name == 'or':
			val = False
			occ = {}
			nargs = []
			for a in self.args:
				if isinstance(a, (int, float)):
					val = val or a
				elif a in occ:
					occ[a] += 1
				else:
					occ[a] = 1
			nargs.append(val)
			for a in occ.keys():
				nargs.append(a)
			if len(nargs) == 1:
				return nargs[0]
		elif name == 'and':
			val = True
			occ = {}
			nargs = []
			for a in self.args:
				if isinstance(a, (int, float)):
					val = val and a
				elif a in occ:
					occ[a] += 1
				else:
					occ[a] = 1
			nargs.append(val)
			for a in occ.keys():
				nargs.append(a)
			if len(nargs) == 1:
				return nargs[0]
		elif name == 'D':
			if self.args[0] == self.args[1]:
				return self.args[0]

		# for a in range(len(nargs)):
		# 	if isinstance(nargs[a], Fnc):
		# 		nargs[a] = nargs[a].simplify(merge_sums, merge_prods, merge_negs)
		return Fnc(name, nargs, self.fmt)

	def is_numeric(self):
		"""
		Checks if the function only contains numeric arguments.
		"""
		return all([isinstance(x, (int, float)) for x in self.args])

	def dependencies(self):
		"""
		Obtains the dependencies for executing the function.
		"""
		x = []
		for a in self.args:
			if isinstance(a, str):
				x.append(a)
			elif isinstance(a, Fnc):
				x += a.dependencies()
		return list(set(x))

	def brackets(self):
		"""
		Tests if it is required to enclose the function in brackets.
		"""
		return self.name in ["+", "-", "*", "~", "^", "root", "%", "or", "and", "==", "<=", "<"]

	def latex(self, latex=True, time_var="i"):
		"""
		Returns a LaTeX-formatted string of this function.

		Args:
			latex (bool):   Whether or not to use LaTeX-based strings.
			time_var (str): The time var string name to use for complex math.
		"""
		largs = deepcopy(self.args)
		for i, a in enumerate(self.args):
			if isinstance(a, Fnc):
				txt = a.latex(latex, time_var)
				if a.brackets():
					largs[i] = "(%s)" % txt
				else:
					largs[i] = txt
			elif isinstance(a, str):
				largs[i] = "%s" % a
			else:
				largs[i] = str(a)

		f = self.fmt.get(self.name, None)
		if f is not None:
			return f(self.name, largs)

		opers = {}
		if latex:
			opers = {
				'*': r"\cdot ",
				'or': r"\wedge ",
				'and': r"\vee ",
				'!': r"\neg ",
				'~': "1/",
				"%": r"\mod ",
				"<=": r"\leq ",
				"==": r"\leftrightarrow ",
			}
		if self.name in ['+', '*', 'or', 'and']:
			op = opers.get(self.name, self.name)
			return (" %s " % op).join(largs)
		elif self.name in '-!~':
			op = opers.get(self.name, self.name)
			return "{}{}".format(op, largs[0])
		elif self.name == '^':
			if latex:
				return "%s^{%s}" % (largs[0], largs[1])
			return "%s^(%s)" % (largs[0], largs[1])
		elif self.name == 'root':
			if latex:
				return "%s^{1/%s}" % (largs[0], largs[1])
			if largs[1] == 2:
				return "sqrt(%s)" % largs[0]
			return "root(%s, %s)" % (largs[0], largs[1])
		elif self.name in ['%', '<', '<=', '==']:
			op = opers.get(self.name, self.name)
			return "%s %s %s" % (largs[0], op, largs[1])
		elif self.name == 'D':
			return largs[0]
		if latex:
			if self.name == 'der':
				return "\\dfrac{d}{d%s} %s" % (time_var, largs[0])
			if self.name == 'integral':
				return "\\int_0^{%s} %s d%s" % (time_var, largs[0], time_var)
		return "{}({})".format(self.name, ", ".join(largs))

	def apply_time(self, time=0, t="t", fmt="({time})", dt=""):
		"""
		Converts all equations to functions that take a time-argument.
		Delay blocks decrease the "time" annotation. This function is used
		to find the initial conditions of a system.

		Calling :func:`apply_time` followed by :func:`apply_delay`
		with the same time solves the system for that time.

		Args:
			time (int):     How much time in the past this must be applied.
							A positive value of :code:`n` means this is applied
							at :code:`time-n`.
			t (str/int):    The time variable name, or an integer indicative of
							a specific time that must be applied. E.g., setting
							this value to 2 will apply the the formulas at time 2.
			fmt (str):      The format for the time. By default it will be placed
							in parentheses at the end. Use :code:`{time}` to
							identify the time variable.
			dt (str):       The representation of the used delta. This will be
							appended after the :code:`n` value. Defaults to the
							empty string.
		"""
		if self.name in _MEMORY:
			time += 1
		to = t
		if isinstance(t, str):
			if time > 0:
				t += "-%d%s" % (time, dt)
			if time is None:
				t = "0"
		else:
			if time is None:
				t = 0
			else:
				t -= time
		for i, a in enumerate(self.args):
			if isinstance(a, str):
				if not isinstance(t, str) and t < 0:
					self.args[i] = "%s%s" % (a, fmt.format(time=0))
				else:
					self.args[i] = "%s%s" % (a, fmt.format(time=t))
			elif isinstance(a, Fnc):
				if self.name in _MEMORY and i == 1:
					a.apply_time(None, to, fmt, dt)
				else:
					a.apply_time(time, to, fmt, dt)

	def get_delay_depth(self, start=0):
		"""
		Counts the amount of "nested" delay blocks.

		Args:
			start (int):    Initial count value.
		"""
		c = start
		if self.name in _MEMORY:
			c += 1
		v = [c]
		for a in self.args:
			if isinstance(a, Fnc):
				v.append(a.get_delay_depth(c))
		return max(v)


def _clamp_block(block, p):
	if block._use_const:
		return p + ".OUT1", Fnc('clamp', [p + ".IN1", block.min, block.max])
	return p + ".OUT1", Fnc('clamp', [p + ".IN1", p + ".IN2", p + ".IN3"])

# Maps all standard block types onto a function that is representative of the
# corresponding equation. This function will be called with the block and its full
# path; and it should return a tuple of :code:`(LeftHandSide, RightHandSide)`.
# When the value in this dict is a string, the standard function will be used with
# the string as a function name. This standard function is:
#       lambda b, p, f=func: (p + ".OUT1", Fnc(f, [p + ".%s" % x for x in block.getInputPortNames()]))
# Note: the LHS is required to be a single value!
_BLOCK_MAP = {
	"ConstantBlock": lambda block, p: (p("OUT1"), block.getValue()),
	"NegatorBlock": lambda block, p: (p("OUT1"), Fnc('-', [p("IN1")])),
	"InverterBlock": lambda block, p: (p("OUT1"), Fnc('~', [p("IN1")])),
	"AdderBlock": '+',
	"ProductBlock": '*',
	"ModuloBlock": lambda block, p: (p("OUT1"), Fnc('%', [p("IN1"), p("IN2")])),
	"RootBlock": lambda block, p: (p("OUT1"), Fnc('root', [p("IN1"), p("IN2")])),
	"PowerBlock": lambda block, p: (p("OUT1"), Fnc('^', [p("IN1"), p("IN2")])),
	"AbsBlock": lambda block, p: (p("OUT1"), Fnc('abs', [p("IN1")])),
	"IntBlock": lambda block, p: (p("OUT1"), Fnc('int', [p("IN1")])),
	"ClampBlock": _clamp_block,
	"GenericBlock": lambda block, p: (p("OUT1"), Fnc(block.getBlockOperator(), [p("IN1")])),
	"MultiplexerBlock": 'MUX',
	"MaxBlock": 'max',
	"MinBlock": 'min',
	"LessThanBlock": lambda block, p: (p("OUT1"), Fnc('<', [p("IN1"), p("IN2")])),
	"LessThanOrEqualsBlock": lambda block, p: (p("OUT1"), Fnc('<=', [p("IN1"), p("IN2")])),
	"EqualsBlock": lambda block, p: (p("OUT1"), Fnc('==', [p("IN1"), p("IN2")])),
	"NotBlock": lambda block, p: (p("OUT1"), Fnc('!', [p("IN1")])),
	"OrBlock": 'or',
	"AndBlock": 'and',
	"DelayBlock": 'D',
	"TimeBlock": lambda block, p: (p("OUT1"), '{time}'),
	"DerivatorBlock": 'der',
	"IntegratorBlock": 'integral',
}

_MEMORY = ['D', 'der', 'integral']


if __name__ == '__main__':
	from CBD.Core import CBD
	from CBD.lib.std import *
	class Test(CBD):
		def __init__(self, name):
			super().__init__(name, [], ["x"])
			self.addBlock(AdderBlock("A"))
			self.addBlock(ProductBlock("B"))
			self.addBlock(ConstantBlock("C", 3.0))
			self.addBlock(ConstantBlock("D", -4.0))
			self.addBlock(ConstantBlock("E", -8.0))
			self.addConnection("C", "A")
			self.addConnection("D", "A")
			self.addConnection("A", "B")
			self.addConnection("E", "B")
			self.addConnection("B", "x")

	class FibonacciGen(CBD):
		def __init__(self, block_name):
			super().__init__(block_name, input_ports=[], output_ports=['OUT1'])

			# Create the Blocks
			self.addBlock(DelayBlock("delay1"))
			self.addBlock(DelayBlock("delay2"))
			self.addBlock(IntegratorBlock("delay3"))
			self.addBlock(AdderBlock("sum"))
			self.addBlock(ConstantBlock("zero", value=(0)))
			self.addBlock(ConstantBlock("one", value=(1)))
			self.addBlock(ConstantBlock("dt", value=(0.1)))

			# Create the Connections
			self.addConnection("delay1", "delay2", output_port_name='OUT1', input_port_name='IN1')
			self.addConnection("delay2", "delay3", output_port_name='OUT1', input_port_name='IN1')
			self.addConnection("delay1", "sum", output_port_name='OUT1', input_port_name='IN1')
			self.addConnection("delay2", "sum", output_port_name='OUT1', input_port_name='IN2')
			self.addConnection("delay3", "delay1", output_port_name='OUT1', input_port_name='IN1')
			self.addConnection("dt", "delay3", output_port_name='OUT1', input_port_name='delta_t')
			self.addConnection("sum", "delay3", output_port_name='OUT1', input_port_name='IN1')
			self.addConnection("zero", "delay1", output_port_name='OUT1', input_port_name='IC')
			self.addConnection("one", "delay2", output_port_name='OUT1', input_port_name='IC')
			self.addConnection("one", "delay3", output_port_name='OUT1', input_port_name='IC')
			self.addConnection("delay3", "OUT1", output_port_name='OUT1')


	ltx = CBD2Latex(FibonacciGen("fib"), render_latex=False, show_steps=True)
	# ltx.render()
	# ltx.simplify()
	# print("----------------------------")
	# print(ltx.render())
	# print("----------------------------")
	print(ltx.equations)
