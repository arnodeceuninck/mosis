#!/usr/bin/python3
# This file was automatically generated from drawio2cbd with the command:
#   C:/Users/dogukan/Desktop/UA/2021-2022/mosis/assignment_3/DrawioConvert/__main__.py -F CBD -e LookUpTableBlock -sSrgv LookUpTableBlock.drawio.xml -E delta=0.1

from CBD.Core import *
from CBD.lib.std import *

DELTA_T = 0.1

class LookUpTable(CBD):
    def __init__(self, block_name):
        super().__init__(block_name, input_ports=[], output_ports=['OUT1'])

        # Create the Blocks
        self.addBlock(LessThanBlock("_l-YlHAasBxaOKrxFiZ4-4"))
        self.addBlock(ConstantBlock("_l-YlHAasBxaOKrxFiZ4-9", value=(10)))
        self.addBlock(MultiplexerBlock("_l-YlHAasBxaOKrxFiZ4-20"))
        self.addBlock(ConstantBlock("_l-YlHAasBxaOKrxFiZ4-26", value=(0)))
        self.addBlock(ConstantBlock("_l-YlHAasBxaOKrxFiZ4-34", value=(170)))
        self.addBlock(LessThanBlock("_l-YlHAasBxaOKrxFiZ4-36"))
        self.addBlock(MultiplexerBlock("_l-YlHAasBxaOKrxFiZ4-42"))
        self.addBlock(ConstantBlock("_l-YlHAasBxaOKrxFiZ4-49", value=(10)))
        self.addBlock(ConstantBlock("_l-YlHAasBxaOKrxFiZ4-56", value=(200)))
        self.addBlock(LessThanBlock("_l-YlHAasBxaOKrxFiZ4-58"))
        self.addBlock(MultiplexerBlock("_l-YlHAasBxaOKrxFiZ4-62"))
        self.addBlock(ConstantBlock("_l-YlHAasBxaOKrxFiZ4-67", value=(8)))
        self.addBlock(TimeBlock("_l-YlHAasBxaOKrxFiZ4-76"))
        self.addBlock(ConstantBlock("_l-YlHAasBxaOKrxFiZ4-78", value=(260)))
        self.addBlock(LessThanBlock("_l-YlHAasBxaOKrxFiZ4-80"))
        self.addBlock(MultiplexerBlock("_l-YlHAasBxaOKrxFiZ4-84"))
        self.addBlock(ConstantBlock("_l-YlHAasBxaOKrxFiZ4-89", value=(18)))
        self.addBlock(ConstantBlock("_l-YlHAasBxaOKrxFiZ4-138", value=(12)))

        # Create the Connections
        self.addConnection("_l-YlHAasBxaOKrxFiZ4-9", "_l-YlHAasBxaOKrxFiZ4-4", output_port_name='OUT1', input_port_name='IN2')
        self.addConnection("_l-YlHAasBxaOKrxFiZ4-4", "_l-YlHAasBxaOKrxFiZ4-20", output_port_name='OUT1', input_port_name='select')
        self.addConnection("_l-YlHAasBxaOKrxFiZ4-26", "_l-YlHAasBxaOKrxFiZ4-20", output_port_name='OUT1', input_port_name='IN1')
        self.addConnection("_l-YlHAasBxaOKrxFiZ4-34", "_l-YlHAasBxaOKrxFiZ4-36", output_port_name='OUT1', input_port_name='IN2')
        self.addConnection("_l-YlHAasBxaOKrxFiZ4-36", "_l-YlHAasBxaOKrxFiZ4-42", output_port_name='OUT1', input_port_name='select')
        self.addConnection("_l-YlHAasBxaOKrxFiZ4-42", "_l-YlHAasBxaOKrxFiZ4-20", output_port_name='OUT1', input_port_name='IN2')
        self.addConnection("_l-YlHAasBxaOKrxFiZ4-56", "_l-YlHAasBxaOKrxFiZ4-58", output_port_name='OUT1', input_port_name='IN2')
        self.addConnection("_l-YlHAasBxaOKrxFiZ4-58", "_l-YlHAasBxaOKrxFiZ4-62", output_port_name='OUT1', input_port_name='select')
        self.addConnection("_l-YlHAasBxaOKrxFiZ4-49", "_l-YlHAasBxaOKrxFiZ4-42", output_port_name='OUT1', input_port_name='IN1')
        self.addConnection("_l-YlHAasBxaOKrxFiZ4-67", "_l-YlHAasBxaOKrxFiZ4-62", output_port_name='OUT1', input_port_name='IN1')
        self.addConnection("_l-YlHAasBxaOKrxFiZ4-62", "_l-YlHAasBxaOKrxFiZ4-42", output_port_name='OUT1', input_port_name='IN2')
        self.addConnection("_l-YlHAasBxaOKrxFiZ4-76", "_l-YlHAasBxaOKrxFiZ4-80", output_port_name='OUT1', input_port_name='IN1')
        self.addConnection("_l-YlHAasBxaOKrxFiZ4-76", "_l-YlHAasBxaOKrxFiZ4-58", output_port_name='OUT1', input_port_name='IN1')
        self.addConnection("_l-YlHAasBxaOKrxFiZ4-76", "_l-YlHAasBxaOKrxFiZ4-36", output_port_name='OUT1', input_port_name='IN1')
        self.addConnection("_l-YlHAasBxaOKrxFiZ4-76", "_l-YlHAasBxaOKrxFiZ4-4", output_port_name='OUT1', input_port_name='IN1')
        self.addConnection("_l-YlHAasBxaOKrxFiZ4-78", "_l-YlHAasBxaOKrxFiZ4-80", output_port_name='OUT1', input_port_name='IN2')
        self.addConnection("_l-YlHAasBxaOKrxFiZ4-80", "_l-YlHAasBxaOKrxFiZ4-84", output_port_name='OUT1', input_port_name='select')
        self.addConnection("_l-YlHAasBxaOKrxFiZ4-89", "_l-YlHAasBxaOKrxFiZ4-84", output_port_name='OUT1', input_port_name='IN1')
        self.addConnection("_l-YlHAasBxaOKrxFiZ4-84", "_l-YlHAasBxaOKrxFiZ4-62", output_port_name='OUT1', input_port_name='IN2')
        self.addConnection("_l-YlHAasBxaOKrxFiZ4-138", "_l-YlHAasBxaOKrxFiZ4-84", output_port_name='OUT1', input_port_name='IN2')
        self.addConnection("_l-YlHAasBxaOKrxFiZ4-20", "OUT1", output_port_name='OUT1')


