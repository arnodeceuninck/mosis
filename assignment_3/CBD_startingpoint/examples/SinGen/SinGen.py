#!/usr/bin/python3
# This file was automatically generated from drawio2cbd with the command:
#   /home/red/git/DrawioConvert/__main__.py SinGen.xml -fav -F CBD -e SinGen -E delta=0.1

from CBD.Core import *
from CBD.lib.std import *
from CBD.lib.endpoints import SignalCollectorBlock

DELTA_T = 0.1

class SinGen(CBD):
    def __init__(self, block_name):
        CBD.__init__(self, block_name, input_ports=[], output_ports=[])

        # Create the Blocks
        self.addBlock(GenericBlock("sin", block_operator=("sin")))
        self.addBlock(TimeBlock("navfwlU7EP--ZkxJ3C-2-12"))
        self.addBlock(SignalCollectorBlock("plot"))

        # Create the Connections
        self.addConnection("navfwlU7EP--ZkxJ3C-2-12", "sin", output_port_name='OUT1', input_port_name='IN1')
        self.addConnection("sin", "plot", output_port_name='OUT1', input_port_name='IN1')


