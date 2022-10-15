Live Plotting of Data During the Simulation
===========================================
During a (realtime) simulation, often you would like to show some data that's being sent over a
certain connection. This can be intermediary data (i.e. the individual components of a computation),
system data (battery life, sensor information...) or output information (results, actuator inputs...).

Luckily, the CBD framework provides this functionality in a clean and efficient manner.

To allow for "live" plotting of data, make use of the :class:`CBD.realtime.plotting.PlotManager` class,
which is a wrapper for tracking multiple realtime plots. Internally, it will keep track of multiple
:class:`CBD.realtime.plotting.PlotHandler` instances to reduce code-overhead.

.. code-block:: python

    from CBD.realtime.plotting import PlotManager, ScatterPlot

    manager = PlotManager()

    # Register a scatter plot handler with name "myHandler", which listens to
    #   the data of the block "myBlock".
    manager.register("myHandler", MyBlock('myBlock'), figure, ScatterPlot())

Notice you also need a block that stores the data. For plotting a single signal, it's best to use the
:class:`CBD.lib.endpoints.SignalCollectorBlock`. Alternatively, to plot XY-pairs, the
:class:`CBD.lib.endpoints.PositionCollectorBlock` can be used.

Example Model
-------------
The examples below show how you can display a live plot for the :doc:`SinGen`, plotted in realtime.
The output of this block is removed and changed to a :code:`SignalCollectorBlock`:

.. code-block:: python

    from CBD.Core import CBD
    from CBD.lib.std import TimeBlock, GenericBlock
    from CBD.lib.endpoints import SignalCollectorBlock

    class SinGen(CBD):
        def __init__(self, name="SinGen"):
            CBD.__init__(self, name, input_ports=[], output_ports=[])

            # Create the blocks
            self.addBlock(TimeBlock("time"))
            self.addBlock(GenericBlock("sin", block_operator="sin"))
            self.addBlock(SignalCollectorBlock("collector"))

            # Connect the blocks
            self.addConnection("time", "sin")
            self.addConnection("sin", "collector")

    sinGen = SinGen("SinGen")

Using MatPlotLib
----------------
The most common plotting framework for Python is `MatPlotLib <https://matplotlib.org/>`_. It provides
a lot of additional features and functionalities, but we will keep it simple. For more complexity, please
refer to their documentation.

.. note::
    While there are other plotting frameworks, `MatPlotLib` is by far the easiest to get live plotting
    to work.

Default
^^^^^^^
If we're not concerned about a window manager in our system, we can easily make use of  `MatPlotLib`'s
builtin plotting window.

.. code-block:: python

    from CBD.realtime.plotting import PlotManager, LinePlot, follow
    from CBD.simulator import Simulator
    import matplotlib.pyplot as plt

    fig = plt.figure(figsize=(5, 5), dpi=100)
    ax = fig.add_subplot(111)
    ax.set_ylim((-1, 1))    # The sine wave never exceeds this range

    manager = PlotManager()
    manager.register("sin", sinGen.findBlock('collector')[0], (fig, ax), LinePlot(color='red'))
    manager.connect('sin', 'update_event', lambda d, axis=ax: axis.set_xlim(follow(d[0], 10.0, lower_bound=0.0)))

    sim = Simulator(sinGen)
    sim.setRealTime()
    sim.setDeltaT(0.1)
    sim.run(20.0)

    plt.show()

.. figure:: ../_figures/sine-wave-mpl.gif
    :width: 400

Seaborn
^^^^^^^
`Seaborn <https://seaborn.pydata.org/>`_ is a data visualization library, built on top of `MatPlotLib`.
Hence, it can be easily integrated and used for plotting live data. It can simply be used by providing
the :code:`PlotManager`'s constructor with a backend argument:

.. code-block:: python

    manager = PlotManager(Backend.SNS)

That's it. To change the theme to a `Seaborn` theme, you can either
`use a MatPlotLib theme <https://matplotlib.org/stable/gallery/style_sheets/style_sheets_reference.html>`_ theme,
or place the following code before the creation of the figure (see also
`Seaborn's documentation <https://seaborn.pydata.org/generated/seaborn.set_theme.html#seaborn.set_theme>`_ on
this topic):

.. code-block:: python

    import seaborn as sns
    sns.set_theme(style="darkgrid")  # or any of darkgrid, whitegrid, dark, white, ticks

Jupyter Notebook
^^^^^^^^^^^^^^^^
These days, `Jupyter Notebooks <https://jupyter.org/>`_ are the most common way to collect experiments.
Luckily, the :class:`CBD.realtime.plotting.PlotManager` can work with them without too much overhead. In fact,
all that's required is setting the magic function :code:`%matplotlib` **before** creating the plot. That's it!

However, a small caveat is the fact that a :code:`notebook` stays alive after the simulation finishes. This
means the :code:`PlotManager` keeps polling for data. To stop this, connect a signal that terminates this
polling to the simulator **before** starting the simulation:

.. code-block:: python

    # Kills all polling requests and closes the plots
    sim.connect("finished", manager.terminate)

    # Kills all polling requests, but keeps plots alive
    sim.connect("finished", manager.stop)

Also take a look at the :code:`examples/notebook` folder for more info.

TkInter
^^^^^^^
Now, as mentioned in :doc:`RealTime`, there is also a :code:`TkInter` platform to run the realtime
simulation on. This can be useful for creating graphical user interfaces (GUIs). Sometimes, such a
GUI might be in need of a plot of the data. See also the :doc:`Dashboard` example for a more complex
variation.

.. code-block:: python

    from CBD.realtime.plotting import PlotManager, LinePlot, follow
    from CBD.simulator import Simulator

    import tkinter as tk
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

    fig = plt.figure(figsize=(5, 5), dpi=100)
    ax = fig.add_subplot(111)
    ax.set_ylim((-1, 1))    # The sine wave never exceeds this range

    root = tk.Tk()

    # Create a canvas to draw the plot on
    canvas = FigureCanvasTkAgg(fig, master=root)  # A Tk DrawingArea
    canvas.draw()
    canvas.get_tk_widget().grid(column=1, row=1)

    manager = PlotManager()
    manager.register("sin", sinGen.findBlock('collector')[0], (fig, ax), LinePlot(color='red'))
    manager.connect('sin', 'update_event', lambda d, axis=ax: axis.set_xlim(follow(d[0], 10.0, lower_bound=0.0)))

    sim = Simulator(sinGen)
    sim.setRealTime()
    sim.setRealTimePlatformTk(root)
    sim.setDeltaT(0.1)
    sim.run(20.0)

    root.mainloop()

The plot will look exactly like the one for the default platform, except that it is inside a :code:`TkInter` window
now.

Using Bokeh
-----------
As an alternative for `MatPlotLib`, `Bokeh <https://docs.bokeh.org/en/latest/index.html>`_ kan be used. However, as
you will see, this will require a little bit more "managing" code.

.. attention::
    While functional for the most part, live plotting using `Bokeh` is still in beta. Not all features will work
    as expected.

.. warning::
    In order to get this plotting framework to show live plots, you need to start a `Bokeh` server via the command:

    .. code-block:: bash

        bokeh serve

    |

.. code-block:: python

    from CBD.realtime.plotting import PlotManager, Backend, LinePlot, follow
    from CBD.simulator import Simulator

    from bokeh.plotting import figure, curdoc
    from bokeh.client import push_session

    fig = figure(plot_width=500, plot_height=500, y_range=(-1, 1))
    curdoc().add_root(fig)

    # Use the Bokeh Backend
    manager = PlotManager(Backend.BOKEH)
    manager.register("sin", sinGen.findBlock('collector')[0], fig, LinePlot(color='red'))

    def set_xlim(limits):
        lower, upper = limits
        fig.x_range.start = lower
        fig.x_range.end = upper
    manager.connect('sin', 'update_event', lambda d: set_xlim(follow(d[0], 10.0, lower_bound=0.0)))

    session = push_session(curdoc())
    session.show()

    sim = Simulator(sinGen)
    sim.setRealTime()
    sim.setDeltaT(0.1)
    sim.run(20.0)

    # NOTE: currently, there can be 'flickering' of the plot
    import time
    while manager.is_opened():
        session.push()
        time.sleep(0.1)

.. figure:: ../_figures/sine-wave-bokeh.gif
    :width: 400

.. note::
    Currenly, there is a lot of "flickering" of the plot. There has not yet been found a solution
    for this problem. It is presumed that this is a consequence of Bokeh being browser-based.
