from CBD.Core import *
from CBD.lib.std import *


class FactorialBlock(CBD):
    def __init__(self, block_name):
        super().__init__(block_name, input_ports=[], output_ports=['OUT1'])

        # Create the Blocks
        self.addBlock(ProductBlock("tBfipwNkkbDthypPoH6E-7"))
        self.addBlock(DelayBlock("tBfipwNkkbDthypPoH6E-12"))
        self.addBlock(EqualsBlock("tBfipwNkkbDthypPoH6E-18"))
        self.addBlock(ConstantBlock("tBfipwNkkbDthypPoH6E-22", value=(0)))
        self.addBlock(AdderBlock("tBfipwNkkbDthypPoH6E-27"))
        self.addBlock(ConstantBlock("tBfipwNkkbDthypPoH6E-35", value=(1)))
        self.addBlock(TimeBlock("4l0UysXjW6RqrtF_B9rH-6"))

        # Create the Connections
        self.addConnection("tBfipwNkkbDthypPoH6E-12", "tBfipwNkkbDthypPoH6E-7", output_port_name='OUT1',
                           input_port_name='IN2')
        self.addConnection("tBfipwNkkbDthypPoH6E-22", "tBfipwNkkbDthypPoH6E-18", output_port_name='OUT1',
                           input_port_name='IN1')
        self.addConnection("tBfipwNkkbDthypPoH6E-18", "tBfipwNkkbDthypPoH6E-27", output_port_name='OUT1',
                           input_port_name='IN1')
        self.addConnection("tBfipwNkkbDthypPoH6E-7", "tBfipwNkkbDthypPoH6E-27", output_port_name='OUT1',
                           input_port_name='IN2')
        self.addConnection("tBfipwNkkbDthypPoH6E-27", "tBfipwNkkbDthypPoH6E-12", output_port_name='OUT1',
                           input_port_name='IN1')
        self.addConnection("tBfipwNkkbDthypPoH6E-27", "OUT1", output_port_name='OUT1')
        self.addConnection("tBfipwNkkbDthypPoH6E-35", "tBfipwNkkbDthypPoH6E-12", output_port_name='OUT1',
                           input_port_name='IC')
        self.addConnection("4l0UysXjW6RqrtF_B9rH-6", "tBfipwNkkbDthypPoH6E-18", output_port_name='OUT1',
                           input_port_name='IN2')
        self.addConnection("4l0UysXjW6RqrtF_B9rH-6", "tBfipwNkkbDthypPoH6E-7", output_port_name='OUT1',
                           input_port_name='IN1')


class ForwardsIntegratorBlock(CBD):
    """
    The integrator block is a CBD that calculates the integration.
    The block is implemented according to the forwards Euler rule.
    """

    def __init__(self, block_name):
        CBD.__init__(self, block_name, ["IN1", "delta_t", "IC"], ["OUT1"])

        # Create the Blocks
        self.addBlock(DelayBlock("JXq-RYHm1Y9GmrViecSe-6"))
        self.addBlock(AdderBlock("JXq-RYHm1Y9GmrViecSe-10"))
        self.addBlock(AdderBlock("JXq-RYHm1Y9GmrViecSe-14"))
        self.addBlock(ProductBlock("JXq-RYHm1Y9GmrViecSe-18"))
        self.addBlock(NegatorBlock("JXq-RYHm1Y9GmrViecSe-22"))

        # Create the Connections
        self.addConnection("IC", "JXq-RYHm1Y9GmrViecSe-10", input_port_name='IN1')
        self.addConnection("IN1", "JXq-RYHm1Y9GmrViecSe-18", input_port_name='IN1')
        self.addConnection("delta_t", "JXq-RYHm1Y9GmrViecSe-18", input_port_name='IN2')
        self.addConnection("JXq-RYHm1Y9GmrViecSe-18", "JXq-RYHm1Y9GmrViecSe-22", output_port_name='OUT1',
                           input_port_name='IN1')
        self.addConnection("JXq-RYHm1Y9GmrViecSe-18", "JXq-RYHm1Y9GmrViecSe-14", output_port_name='OUT1',
                           input_port_name='IN2')
        self.addConnection("JXq-RYHm1Y9GmrViecSe-22", "JXq-RYHm1Y9GmrViecSe-10", output_port_name='OUT1',
                           input_port_name='IN2')
        self.addConnection("JXq-RYHm1Y9GmrViecSe-10", "JXq-RYHm1Y9GmrViecSe-6", output_port_name='OUT1',
                           input_port_name='IC')
        self.addConnection("JXq-RYHm1Y9GmrViecSe-6", "JXq-RYHm1Y9GmrViecSe-14", output_port_name='OUT1',
                           input_port_name='IN1')
        self.addConnection("JXq-RYHm1Y9GmrViecSe-14", "JXq-RYHm1Y9GmrViecSe-6", output_port_name='OUT1',
                           input_port_name='IN1')
        self.addConnection("JXq-RYHm1Y9GmrViecSe-14", "OUT1", output_port_name='OUT1')
        pass


class BackwardsIntegratorBlock(CBD):
    """
    The integrator block is a CBD that calculates the integration.
    The block is implemented according to the backwards Euler rule.
    """

    def __init__(self, block_name):
        CBD.__init__(self, block_name, ["IN1", "delta_t", "IC"], ["OUT1"])

        # Create the Blocks
        self.addBlock(DelayBlock("A1-xDxaG78zK10PtN00b-6"))
        self.addBlock(ProductBlock("A1-xDxaG78zK10PtN00b-11"))
        self.addBlock(AdderBlock("A1-xDxaG78zK10PtN00b-17"))
        self.addBlock(DelayBlock("A1-xDxaG78zK10PtN00b-22"))
        self.addBlock(ConstantBlock("761zdItCE1HLNNpBY14G-1", value=(0)))
        self.addBlock(InverterBlock("761zdItCE1HLNNpBY14G-6"))
        self.addBlock(ProductBlock("761zdItCE1HLNNpBY14G-10"))

        # Create the Connections
        self.addConnection("IC", "761zdItCE1HLNNpBY14G-10", input_port_name='IN1')
        self.addConnection("IN1", "A1-xDxaG78zK10PtN00b-6", input_port_name='IN1')
        self.addConnection("delta_t", "A1-xDxaG78zK10PtN00b-11", input_port_name='IN2')
        self.addConnection("delta_t", "761zdItCE1HLNNpBY14G-6", input_port_name='IN1')
        self.addConnection("A1-xDxaG78zK10PtN00b-6", "A1-xDxaG78zK10PtN00b-11", output_port_name='OUT1',
                           input_port_name='IN1')
        self.addConnection("A1-xDxaG78zK10PtN00b-11", "A1-xDxaG78zK10PtN00b-17", output_port_name='OUT1',
                           input_port_name='IN2')
        self.addConnection("A1-xDxaG78zK10PtN00b-22", "A1-xDxaG78zK10PtN00b-17", output_port_name='OUT1',
                           input_port_name='IN1')
        self.addConnection("A1-xDxaG78zK10PtN00b-17", "A1-xDxaG78zK10PtN00b-22", output_port_name='OUT1',
                           input_port_name='IN1')
        self.addConnection("A1-xDxaG78zK10PtN00b-17", "OUT1", output_port_name='OUT1')
        self.addConnection("761zdItCE1HLNNpBY14G-1", "A1-xDxaG78zK10PtN00b-22", output_port_name='OUT1',
                           input_port_name='IC')
        self.addConnection("761zdItCE1HLNNpBY14G-6", "761zdItCE1HLNNpBY14G-10", output_port_name='OUT1',
                           input_port_name='IN2')
        self.addConnection("761zdItCE1HLNNpBY14G-10", "A1-xDxaG78zK10PtN00b-6", output_port_name='OUT1',
                           input_port_name='IC')

class TrapezoidIntegrator(CBD):
    def __init__(self, block_name):
        super().__init__(block_name, input_ports=['delta_t', 'IC', 'IN1'], output_ports=['OUT1'])

        # Create the Blocks
        self.addBlock(AdderBlock("dyW6lUOR_W77oT1eDYwR-0"))
        self.addBlock(DelayBlock("dyW6lUOR_W77oT1eDYwR-4"))
        self.addBlock(ProductBlock("dyW6lUOR_W77oT1eDYwR-8"))
        self.addBlock(ConstantBlock("dyW6lUOR_W77oT1eDYwR-12", value=(2)))
        self.addBlock(InverterBlock("dyW6lUOR_W77oT1eDYwR-14"))
        self.addBlock(ProductBlock("dyW6lUOR_W77oT1eDYwR-25"))
        self.addBlock(AdderBlock("dyW6lUOR_W77oT1eDYwR-31"))
        self.addBlock(DelayBlock("dyW6lUOR_W77oT1eDYwR-37"))
        self.addBlock(ConstantBlock("dyW6lUOR_W77oT1eDYwR-44", value=(0)))
        self.addBlock(TrapezoidInitialCondition("d5DzESwMpZbKSwdefnG8-39"))

        # Create the Connections
        self.addConnection("dyW6lUOR_W77oT1eDYwR-14", "dyW6lUOR_W77oT1eDYwR-8", output_port_name='OUT1', input_port_name='IN1')
        self.addConnection("dyW6lUOR_W77oT1eDYwR-0", "dyW6lUOR_W77oT1eDYwR-8", output_port_name='OUT1', input_port_name='IN2')
        self.addConnection("dyW6lUOR_W77oT1eDYwR-4", "dyW6lUOR_W77oT1eDYwR-0", output_port_name='OUT1', input_port_name='IN2')
        self.addConnection("delta_t", "dyW6lUOR_W77oT1eDYwR-25", input_port_name='IN2')
        self.addConnection("delta_t", "d5DzESwMpZbKSwdefnG8-39", input_port_name='delta_t')
        self.addConnection("dyW6lUOR_W77oT1eDYwR-8", "dyW6lUOR_W77oT1eDYwR-25", output_port_name='OUT1', input_port_name='IN1')
        self.addConnection("dyW6lUOR_W77oT1eDYwR-25", "dyW6lUOR_W77oT1eDYwR-31", output_port_name='OUT1', input_port_name='IN2')
        self.addConnection("dyW6lUOR_W77oT1eDYwR-31", "OUT1", output_port_name='OUT1')
        self.addConnection("dyW6lUOR_W77oT1eDYwR-31", "dyW6lUOR_W77oT1eDYwR-37", output_port_name='OUT1', input_port_name='IN1')
        self.addConnection("dyW6lUOR_W77oT1eDYwR-37", "dyW6lUOR_W77oT1eDYwR-31", output_port_name='OUT1', input_port_name='IN1')
        self.addConnection("dyW6lUOR_W77oT1eDYwR-44", "dyW6lUOR_W77oT1eDYwR-37", output_port_name='OUT1', input_port_name='IC')
        self.addConnection("IC", "d5DzESwMpZbKSwdefnG8-39", input_port_name='IC')
        self.addConnection("d5DzESwMpZbKSwdefnG8-39", "dyW6lUOR_W77oT1eDYwR-4", output_port_name='OUT1', input_port_name='IC')
        self.addConnection("IN1", "d5DzESwMpZbKSwdefnG8-39", input_port_name='IN1')
        self.addConnection("IN1", "dyW6lUOR_W77oT1eDYwR-4", input_port_name='IN1')
        self.addConnection("IN1", "dyW6lUOR_W77oT1eDYwR-0", input_port_name='IN1')
        self.addConnection("dyW6lUOR_W77oT1eDYwR-12", "dyW6lUOR_W77oT1eDYwR-14", output_port_name='OUT1', input_port_name='IN1')

class TrapezoidInitialCondition(CBD):
    def __init__(self, block_name):
        super().__init__(block_name, input_ports=['delta_t', 'IC', 'IN1'], output_ports=['OUT1'])

        # Create the Blocks
        self.addBlock(ProductBlock("d5DzESwMpZbKSwdefnG8-5"))
        self.addBlock(ConstantBlock("d5DzESwMpZbKSwdefnG8-9", value=(2)))
        self.addBlock(InverterBlock("d5DzESwMpZbKSwdefnG8-14"))
        self.addBlock(ProductBlock("d5DzESwMpZbKSwdefnG8-18"))
        self.addBlock(NegatorBlock("d5DzESwMpZbKSwdefnG8-25"))
        self.addBlock(AdderBlock("d5DzESwMpZbKSwdefnG8-29"))

        # Create the Connections
        self.addConnection("IC", "d5DzESwMpZbKSwdefnG8-5", input_port_name='IN2')
        self.addConnection("d5DzESwMpZbKSwdefnG8-9", "d5DzESwMpZbKSwdefnG8-5", output_port_name='OUT1', input_port_name='IN1')
        self.addConnection("delta_t", "d5DzESwMpZbKSwdefnG8-14", input_port_name='IN1')
        self.addConnection("d5DzESwMpZbKSwdefnG8-5", "d5DzESwMpZbKSwdefnG8-18", output_port_name='OUT1', input_port_name='IN1')
        self.addConnection("d5DzESwMpZbKSwdefnG8-14", "d5DzESwMpZbKSwdefnG8-18", output_port_name='OUT1', input_port_name='IN2')
        self.addConnection("IN1", "d5DzESwMpZbKSwdefnG8-25", input_port_name='IN1')
        self.addConnection("d5DzESwMpZbKSwdefnG8-25", "d5DzESwMpZbKSwdefnG8-29", output_port_name='OUT1', input_port_name='IN2')
        self.addConnection("d5DzESwMpZbKSwdefnG8-18", "d5DzESwMpZbKSwdefnG8-29", output_port_name='OUT1', input_port_name='IN1')
        self.addConnection("d5DzESwMpZbKSwdefnG8-29", "OUT1", output_port_name='OUT1')



class SimpsonBlock(CBD):
    def __init__(self, block_name):
        super().__init__(block_name, input_ports=['IN1', 'delta_t', 'IC'], output_ports=['OUT1'])

        # Create the Blocks
        self.addBlock(TimeBlock("ihgbk0rLZbIN8TCgCPIG-36"))
        self.addBlock(MultiplexerBlock("ihgbk0rLZbIN8TCgCPIG-61"))
        self.addBlock(DelayBlock("ihgbk0rLZbIN8TCgCPIG-71"))
        self.addBlock(DelayBlock("ihgbk0rLZbIN8TCgCPIG-75"))
        self.addBlock(ConstantBlock("ihgbk0rLZbIN8TCgCPIG-81", value=(0)))
        self.addBlock(ConstantBlock("b4nyJ0-0gb9Xj1dY3D5m-7", value=(0)))
        self.addBlock(AdderBlock("b4nyJ0-0gb9Xj1dY3D5m-10"))
        self.addBlock(DelayBlock("b4nyJ0-0gb9Xj1dY3D5m-14"))
        self.addBlock(NegatorBlock("b4nyJ0-0gb9Xj1dY3D5m-22"))
        self.addBlock(AdderBlock("b4nyJ0-0gb9Xj1dY3D5m-26"))
        self.addBlock(SimpsonFormula("b4nyJ0-0gb9Xj1dY3D5m-37"))
        self.addBlock(AdderBlock("b4nyJ0-0gb9Xj1dY3D5m-45"))
        self.addBlock(MultiplexerBlock("b4nyJ0-0gb9Xj1dY3D5m-52"))
        self.addBlock(ModuloBlock("b4nyJ0-0gb9Xj1dY3D5m-60"))
        self.addBlock(ConstantBlock("b4nyJ0-0gb9Xj1dY3D5m-66", value=(2)))
        self.addBlock(TrapezoidFormula("mz41oFtheWdhpwzK8Vbf-37"))
        self.addBlock(ProductBlock("mz41oFtheWdhpwzK8Vbf-49"))

        # Create the Connections
        self.addConnection("delta_t", "mz41oFtheWdhpwzK8Vbf-37", input_port_name='delta_t')
        self.addConnection("delta_t", "mz41oFtheWdhpwzK8Vbf-49", input_port_name='IN1')
        self.addConnection("IN1", "ihgbk0rLZbIN8TCgCPIG-71", input_port_name='IN1')
        self.addConnection("IN1", "b4nyJ0-0gb9Xj1dY3D5m-37", input_port_name='IN1')
        self.addConnection("IN1", "mz41oFtheWdhpwzK8Vbf-37", input_port_name='IN1')
        self.addConnection("IC", "ihgbk0rLZbIN8TCgCPIG-61", input_port_name='IN1')
        self.addConnection("IC", "ihgbk0rLZbIN8TCgCPIG-71", input_port_name='IC')
        self.addConnection("ihgbk0rLZbIN8TCgCPIG-36", "ihgbk0rLZbIN8TCgCPIG-61", output_port_name='OUT1', input_port_name='select')
        self.addConnection("ihgbk0rLZbIN8TCgCPIG-36", "b4nyJ0-0gb9Xj1dY3D5m-60", output_port_name='OUT1', input_port_name='IN1')
        self.addConnection("ihgbk0rLZbIN8TCgCPIG-61", "OUT1", output_port_name='OUT1')
        self.addConnection("ihgbk0rLZbIN8TCgCPIG-61", "b4nyJ0-0gb9Xj1dY3D5m-14", output_port_name='OUT1', input_port_name='IN1')
        self.addConnection("ihgbk0rLZbIN8TCgCPIG-81", "ihgbk0rLZbIN8TCgCPIG-75", output_port_name='OUT1', input_port_name='IC')
        self.addConnection("b4nyJ0-0gb9Xj1dY3D5m-7", "b4nyJ0-0gb9Xj1dY3D5m-14", output_port_name='OUT1', input_port_name='IC')
        self.addConnection("b4nyJ0-0gb9Xj1dY3D5m-14", "b4nyJ0-0gb9Xj1dY3D5m-10", output_port_name='OUT1', input_port_name='IN1')
        self.addConnection("b4nyJ0-0gb9Xj1dY3D5m-14", "b4nyJ0-0gb9Xj1dY3D5m-26", output_port_name='OUT1', input_port_name='IN1')
        self.addConnection("b4nyJ0-0gb9Xj1dY3D5m-22", "b4nyJ0-0gb9Xj1dY3D5m-26", output_port_name='OUT1', input_port_name='IN2')
        self.addConnection("ihgbk0rLZbIN8TCgCPIG-75", "b4nyJ0-0gb9Xj1dY3D5m-37", output_port_name='OUT1', input_port_name='IN3')
        self.addConnection("b4nyJ0-0gb9Xj1dY3D5m-26", "b4nyJ0-0gb9Xj1dY3D5m-45", output_port_name='OUT1', input_port_name='IN1')
        self.addConnection("b4nyJ0-0gb9Xj1dY3D5m-10", "b4nyJ0-0gb9Xj1dY3D5m-52", output_port_name='OUT1', input_port_name='IN1')
        self.addConnection("b4nyJ0-0gb9Xj1dY3D5m-45", "b4nyJ0-0gb9Xj1dY3D5m-52", output_port_name='OUT1', input_port_name='IN2')
        self.addConnection("b4nyJ0-0gb9Xj1dY3D5m-52", "ihgbk0rLZbIN8TCgCPIG-61", output_port_name='OUT1', input_port_name='IN2')
        self.addConnection("b4nyJ0-0gb9Xj1dY3D5m-60", "b4nyJ0-0gb9Xj1dY3D5m-52", output_port_name='OUT1', input_port_name='select')
        self.addConnection("b4nyJ0-0gb9Xj1dY3D5m-66", "b4nyJ0-0gb9Xj1dY3D5m-60", output_port_name='OUT1', input_port_name='IN2')
        self.addConnection("ihgbk0rLZbIN8TCgCPIG-71", "b4nyJ0-0gb9Xj1dY3D5m-37", output_port_name='OUT1', input_port_name='IN2')
        self.addConnection("ihgbk0rLZbIN8TCgCPIG-71", "ihgbk0rLZbIN8TCgCPIG-75", output_port_name='OUT1', input_port_name='IN1')
        self.addConnection("ihgbk0rLZbIN8TCgCPIG-71", "mz41oFtheWdhpwzK8Vbf-37", output_port_name='OUT1', input_port_name='IN2')
        self.addConnection("mz41oFtheWdhpwzK8Vbf-37", "b4nyJ0-0gb9Xj1dY3D5m-10", output_port_name='OUT1', input_port_name='IN2')
        self.addConnection("mz41oFtheWdhpwzK8Vbf-37", "b4nyJ0-0gb9Xj1dY3D5m-22", output_port_name='OUT1', input_port_name='IN1')
        self.addConnection("b4nyJ0-0gb9Xj1dY3D5m-37", "mz41oFtheWdhpwzK8Vbf-49", output_port_name='OUT1', input_port_name='IN2')
        self.addConnection("mz41oFtheWdhpwzK8Vbf-49", "b4nyJ0-0gb9Xj1dY3D5m-45", output_port_name='OUT1', input_port_name='IN2')


class OneThird(CBD):
    def __init__(self, block_name):
        super().__init__(block_name, input_ports=['IN1'], output_ports=['OUT1'])

        # Create the Blocks
        self.addBlock(ConstantBlock("02yunkB4Dpg0Stvmmu_V-8", value=(3)))
        self.addBlock(InverterBlock("02yunkB4Dpg0Stvmmu_V-10"))
        self.addBlock(ProductBlock("02yunkB4Dpg0Stvmmu_V-14"))

        # Create the Connections
        self.addConnection("IN1", "02yunkB4Dpg0Stvmmu_V-14", input_port_name='IN2')
        self.addConnection("02yunkB4Dpg0Stvmmu_V-8", "02yunkB4Dpg0Stvmmu_V-10", output_port_name='OUT1', input_port_name='IN1')
        self.addConnection("02yunkB4Dpg0Stvmmu_V-10", "02yunkB4Dpg0Stvmmu_V-14", output_port_name='OUT1', input_port_name='IN1')
        self.addConnection("02yunkB4Dpg0Stvmmu_V-14", "OUT1", output_port_name='OUT1')


class SimpsonFormula(CBD):
    def __init__(self, block_name):
        super().__init__(block_name, input_ports=['IN1', 'IN2', 'IN3'], output_ports=['OUT1'])

        # Create the Blocks
        self.addBlock(AdderBlock("ihgbk0rLZbIN8TCgCPIG-12"))
        self.addBlock(ConstantBlock("ihgbk0rLZbIN8TCgCPIG-16", value=(4)))
        self.addBlock(ProductBlock("ihgbk0rLZbIN8TCgCPIG-18"))
        self.addBlock(AdderBlock("ihgbk0rLZbIN8TCgCPIG-27"))
        self.addBlock(OneThird("b4nyJ0-0gb9Xj1dY3D5m-69"))

        # Create the Connections
        self.addConnection("IN1", "ihgbk0rLZbIN8TCgCPIG-12", input_port_name='IN1')
        self.addConnection("IN2", "ihgbk0rLZbIN8TCgCPIG-18", input_port_name='IN2')
        self.addConnection("IN3", "ihgbk0rLZbIN8TCgCPIG-27", input_port_name='IN2')
        self.addConnection("ihgbk0rLZbIN8TCgCPIG-16", "ihgbk0rLZbIN8TCgCPIG-18", output_port_name='OUT1', input_port_name='IN1')
        self.addConnection("ihgbk0rLZbIN8TCgCPIG-18", "ihgbk0rLZbIN8TCgCPIG-12", output_port_name='OUT1', input_port_name='IN2')
        self.addConnection("ihgbk0rLZbIN8TCgCPIG-12", "ihgbk0rLZbIN8TCgCPIG-27", output_port_name='OUT1', input_port_name='IN1')
        self.addConnection("ihgbk0rLZbIN8TCgCPIG-27", "b4nyJ0-0gb9Xj1dY3D5m-69", output_port_name='OUT1', input_port_name='IN1')
        self.addConnection("b4nyJ0-0gb9Xj1dY3D5m-69", "OUT1", output_port_name='OUT1')


class TrapezoidFormula(CBD):
    def __init__(self, block_name):
        super().__init__(block_name, input_ports=['IN1', 'IN2', 'delta_t'], output_ports=['OUT1'])

        # Create the Blocks
        self.addBlock(AdderBlock("mz41oFtheWdhpwzK8Vbf-6"))
        self.addBlock(ConstantBlock("mz41oFtheWdhpwzK8Vbf-12", value=(2)))
        self.addBlock(InverterBlock("mz41oFtheWdhpwzK8Vbf-14"))
        self.addBlock(ProductBlock("mz41oFtheWdhpwzK8Vbf-18"))
        self.addBlock(ProductBlock("mz41oFtheWdhpwzK8Vbf-24"))

        # Create the Connections
        self.addConnection("IN1", "mz41oFtheWdhpwzK8Vbf-6", input_port_name='IN1')
        self.addConnection("IN2", "mz41oFtheWdhpwzK8Vbf-6", input_port_name='IN2')
        self.addConnection("delta_t", "mz41oFtheWdhpwzK8Vbf-24", input_port_name='IN2')
        self.addConnection("mz41oFtheWdhpwzK8Vbf-12", "mz41oFtheWdhpwzK8Vbf-14", output_port_name='OUT1', input_port_name='IN1')
        self.addConnection("mz41oFtheWdhpwzK8Vbf-14", "mz41oFtheWdhpwzK8Vbf-18", output_port_name='OUT1', input_port_name='IN1')
        self.addConnection("mz41oFtheWdhpwzK8Vbf-6", "mz41oFtheWdhpwzK8Vbf-18", output_port_name='OUT1', input_port_name='IN2')
        self.addConnection("mz41oFtheWdhpwzK8Vbf-18", "mz41oFtheWdhpwzK8Vbf-24", output_port_name='OUT1', input_port_name='IN1')
        self.addConnection("mz41oFtheWdhpwzK8Vbf-24", "OUT1", output_port_name='OUT1')

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




