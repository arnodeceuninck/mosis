#!/usr/bin/python3
# This file was automatically generated from drawio2cbd with the command:
#   /home/red/git/DrawioConvert/__main__.py Test.drawio -e Test -Ssargv -F CBD -E delta=0.1

from CBD.Core import *
from CBD.lib.std import *

DELTA_T = 0.1

class Test(CBD):
    def __init__(self, block_name):
        CBD.__init__(self, block_name, input_ports=[], output_ports=['y'])

        # Create the Blocks
        self.addBlock(IntegratorBlock("int"))
        self.addBlock(ConstantBlock("IC", value=(0)))
        self.addBlock(ProductBlock("mult"))
        self.addBlock(AdderBlock("sum"))
        self.addBlock(ConstantBlock("one", value=(1)))
        self.addBlock(ConstantBlock("time", value=(DELTA_T)))

        # Create the Connections
        self.addConnection("IC", "int", output_port_name='OUT1', input_port_name='IC')
        self.addConnection("int", "mult", output_port_name='OUT1', input_port_name='IN1')
        self.addConnection("int", "mult", output_port_name='OUT1', input_port_name='IN2')
        self.addConnection("int", "y", output_port_name='OUT1')
        self.addConnection("mult", "sum", output_port_name='OUT1', input_port_name='IN2')
        self.addConnection("one", "sum", output_port_name='OUT1', input_port_name='IN1')
        self.addConnection("sum", "int", output_port_name='OUT1', input_port_name='IN1')
        self.addConnection("time", "int", output_port_name='OUT1', input_port_name='delta_t')


