#!/usr/bin/python3
# This file was automatically generated from drawio2cbd with the command:
#   /home/red/git/DrawioConvert/__main__.py EvenNumberGen.xml -av -F CBD -e LCG -t 30 -f

from CBD.Core import *
from CBD.lib.std import *
from CBD.src.lib.endpoints import SignalCollectorBlock


class Counter(CBD):
    def __init__(self, block_name):
        CBD.__init__(self, block_name, input_ports=[], output_ports=['OutCount'])

        # Create the Blocks
        self.addBlock(ConstantBlock("zero", value=(0.0)))
        self.addBlock(DelayBlock("delay"))
        self.addBlock(ConstantBlock("one", value=(1.0)))
        self.addBlock(AdderBlock("sum"))

        # Create the Connections
        self.addConnection("zero", "delay", output_port_name='OUT1', input_port_name='IC')
        self.addConnection("delay", "sum", output_port_name='OUT1', input_port_name='IN1')
        self.addConnection("delay", "OutCount", output_port_name='OUT1')
        self.addConnection("one", "sum", output_port_name='OUT1', input_port_name='IN2')
        self.addConnection("sum", "delay", output_port_name='OUT1', input_port_name='IN1')


class Double(CBD):
    def __init__(self, block_name):
        CBD.__init__(self, block_name, input_ports=['InNumber'], output_ports=['OutDouble'])

        # Create the Blocks
        self.addBlock(ConstantBlock("two", value=(2.0)))
        self.addBlock(ProductBlock("mult"))

        # Create the Connections
        self.addConnection("InNumber", "mult", input_port_name='IN1')
        self.addConnection("two", "mult", output_port_name='OUT1', input_port_name='IN2')
        self.addConnection("mult", "OutDouble", output_port_name='OUT1')


class EvenNumberGen(CBD):
    def __init__(self, block_name):
        CBD.__init__(self, block_name, input_ports=[], output_ports=[])

        # Create the Blocks
        self.addBlock(Counter("counter"))
        self.addBlock(Double("double"))
        self.addBlock(SignalCollectorBlock("collector"))

        # Create the Connections
        self.addConnection("counter", "double", output_port_name='OutCount', input_port_name='InNumber')
        self.addConnection("double", "collector", output_port_name='OutDouble', input_port_name='IN1')


