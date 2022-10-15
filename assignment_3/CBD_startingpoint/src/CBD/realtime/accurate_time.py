"""
Custom time module to keep things platform- and Python version-independent.
"""
import time as python_time
from ..util import PYTHON_VERSION
import sys

def time():
	"""
	Gets the correct system time, independent of the Python version or the
	platform.
	"""
	if PYTHON_VERSION == 2 and sys.platform == "win32":
		return python_time.clock()  # << better precision on windows
	else:
		return python_time.time()

def sleep(t):
	"""
	Sleeps for a while.

	Args:
		t (float):  Amount of seconds to sleep.
	"""
	python_time.sleep(t)
