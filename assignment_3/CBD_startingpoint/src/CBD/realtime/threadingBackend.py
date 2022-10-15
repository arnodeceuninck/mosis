# Copyright 2014 Modelling, Simulation and Design Lab (MSDL) at 
# McGill University and the University of Antwerp (http://msdl.cs.mcgill.ca/)
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from ..util import enum
import threading

class Platform:
    """
    Identifies the platform to use in real-time simulation.
    """
    THREADING = "python"
    """
    Use the default Python threading platform.
    
    See Also:
        :class:`CBD.realtime.threadingPython.ThreadingPython`
    """

    PYTHON    = "python"
    """
    Use the default Python threading platform.
    
    See Also:
        :class:`CBD.realtime.threadingPython.ThreadingPython`
    """

    TKINTER   = "tkinter"
    """
    Use the TkInter backend, to allow GUIs of the simulation.
    
    See Also:
        :class:`CBD.realtime.threadingTkInter.ThreadingTkInter`
    """

    TK        = "tkinter"
    """
    Use the TkInter backend, to allow GUIs of the simulation.
    
    See Also:
        :class:`CBD.realtime.threadingTkInter.ThreadingTkInter`
    """

    GAMELOOP  = "loop"
    """
    Use a gameloop backend, to keep the time yourself.
    
    See Also:
        :class:`CBD.realtime.threadingGameLoop.ThreadingGameLoop`
    """

    LOOP      = "loop"
    """
    Use a gameloop backend, to keep the time yourself.
    
    See Also:
        :class:`CBD.realtime.threadingGameLoop.ThreadingGameLoop`
    """

    GLA      = "loop_alt"
    """
    Use an alternative gameloop backend, to keep the time yourself.
    
    See Also:
        :class:`CBD.realtime.threadingGameLoopAlt.ThreadingGameLoopAlt`
    """



class ThreadingBackend(object):
    """
    Wrapper around the actual threading backend.
    It will also handle interrupts and the passing of them to the calling thread.

    Args:
        subsystem (str):    String specifying the subsystem to use. Must be one of
                            :code:`python`, :code:`tkinter` or :code:`loop` (case-insensitive).
                            The :class:`Platform` class may be used to help identifying
                            the subsystem.
        args (list):        All additional arguments that should be passed to the subsystem's
                            constructor (must be a list). Only used for the :code:`tkinter`
                            subsystem.
    """
    def __init__(self, subsystem, args):
        self.interrupted_value = None
        self.value_lock = threading.Lock()
        if subsystem.lower() == Platform.THREADING:
            from .threadingPython import ThreadingPython
            self.subsystem = ThreadingPython()
        elif subsystem.lower() == Platform.TKINTER:
            from .threadingTkInter import ThreadingTkInter
            self.subsystem = ThreadingTkInter(*args)
        elif subsystem.lower() == Platform.GAMELOOP:
            from .threadingGameLoop import ThreadingGameLoop
            self.subsystem = ThreadingGameLoop()
        elif subsystem.lower() == Platform.GLA:
            from .threadingGameLoopAlt import ThreadingGameLoopAlt
            self.subsystem = ThreadingGameLoopAlt()
        else:
            raise Exception("Realtime subsystem not found: " + str(subsystem))

    def wait(self, time, func):
        """
        A non-blocking call, which will call the :code:`func` parameter after
        :code:`time` seconds. It will use the provided backend to do this.

        :param time: time to wait in seconds, a float is possible
        :param func: the function to call after the time has passed
        """
        self.subsystem.wait(time, func)

    def interrupt(self, value):
        """
        Interrupt a running wait call.

        :param value: the value that interrupts
        """
        self.interrupted_value = value
        self.subsystem.interrupt()

    def setInterrupt(self, value):
        """
        Sets the value of the interrupt. This should not be used manually and is
        only required to prevent the asynchronous combo generator from making
        :func:`interrupt` calls.
        
        :param value: value with which the interrupt variable should be set
        """
        with self.value_lock:
            if self.interrupted_value is None:
                self.interrupted_value = value
                return True
            else:
                # The interrupt was already set, indicating a collision!
                return False

    def getInterrupt(self):
        """
        Return the value of the interrupt and clear it internally.

        :returns: the interrupt
        """
        with self.value_lock:
            val = self.interrupted_value
            self.interrupted_value = None
        return val

    def step(self, time=0.0):
        """
        Perform a step in the backend; only supported for the game loop backend.

        Args:
            time (float):   The current simulation time. Only used if the alternative
                            gameloop backend is used.
        """
        if hasattr(self.subsystem, "time"):
            self.subsystem.step(time)
        else:
            self.subsystem.step()
