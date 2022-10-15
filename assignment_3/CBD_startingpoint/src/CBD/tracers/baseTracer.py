import sys
import time
from .color import COLOR

class BaseTracer:
	"""
	Base class for all tracers.

	Args:
		uid:            A unique identifier for the tracer.
						Defaults to -1 (unset).
		filename (str): The name of the file to write to. When :code:`None`,
						the trace is written to the terminal/console.
						Defaults to :code:`None`.

	Warning:
		This class contains virtual methods and should therefore only be
		subclassed; **not** instantiated.
	"""
	def __init__(self, uid=-1, filename=None):
		self.uid = uid
		self.filename = filename
		self.file = None
		self.width = 80

	def openFile(self, recover=False):
		"""
		Opens the file.

		Args:
			recover (bool): When :code:`True`, the file needs to be recovered,
							i.e. it must be appended.
		"""
		if self.filename is None:
			self.file = sys.stdout
		elif recover:
			self.file = open(self.filename, 'a+')
		else:
			self.file = open(self.filename, 'w')

	def closeFile(self):
		"""
		Closes the file.
		"""
		self.file.flush()
		if self.filename is not None:
			self.file.close()

	def startTracer(self, recover=False):
		"""
		Starts the tracer. The file should be opened in this function.
		Additionally, file headers can be written here.

		Args:
			recover (bool): When :code:`True`, the file needs to be recovered,
							i.e. it must be appended.

		See Also:
			:func:`openFile`
		"""
		self.openFile(recover)

	def stopTracer(self):
		"""
		Stops the tracer. The file should be closed in this function.

		See Also:
			:func:`closeFile`
		"""
		self.closeFile()

	def traceNewIteration(self, curIt, time):
		"""
		Traces the start of a new iteration.

		Note:
			This function must be implemented in the subclass(es)!

		Args:
			curIt (int):    The current iteration.
			time (numeric): The current simulation time.
		"""
		raise NotImplementedError()

	def traceCompute(self, curIt, block):
		"""
		Traces the computation of a specific block.

		Note:
			This function must be implemented in the subclass(es)!

		Args:
			curIt (int):                The current iteration.
			block (CBD.Core.BaseBlock): The block for which a compute just happened.
		"""
		raise NotImplementedError()

	def trace(self, *text):
		"""
		Writes text to the trace file or the console.
		If a trace file was set, the coloring will be removed.

		Args:
			*text:  The text(s) to write.
		"""
		text = "".join(text)
		if self.filename is not None:
			text = COLOR.uncolorize(text)
		self.file.write(text)

	def traceln(self, *text):
		"""
		Writes text to the trace file, appended with a newline.

		Args:
			*text:  The text(s) to write.
		"""
		text = list(text) + ["\n"]
		self.trace(*text)

	def timeInfo(self, format="%Y-%m-%d %H:%M:%S"):
		"""
		Obtains the current time as a string, which allows detailed trace information.

		Args:
			format (str):   The format string.

		See Also:
			`Documentation on time formatting. <https://docs.python.org/3/library/time.html#time.strftime>`_
		"""
		return time.strftime(format, time.time())
