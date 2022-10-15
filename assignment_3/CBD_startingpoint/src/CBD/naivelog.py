"""
Helper module to allow for simplified logging.

Warning:
	In the future, this module may be removed. Its logic will
	be separated into some tracers and a SysLog logger.
"""
import os
import sys
import datetime

DEBUG, INFO, WARNING, ERROR, FATAL = 0, 1, 2, 3, 4
"""Level identifier."""

def strToLevel(elvl):
	"""
	Go from string identifier of a logging level to the
	level identifier.

	Args:
		elvl (str): Must be one of :code:`DEBUG`, :code:`INFO`,
					:code:`WARNING`, :code:`ERROR` or :code:`FATAL`,
					case-sensitive.

	See Also:
		- :func:`levelToStr`
		- :func:`levelToShortStr`
	"""
	if elvl == "DEBUG":
		return DEBUG
	if elvl == "INFO":
		return INFO
	if elvl == "WARNING":
		return WARNING
	if elvl == "ERROR":
		return ERROR
	if elvl == "FATAL":
		return FATAL
	else:
		return None

def levelToStr(lvl):
	"""
	Go from a level identifier to the corresponding string representation.

	Args:
		lvl (int):  The level identifier.

	See Also:
		- :func:`strToLevel`
		- :func:`levelToShortStr`
	"""
	if lvl == DEBUG:
		return "DEBUG"
	if lvl == INFO:
		return "INFO"
	if lvl == WARNING:
		return "WARNING"
	if lvl == ERROR:
		return "ERROR"
	if lvl == FATAL:
		return "FATAL"
	return None


def levelToShortStr(lvl):
	"""
	Go from a level identifier to a short, representative string.

	Args:
		lvl (int):  The level identifier.

	See Also:
		- :func:`strToLevel`
		- :func:`levelToStr`
	"""
	if lvl == DEBUG:
		return "DBUG"
	if lvl == INFO:
		return "INFO"
	if lvl == WARNING:
		return "WARN"
	if lvl == ERROR:
		return "ERROR"
	if lvl == FATAL:
		return "FATAL"
	return None

class Logger:
	"""
	A simple logging class.

	Args:
		modulename (str):   The name of the module.
		level (int):        Lowest level for the logger to output.
		crashlevel (int):   Level at which the logger should terminate.
	"""
	def __init__(self, modulename, level, crashlevel):
		self.__modulename = modulename
		self.__level = level
		self.__crashlevel = crashlevel

	def debug(self, mainstr, *args, **kwargs):
		"""
		Send :code:`DEBUG` message. Wrapper around the :func:`log` function.

		Args:
			mainstr (str):  The main message information.
			*args:          List of arguments for formatting the :code:`mainstr`.
			**kwargs:       List of keyword arguments for formatting the
							:code:`mainstr`.
		"""
		self.log(DEBUG, mainstr, *args, **kwargs)

	def info(self, mainstr, *args, **kwargs):
		"""
		Send :code:`INFO` message. Wrapper around the :func:`log` function.

		Args:
			mainstr (str):  The main message information.
			*args:          List of arguments for formatting the :code:`mainstr`.
			**kwargs:       List of keyword arguments for formatting the
							:code:`mainstr`.
		"""
		self.log(INFO, mainstr, *args, **kwargs)

	def warning(self, mainstr, *args, **kwargs):
		"""
		Send :code:`WARNING` message. Wrapper around the :func:`log` function.

		Args:
			mainstr (str):  The main message information.
			*args:          List of arguments for formatting the :code:`mainstr`.
			**kwargs:       List of keyword arguments for formatting the
							:code:`mainstr`.
		"""
		self.log(WARNING, mainstr, *args, **kwargs)

	def error(self, mainstr, *args, **kwargs):
		"""
		Send :code:`ERROR` message. Wrapper around the :func:`log` function.

		Args:
			mainstr (str):  The main message information.
			*args:          List of arguments for formatting the :code:`mainstr`.
			**kwargs:       List of keyword arguments for formatting the
							:code:`mainstr`.
		"""
		self.log(ERROR, mainstr, *args, **kwargs)

	def fatal(self, mainstr, *args, **kwargs):
		"""
		Send :code:`FATAL` message. Wrapper around the :func:`log` function.

		Args:
			mainstr (str):  The main message information.
			*args:          List of arguments for formatting the :code:`mainstr`.
			**kwargs:       List of keyword arguments for formatting the
							:code:`mainstr`.
		"""
		self.log(FATAL, mainstr, *args, **kwargs)

	def log(self, level, mainstr, *args, **kwargs):
		"""
		Send a message.

		Args:
			level (int):    Level at which there must be logged.
			mainstr (str):  The main message information.
			*args:          List of arguments for formatting the :code:`mainstr`.
			**kwargs:       List of keyword arguments for formatting the
							:code:`mainstr`.

		See Also:
			- :func:`debug`
			- :func:`info`
			- :func:`warning`
			- :func:`error`
			- :func:`fatal`
		"""
		if level >= self.__level:
			sys.stdout.write(self.formatmsg(level,str(mainstr).format(*args, **kwargs)))

		if level >= self.__crashlevel:
			exit(1)

	def setLevel(self, level):
		"""
		Sets the level to a new value.

		Args:
			level (int):    The new level.
		"""
		self.__level = level

	def formatmsg(self, level, mainstr):
		"""
		Formats the message, used internally.

		Args:
			level (int):    The level of the message.
			mainstr (str):  The main message to print.
		"""
		class bcolors:
			"""
			Helper class to set the colors to the terminal.
			"""
			HEADER = '\033[95m'
			OKBLUE = '\033[94m'
			OKGREEN = '\033[92m'
			WARNING = '\033[93m'
			FAIL = '\033[91m'
			ENDC = '\033[0m'


		col = bcolors.OKGREEN
		if level >= WARNING:
			col = bcolors.WARNING
		if level >= ERROR:
			col = bcolors.FAIL

		return "{startcol}[{now:%H:%M:%S.%f} {module} {lvl}] {mainstr}{endcol}\n".format(
				lvl=levelToShortStr(level),
				module=self.__modulename,
				now=datetime.date.today(),
				mainstr=mainstr,
				startcol=col,
				endcol=bcolors.ENDC)

defaultLogLevel = INFO
"""Default level at which logging is enabled."""

defaultCrashLevel = FATAL
"""Default level at which a termination must occur."""

def getAbstractLogLevel(env, default):
	"""
	Obtains the log level from the environment variables.

	Args:
		env (str):      Variable name.
		default (Any):  The default value if the variable does not
						exist.
	"""
	elvl = os.environ[env] if env in os.environ else ''

	lvl = strToLevel(elvl)
	if lvl:
		return lvl
	else:
		return default

def getLogLevel():
	"""
	Gets the logging level from the environment.
	"""
	return getAbstractLogLevel('NAIVE_LOGLEVEL', defaultLogLevel)

def getCrashLevel():
	"""
	Gets the crash level from the environment.
	"""
	return getAbstractLogLevel('NAIVE_CRASHLEVEL', defaultCrashLevel)

def getLogger(modulename):
	"""
	Gets the logger for a certain module.

	Args:
		modulename (str):   The module's name.
	"""
	return Logger(modulename, getLogLevel(), getCrashLevel())

if __name__ == "__main__":
	l = getLogger('testmodule')
	l.info("bla")
	l.info("test nummer {}{}", 2, " is good")
	l.info("test {hier} is ook ok", hier=3, daar=4)
	l.info("should not see this")


	l2 = getLogger('testmodule.m2')
	l2.info("More info")
	l2.info("and even more")
