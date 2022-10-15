from .util import enum, hash64
from collections import namedtuple
from copy import deepcopy

InputLink = namedtuple("InputLink", ["block", "output_port"])
Signal = namedtuple("Signal", ["time", "value"])


level = enum(WARNING=1, ERROR=2, FATAL=3)
epsilon = 0.001


class BaseBlock:
    """
    A base class for all types of basic blocks

    Args:
        name (str):             The name of the block. When empty, a :func:`CBD.util.hash64`
                                encoded name of the instance :func:`id` will be used.
        input_ports (iter):     List of input port names (strings).
        output_ports (iter):    List of output port names (strings).
    """
    def __init__(self, name, input_ports, output_ports):
        self.__block_name = hash64(id(self))
        if name != "":
            self.setBlockName(name)

        # The output signals produced by this block is encoded as a dictionary.
        # The key of this dictionary is the name of the output port.
        # Each element of the dictionary contains an ordered list of values.
        self.__signals = dict()
        for output_port in output_ports:
            self.__signals[output_port] = []

        # The input links produced by this block is encoded as a dictionary.
        # The key of this dictionary is the name of the input port.
        # Each element of the dictionary contains
        # a tuple of the block and the output name of the other block.
        self._linksIn = dict()

        # The list of possible input ports
        self.__nameLinks = input_ports
        # In wich CBD the baseblock is situated
        self._parent = None

    def addInputPort(self, name):
        """
        Adds an input port if there is no port with the given name.

        Args:
            name (str): The name of the port.
        """
        if name not in self.__nameLinks:
            self.__nameLinks.append(name)

    def addOutputPort(self, name):
        """
        Adds an output port if there is no port with the given name.

        Args:
            name (str): The name of the port.
        """
        if name not in self.__signals:
            self.__signals[name] = []

    def clone(self):
        """
        (Deep) copies the current block, ignoring all connections or links
        that were set on this block.
        """
        other = deepcopy(self)
        other._linksIn.clear()
        other._parent = None
        return other

    def getBlockName(self):
        """
        Gets the name of the block.
        """
        return self.__block_name

    def setBlockName(self, block_name):
        """
        Sets the name of the block.

        Args:
            block_name (str):   The name.
        """
        self.__block_name = block_name

    def setParent(self, parent):
        """
        Sets the block's parent.

        Args:
            parent (CBD):   The parent of the block.
        """
        self._parent = parent

    def getBlockType(self):
        """
        Gets the type of the block. This is the name of the class.
        """
        return self.__class__.__name__

    def getLinksIn(self):
        """
        Gets the inputs of this block.
        """
        return self._linksIn

    def getInputPortNames(self):
        return self.__nameLinks

    def getOutputNameOfInput(self, inputBlock):
        """
        Gets the name of the output port in the :code:`inputBlock` that is linked to this block.

        Args:
            inputBlock (BaseBlock): The block of which the output port must be obtained.
        """
        return [y for (x, y) in self._linksIn.items() if y.block == inputBlock][0].output_port

    def getInputName(self, inputBlock):
        """
        Gets the names of the inputs that are linked to the :code:`inputBlock`.

        Args:
            inputBlock (BaseBlock): The block that is linked.
        """
        return [x for (x, y) in self._linksIn.items() if y.block == inputBlock]

    def getClock(self):
        """
        Gets the simulation clock. Only works if the block is part of a :class:`CBD` model.
        """
        return self._parent.getClock()

    def appendToSignal(self, value, name_output=None):
        """
        Appends the value to the set of obtained signals and links it to the current simulation
        time.

        Args:
            value (Any):        The value to append.
            name_output (str):  The name of the output port. If not set, or :code:`None`,
                                the value of :code:`OUT1` will be used.
        """
        name_output = "OUT1" if name_output is None else name_output
        assert name_output in self.__signals.keys()
        curIt = len(self.__signals[name_output])
        self.__signals[name_output].append(Signal(self.getClock().getTime(curIt), value))

    def getSignal(self, name_output=None):
        """
        Obtains the set of signals this block has sent over an output port.

        Args:
            name_output (str):  The name of the output port. If not set, or :code:`None`,
                                the value of :code:`OUT1` will be used.
        """
        name_output = "OUT1" if name_output is None else name_output
        assert name_output in self.__signals.keys(), "No such output '%s' in %s" % (name_output, self.getPath())
        return self.__signals[name_output]

    def getSignals(self):
        """
        Obtains all the signals of the block.

        Returns:
            Dictionary of :code:`output port name -> list of signals`.
        """
        return self.__signals

    def clearSignals(self):
        for i in self.__signals.keys():
            self.__signals[i].clear()

    def getDependencies(self, curIteration):
        """
        Helper function to help the creation of the dependency graph.

        Args:
            curIteration (int): The current simulation's iteration, for which
                                the dependency graph must be constructed.
        """
        return [x.block for x in self._linksIn.values()]

    def getBlockConnectedToInput(self, input_port):
        """
        Get the block that is connected to a specific input.

        Args:
            input_port (str):   The name of the input port.
        """
        return self._linksIn[input_port]

    def getInputSignal(self, curIteration=-1, input_port="IN1"):
        """
        Returns the signal sent out by the input block.

        Args:
            curIteration (int):     The iteration at which the signal is obtained.
                                    When :code:`None` or :code:`-1`, the last value
                                    will be used.
            input_port (str):       The name of the input port. If omitted, or when
                                    :code:`None`, the value of :code:`IN1` will be used.
        """
        incoming_block, out_port_name = self._linksIn[input_port]
        return incoming_block.getSignal(out_port_name)[curIteration]

    def getPath(self, sep='.'):
        """Gets the path of the current block.
        This includes the paths from its parents. When the block has no parents
        i.e. when it's the top-level block, the block's name is returned.

        Args:
            sep (str):  The separator to use. Defaults to :code:`.`

        Returns:
            The full path as a string.

        Examples:

            A block called :code:`grandchild`, which is located in the :code:`child` CBD,
            that in its turn is located in this CBD has a path of :code:`child.grandchild`.
        """
        if self._parent is None:
            return self.getBlockName()
        return self._parent.getPath() + sep + self.getBlockName()

    def compute(self, curIteration):
        """
        Computes this block's operation, based on its inputs and store it as an output
        signal.

        Args:
            curIteration (int): The iteration at which we must compute this value.
        """
        raise NotImplementedError("BaseBlock has nothing to compute")

    def linkInput(self, in_block, name_input=None, name_output=None):
        """
        Links the output of the :code:`from_block` to the input of the :code:`to_block`.

        Args:
            in_block (BaseBlock):   The block that must be linked.
            name_input (str):       The name of the input port. When :code:`None` or omitted,
                                    the next input port is used. E.g. if the last port was
                                    :code:`IN1`, the input is assumed to be :code:`IN2`.
            name_output (str):      The name of the output port. Defaults to :code:`OUT1`.
        """
        if name_output is None:
            name_output = "OUT1"
        if name_input is not None:
            assert name_input in self.__nameLinks, "Cannot link blocks, no such input '%s' in %s" % (name_input, self.getPath())
            self._linksIn[name_input] = InputLink(in_block, name_output)
        else:
            i = 1
            while True:
                nextIn = "IN" + str(i)
                if nextIn in self.__nameLinks:
                    if not nextIn in self._linksIn:
                        self._linksIn[nextIn] = InputLink(in_block, name_output)
                        return
                else:
                    exit("There are no open IN inputs left in block %s" % self.getBlockName())
                i += 1

    def __repr__(self):
        return self.getPath() + ":" + self.getBlockType() + "\n"

    def info(self, indent=0):
        """
        Returns a string with the block's details.

        Args:
            indent (int):   The amount of indentation that is required at the
                            start of each line. Defaults to 0.
        """
        idt = "\t" * indent
        repr = idt + self.getPath() + ":" + self.getBlockType() + "\n"
        if len(self._linksIn) == 0:
            repr += idt + "  No incoming connections to IN ports\n"
        else:
            for (key, (in_block, out_port)) in self._linksIn.items():
                repr += idt + "  On input " + key + ": " + in_block.getPath() + ":" + in_block.getBlockType() + "\n"
        return repr

    def _rewind(self):
        """
        Rewinds the CBD model to the previous iteration.

        Danger:
            Normally, this function should only be used by the internal mechanisms
            of the CBD simulator, **not** by a user. Using this function without a
            full understanding of the simulator may result in undefined behaviour.
        """
        for signal in self.getSignals().keys():
            self.__signals[signal].pop()


class InputPortBlock(BaseBlock):
    """
    The input port of a CBD
    """
    def __init__(self, block_name, parent):
        BaseBlock.__init__(self, block_name, [], ["OUT1"])
        self._parent = parent

    def compute(self, curIteration):
        self.appendToSignal(self._parent.getInputSignal(curIteration, self.getBlockName()).value)

    @property
    def parent(self):
        return self._parent


class OutputPortBlock(BaseBlock):
    """
    The output port of a CBD
    """
    def __init__(self, block_name, parent):
        BaseBlock.__init__(self, block_name, ["IN1"], ["OUT1"])
        self._parent = parent

    def compute(self, curIteration):
        self.appendToSignal(self.getInputSignal(curIteration, "IN1").value)

    @property
    def parent(self):
        return self._parent


class WireBlock(BaseBlock):
    """
    When a CBD gets flattened, the port blocks will be replaced by a wire block
    """
    def __init__(self, block_name):
        BaseBlock.__init__(self, block_name, ["IN1"], ["OUT1"])

    def compute(self, curIteration):
        self.appendToSignal(self.getInputSignal(curIteration, "IN1").value)


class SequenceBlock(BaseBlock):
    """
    A simple Sequence block: block initializes signal input with given sequence
    Use only for the tests please
    """
    def __init__(self, block_name, sequence):
        BaseBlock.__init__(self, block_name, [], ["OUT1"])
        self.__sequence = sequence

    def compute(self, curIteration):
        if len(self.__sequence) <= curIteration:
            raise ValueError("Sequence is not long enough")
        self.appendToSignal(self.__sequence[curIteration])


class CBD(BaseBlock):
    """
    The CBD class, contains an entire Causal Block Diagram
    Call the run function to simulate the model.
    """
    def __init__(self, block_name, input_ports=None, output_ports=None):
        input_ports = input_ports if input_ports is not None else []
        output_ports = output_ports if output_ports is not None else []
        BaseBlock.__init__(self, block_name, input_ports, output_ports)
        # The blocks in the CBD will be stored both
        # -as an ordered list __blocks and
        # -as a dictionary __blocksDict with the blocknames as keys
        # for fast name-based retrieval and to ensure block names are unique within a single CBD
        self.__blocks = []
        self.__blocksDict = {}
        self.__clock = None

        for input_port in input_ports:
            self.addBlock(InputPortBlock(input_port, self))

        for output_port in output_ports:
            self.addBlock(OutputPortBlock(output_port, self))

        # TODO: automatically add Clock?

    def addInputPort(self, name):
        BaseBlock.addInputPort(self, name)
        self.addBlock(InputPortBlock(name, self))

    def addOutputPort(self, name):
        BaseBlock.addOutputPort(self, name)
        self.addBlock(OutputPortBlock(name, self))

    def clone(self):
        other = BaseBlock.clone(self)
        # other.setClock(deepcopy(self.getClock()))
        other.clearBlocks()
        for block in self.getBlocks():
            other.addBlock(block.clone())
        for block in self.getBlocks():
            for name_input, link in block.getLinksIn().items():
                other.addConnection(link.block.getBlockName(), block.getBlockName(), name_input, link.output_port)
        return other

    def getTopCBD(self):
        """
        Finds the highest-level :class:`CBD` instance.
        """
        return self if self._parent is None else self._parent.getTopCBD()

    def flatten(self, parent=None, ignore=None, psep="."):
        """
        Flatten the CBD parent and call flatten recursively for CBD's in this CBD

        Args:
            parent (CBD):   Reference to the parent. Used for the recursive call.
                            Defaults to :code:`None`. Users should ignore this parameter.
            ignore (iter):  Block class names to ignore in the flattening. When :code:`None`,
                            no blocks are ignored. Defaults to :code:`None`.
            psep (str):     The path separator to use. Defaults to :code:`"."`.
        """
        if ignore is None:
            ignore = []
        blocksToRemove = []
        blocksToAdd = []

        for childBlock in self.__blocks:
            if isinstance(childBlock, InputPortBlock):
                # Replace InputPortBlock with WireBlock
                wb = WireBlock(childBlock.getBlockName())

                # Replace links going out of inputportblock
                blocksToRemove.append(childBlock)
                blocksToAdd.append(wb)

                if parent is not None:
                    for b in self.getBlocks():
                        for input_name, output_port in [(x, y.output_port) for (x, y) in b._linksIn.items() if y.block == childBlock]:
                            b._linksIn[input_name] = InputLink(wb, "OUT1")

                    input = self._linksIn[wb.getBlockName()]
                    parent.addConnection(input.block, wb, output_port_name=input.output_port)
            elif isinstance(childBlock, OutputPortBlock):
                # Replace OutputPortBlock with WireBlock
                wb = WireBlock(childBlock.getBlockName())
                blocksToRemove.append(childBlock)
                blocksToAdd.append(wb)

                for (x, y) in childBlock._linksIn.items():
                    wb._linksIn[x] = y

                if parent is not None:
                    # blocks connected to this output
                    for b in parent.__blocks:
                        for (portname, input) in b._linksIn.items():
                            if input.block == self and input.output_port == wb.getBlockName():
                                b._linksIn[portname] = InputLink(wb, "OUT1")

        for childBlock in self.__blocks:
            if isinstance(childBlock, CBD) and not isinstance(childBlock, tuple(ignore)):
                childBlock.flatten(self, ignore, psep)
                blocksToRemove.append(childBlock)

        # Delete blocksToRemove
        for block in blocksToRemove:
            self.removeBlock(block)

        for b in blocksToAdd:
            self.addBlock(b)

        if parent is not None:
            # Add all components to parent, do not copy blocksToRemove
            for block in [b for b in self.__blocks if not b in blocksToRemove]:
                block.setBlockName(self.getBlockName() + psep + block.getBlockName())
                parent.addBlock(block)

    def getBlocks(self):
        """
        Gets the list of blocks.
        """
        return self.__blocks

    def getBlockByName(self, name):
        """
        Gets a block by its name.

        Args:
            name (str): The block's name
        """
        return self.__blocksDict[name]

    def hasBlock(self, name):
        """
        Checks if the CBD has a block with the given name.

        Args:
            name (str): The name of the block to check.
        """
        return name in self.__blocksDict

    def clearBlocks(self):
        """
        Clears the block information. Calling this function will
        "empty" the current block.
        """
        self.__blocks.clear()
        self.__blocksDict.clear()

    def getClock(self):
        """
        Gets the current simulation clock.
        This will always be the block of the highest-level :class:`CBD`.
        """
        return self.__clock if self._parent is None else self._parent.getClock()

    def addFixedRateClock(self, prefix="clock", delta_t=1.0, start_time=0.0):
        """
        Adds a clock with a fixed rate.

        Two blocks are added to the simulation: a :class:`Clock` and a
        :class:`ConstantBlock` for the rate. Their names will be :code:`<prefix>-<what>`,
        where :code:`<what>` identifies the purpose of the block (which is one of
        :code:`clock` or :code:`delta`).

        Args:
            prefix (str):       The prefix for the names of the blocks.
                                Defaults to :code:`"clock"`.
            delta_t (float):    The interval when the clock must tick.
                                Defaults to 1.
            start_time (float): The time at which the simulation starts.
                                Defaults to 0.

        Note:
            Whenever this function is not called, upon simulation start a clock
            is added with the default values.
        """
        self.addBlock(Clock("%s-clock" % prefix, start_time))
        self.addBlock(ConstantBlock("%s-delta" % prefix, delta_t))
        self.addConnection("%s-delta" % prefix, "%s-clock" % prefix, input_port_name='h')

    def addBlock(self, block):
        """
        Add a block to the CBD model
        """
        assert isinstance(block, BaseBlock), "Can only add BaseBlock (subclass) instances to a CBD"
        block.setParent(self)

        if block.getBlockName() not in self.__blocksDict:
            self.__blocks.append(block)
            self.__blocksDict[block.getBlockName()] = block
            if isinstance(block, Clock):
                self.__clock = block
        else:
            print("Warning: did not add this block as it has the same name %s as an already existing block" % block.getBlockName())

    def removeBlock(self, block):
        """
        Removes a block from the :class:`CBD`.

        Args:
            block (BaseBlock):  The block to remove.
        """
        assert isinstance(block, BaseBlock), "Can only delete BaseBlock (subclass) instances to a CBD"

        if block.getBlockName() in self.__blocksDict:
            self.__blocks.remove(self.__blocksDict[block.getBlockName()])
            del self.__blocksDict[block.getBlockName()]
        else:
            exit("Warning: did not remove this block %s as it was not found" % block.getBlockName())

    def addConnection(self, from_block, to_block, input_port_name=None, output_port_name=None):
        """
        Adds a connection between :code:`from_block` with :code:`input_port_name` to
        :code:`to_block` with :code:`outport_port_name`.

        Args:
            from_block (BaseBlock): The block to start the connection from.
            to_block (BaseBlock):   The target block of the connection.
            input_port_name (str):  The name of the input port. When :code:`None` or unset,
                                    the next port is used. E.g. when called after :code:`IN1`
                                    is already set, :code:`IN2` will be used.
            output_port_name (str): The name of the output port. When not set or :code:`None`,
                                    :code:`OUT1` will be used.

        See Also:
            :func:`BaseBlock.linkInput`
        """
        if type(from_block) == str:
            from_block = self.getBlockByName(from_block)
        if type(to_block) == str:
            to_block = self.getBlockByName(to_block)
        to_block.linkInput(from_block, input_port_name, output_port_name)

    def findBlock(self, path, sep='.'):
        """Obtain a block in a submodel of this CBD.

        Args:
            path (str): The path of the block to find. Empty string for the current block,
                        :code:`child.grandchild` for the block called code:`grandchild`,
                        which is located in the :code:`child` CBD that is located in this CBD.
            sep (str):  The path separator to use. Defaults to :code:`.`

        Returns:
            The block that corresponds to the given path.

            .. note::   The block that will be returned has a different path than the path provided
                        in this function call. This is because this function assumes you already have
                        a path to the CBD you call it on. For instance, if this CBD contains a child
                        called :code:`child`, which has a :code:`grandchild` block in its turn, calling
                        findBlock on the :class:`child` to locate the :code:`grandchild` only needs
                        :code:`grandchild` to be passed as a path. If the function is called on the
                        current CBD block instead, :code:`child.grandchild` is required to obtain the
                        same block.
        """
        if path == '':
            return self, self.getPath()
        cur = self
        for p in path.split(sep):
            if p in cur.__blocksDict:
                cur = cur.getBlockByName(p)
            else:
                raise ValueError("Cannot find block '{}' in '{}'.".format(p, cur.getPath()))
        return cur, path

    def __repr__(self):
        return "CBD <%s>" % self.getBlockName()

    def info(self, indent=0):
        det = ("\t" * indent) + BaseBlock.info(self, indent) + "\n"
        for block in self.getBlocks():
            det += block.info(indent + 1)
        return det

    def dump(self):
        """
        Dumps the model information to the console.
        """
        print("=========== Start of Model Dump ===========")
        print(self)
        print("=========== End of Model Dump =============\n")

    def dumpSignals(self):
        """
        Dumps the signal inromation to the console.
        """
        print("=========== Start of Signals Dump ===========")
        for block in self.getBlocks():
            print("%s:%s" % (block.getBlockName(), block.getBlockType()))
            print(str(block.getSignal()) + "\n")
        print("=========== End of Signals Dump =============\n")

    def getSignal(self, name_output=None):
        name_output = "OUT1" if name_output is None else name_output
        portBlock = self.getBlockByName(name_output)
        assert portBlock is not None
        return portBlock.getSignal("OUT1")

    def getSignals(self):
        res = {}
        for port in super().getSignals().keys():
            res[port] = self.getSignal(port)
        return res

    def clearSignals(self):
        for block in self.getBlocks():
            block.clearSignals()

    def compute(self, curIteration):
        pass

    def _rewind(self):
        for block in self.getBlocks():
            block._rewind()

    def getUniqueBlockName(self, prefix="", hash=False):
        """
        Fetches a name that is unique within the given model.
        This name is in the form :code:`<prefix><suffix>`. The suffix is the
        string representation of a unique identifier. This identifier is
        continuously increased and tested.

        Args:
            prefix (str):   The prefix of the name to fetch. When a valid
                            name by itself, this will be returned, ignoring
                            any suffix. Defaults to the empty string.
            hash (bool):    When :code:`True`, the current object id will be
                            used as a starting point for the identifier.
                            Additionally, the :func:`CBD.util.hash64` function
                            will be used for the suffix representation. When
                            :code:`False`, the identifier will start at 1 and
                            no hashing will be done. Defaults to :code:`False`.
        """
        names = set([x.getBlockName() for x in self.getBlocks()])
        uid = 1
        if hash:
            uid = id(self)
        name = prefix
        while name in names:
            suffix = str(uid)
            if hash:
                suffix = hash64(uid)
            name = prefix + suffix
            uid += 1
        return name


from .lib.std import Clock, ConstantBlock
