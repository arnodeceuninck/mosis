#!/usr/bin/python3
# This file was automatically generated from drawio2cbd with the command:
#   /home/red/git/DrawioConvert/__main__.py Fibonacci.xml -F CBD -e FibonacciGen -gvaf

from CBD.Core import *
from CBD.lib.std import *
from CBD.lib.endpoints import SignalCollectorBlock


class InitialConditions(CBD):
    def __init__(self, block_name):
        super().__init__(block_name, input_ports=[], output_ports=['OUT1', 'OUT3', 'OUT2'])

        # Create the Blocks
        self.addBlock(ConstantBlock("two", value=(2.0)))
        self.addBlock(ConstantBlock("one", value=(1.0)))
        self.addBlock(AdderBlock("sum1"))
        self.addBlock(AdderBlock("sum2"))
        self.addBlock(NegatorBlock("neg1"))
        self.addBlock(NegatorBlock("neg2"))
        self.addBlock(RootBlock("root"))

        # Create the Connections
        self.addConnection("two", "sum1", output_port_name='OUT1', input_port_name='IN1')
        self.addConnection("two", "root", output_port_name='OUT1', input_port_name='IN2')
        self.addConnection("sum1", "sum2", output_port_name='OUT1', input_port_name='IN1')
        self.addConnection("sum1", "neg1", output_port_name='OUT1', input_port_name='IN1')
        self.addConnection("sum1", "OUT1", output_port_name='OUT1')
        self.addConnection("one", "neg2", output_port_name='OUT1', input_port_name='IN1')
        self.addConnection("one", "root", output_port_name='OUT1', input_port_name='IN1')
        self.addConnection("neg2", "sum2", output_port_name='OUT1', input_port_name='IN2')
        self.addConnection("neg1", "sum1", output_port_name='OUT1', input_port_name='IN2')
        self.addConnection("root", "OUT3", output_port_name='OUT1')
        self.addConnection("sum2", "OUT2", output_port_name='OUT1')


class FibonacciGen2(CBD):
    def __init__(self, block_name):
        super().__init__(block_name, input_ports=[], output_ports=[])

        # Create the Blocks
        self.addBlock(InitialConditions("ic"))
        self.addBlock(DelayBlock("D1"))
        self.addBlock(DelayBlock("D2"))
        self.addBlock(DelayBlock("D3"))
        self.addBlock(AdderBlock("sum"))
        self.addBlock(SignalCollectorBlock("collector"))

        # Create the Connections
        self.addConnection("ic", "D3", output_port_name='OUT3', input_port_name='IC')
        self.addConnection("ic", "D2", output_port_name='OUT2', input_port_name='IC')
        self.addConnection("ic", "D1", output_port_name='OUT1', input_port_name='IC')
        self.addConnection("D2", "sum", output_port_name='OUT1', input_port_name='IN2')
        self.addConnection("D1", "sum", output_port_name='OUT1', input_port_name='IN1')
        self.addConnection("D1", "D2", output_port_name='OUT1', input_port_name='IN1')
        self.addConnection("sum", "D3", output_port_name='OUT1', input_port_name='IN1')
        self.addConnection("sum", "D1", output_port_name='OUT1', input_port_name='IN1')
        self.addConnection("D3", "collector", output_port_name='OUT1', input_port_name='IN1')


