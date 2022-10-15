#!/usr/bin/python3
# This file was automatically generated from drawio2cbd with the command:
#   /home/red/git/DrawioConvert/__main__.py LCG.xml -av -F CBD -e LCG -t 100

from CBD.Core import *
from CBD.lib.std import *
from CBD.lib.endpoints import SignalCollectorBlock


class LCG(CBD):
    def __init__(self, block_name, a=(1), c=(4), x0=(0), m=(9)):
        CBD.__init__(self, block_name, input_ports=[], output_ports=[])

        # Create the Blocks
        self.addBlock(ConstantBlock("a", value=(a)))
        self.addBlock(ConstantBlock("x0", value=(x0)))
        self.addBlock(ConstantBlock("c", value=(c)))
        self.addBlock(ConstantBlock("m", value=(m)))
        self.addBlock(DelayBlock("delay"))
        self.addBlock(ProductBlock("mult"))
        self.addBlock(AdderBlock("sum"))
        self.addBlock(ModuloBlock("mod"))
        self.addBlock(SignalCollectorBlock("collector"))

        # Create the Connections
        self.addConnection("x0", "delay", output_port_name='OUT1', input_port_name='IC')
        self.addConnection("a", "mult", output_port_name='OUT1', input_port_name='IN1')
        self.addConnection("delay", "mult", output_port_name='OUT1', input_port_name='IN2')
        self.addConnection("mult", "sum", output_port_name='OUT1', input_port_name='IN1')
        self.addConnection("c", "sum", output_port_name='OUT1', input_port_name='IN2')
        self.addConnection("m", "mod", output_port_name='OUT1', input_port_name='IN2')
        self.addConnection("sum", "mod", output_port_name='OUT1', input_port_name='IN1')
        self.addConnection("mod", "delay", output_port_name='OUT1', input_port_name='IN1')
        self.addConnection("mod", "collector", output_port_name='OUT1', input_port_name='IN1')


