#!/usr/bin/env python
#
# Unit tests for all the basic CBD blocks, discrete-time CBD. 

import unittest

import os
from CBD.Core import *
from CBD.lib.io import *
from CBD.simulator import Simulator

class IOCBDTestCase(unittest.TestCase):
	def setUp(self):
		self.CBD = CBD("CBD_for_block_under_test")
		self.sim = Simulator(self.CBD)
		self.file = os.path.join(os.path.dirname(os.path.realpath(__file__)), "test.csv")

	def _run(self, num_steps=1, delta_t = 1.0):
		self.sim.setDeltaT(delta_t)
		self.sim.setTerminationTime(num_steps * delta_t)
		self.sim.run()

	def _getSignal(self, blockname, output_port = None):
		foundBlocks = [ block for block in self.CBD.getBlocks() if block.getBlockName() == blockname ]
		numFoundBlocks = len(foundBlocks)
		if numFoundBlocks == 1:
			signal =  foundBlocks[0].getSignal(name_output = output_port)
			return [x.value for x in signal]
		else:
			raise Exception(str(numFoundBlocks) + " blocks with name " + blockname + " found.\nExpected a single block.")

	def testCSVReaderNormal(self):
		self.CBD.addBlock(ReadCSV("seq", self.file, Interpolation.LINEAR, repeat=False))
		self._run(30)
		self.assertEqual(self._getSignal("seq", "y"),
		                 [2.0, 2.0, 2.0, 1.0, 0.0, -1.0, -2.0, -1.0, 0.0, 5.0, -5.0, 17.0] +
		                 ([10.0] * 18))

	def testCSVReaderRepeat(self):
		self.CBD.addBlock(ReadCSV("seq", self.file, Interpolation.LINEAR, repeat=True))
		self._run(12 * 4)
		self.assertEqual([10.0, 6.0, 2.0, 1.0, 0.0, -1.0, -2.0, -1.0, 0.0, 5.0, -5.0, 17.0] * 4,
		                 self._getSignal("seq", "y"))


def suite():
	"""Returns a test suite containing all the test cases in this module."""
	suite = unittest.makeSuite(IOCBDTestCase)

	return unittest.TestSuite((suite))

if __name__ == '__main__':
	# When this module is executed from the command-line, run all its tests
	unittest.main(verbosity=2)

  
  
  
  
  
  
  
  
