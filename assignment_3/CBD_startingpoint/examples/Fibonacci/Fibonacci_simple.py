#!/usr/bin/python3
# This file was automatically generated from drawio2cbd with the command:
#   /home/red/git/DrawioConvert/__main__.py Fibonacci.xml -F CBD -e FibonacciGen -gvaf

from CBD.Core import *
from CBD.lib.std import *
from CBD.lib.endpoints import SignalCollectorBlock


class FibonacciGen(CBD):
    def __init__(self, block_name):
        super().__init__(block_name, input_ports=[], output_ports=['OUT1'])

        # Create the Blocks
        self.addBlock(DelayBlock("delay1"))
        self.addBlock(DelayBlock("delay2"))
        self.addBlock(AdderBlock("sum"))
        self.addBlock(ConstantBlock("zero", value=(0)))
        self.addBlock(ConstantBlock("one", value=(1)))

        # Create the Connections
        self.addConnection("delay1", "delay2", output_port_name='OUT1', input_port_name='IN1')
        self.addConnection("delay1", "sum", output_port_name='OUT1', input_port_name='IN2')
        self.addConnection("delay2", "sum", output_port_name='OUT1', input_port_name='IN1')
        self.addConnection("sum", "delay1", output_port_name='OUT1', input_port_name='IN1')
        self.addConnection("sum", "OUT1", output_port_name='OUT1')
        self.addConnection("zero", "delay1", output_port_name='OUT1', input_port_name='IC')
        self.addConnection("one", "delay2", output_port_name='OUT1', input_port_name='IC')


