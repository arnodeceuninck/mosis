#!/usr/bin/env python
#
# Unit tests for all the basic CBD blocks, discrete-time CBD.

import unittest

from assignment_3.CBD_startingpoint.src.CBD.Core import *
from assignment_3.CBD_startingpoint.src.CBD.lib.std import *
from assignment_3.CBD_startingpoint.src.CBD.simulator import Simulator


class OtherCBDTestCase(unittest.TestCase):
    def setUp(self):
        self.CBD = CBD("CBD_for_block_under_test")
        self.sim = Simulator(self.CBD)

    def _run(self, num_steps=1, delta_t=1.0):
        self.sim.setDeltaT(delta_t)
        self.sim.setTerminationTime(num_steps * delta_t)
        self.sim.run()

    def _getSignal(self, blockname, output_port=None):
        foundBlocks = [block for block in self.CBD.getBlocks() if block.getBlockName() == blockname]
        numFoundBlocks = len(foundBlocks)
        if numFoundBlocks == 1:
            signal = foundBlocks[0].getSignal(name_output=output_port)
            return [x.value for x in signal]
        else:
            raise Exception(
                str(numFoundBlocks) + " blocks with name " + blockname + " found.\nExpected a single block.")

    def testMultiRate(self):
        self.CBD.addBlock(TimeBlock("time"))
        self.CBD.addBlock(ConstantBlock("two", 2.0))
        self.CBD.addBlock(ProductBlock("mult"))

        self.CBD.addConnection("time", "mult")
        self.CBD.addConnection("two", "mult")

        self.sim.setBlockRate(self.CBD.getBlockByName("mult").getPath(), 2.0)

        self._run(10)

        self.assertEqual([0.0, 4.0, 8.0, 12.0, 16.0], self._getSignal("mult"))


def suite():
    """Returns a test suite containing all the test cases in this module."""
    suite = unittest.makeSuite(IOCBDTestCase)

    return unittest.TestSuite((suite))


if __name__ == '__main__':
    # When this module is executed from the command-line, run all its tests
    unittest.main(verbosity=2)
