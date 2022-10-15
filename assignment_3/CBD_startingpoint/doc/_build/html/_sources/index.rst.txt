.. Copyright the Modelling, Simulation and Design Lab (MSDL)
      http://msdl.cs.mcgill.ca/

.. drawio2cbd documentation master file, created by
   sphinx-quickstart on Mon Oct 19 12:31:01 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to the CBD Simulator's Documentation!
=============================================

This package contains a CBD modelling and simulation framework, which can be used
to model complex systems of equations.

:Authors:
  * Marc Provost
  * Hans Vangheluwe
  * Joachim Denil
  * Claudio Gomes
  * Randy Paredis

:Python Version: :code:`>= 2.7` or :code:`>= 3.2`


.. note::
    This documentation is a mere description of the CBD modelling framework
    as it has been written in Python. When interested in creating visual
    models in this framework, take a look at
    `the DrawioConvert project <https://msdl.uantwerpen.be/git/rparedis/DrawioConvert>`_.

.. toctree::
    :maxdepth: 2
    :caption: Setup

    install
    running
    changelog
    issues

.. toctree::
    :maxdepth: 2
    :caption: Simple Examples

    examples/SinGen
    examples/EvenNumberGen
    examples/Fibonacci
    examples/LCG

.. toctree::
    :maxdepth: 2
    :caption: Advanced Examples

    examples/RealTime
    examples/LivePlot
    examples/Dashboard
    examples/ContinuousTime

.. toctree::
    :maxdepth: 3
    :caption: Internal Documentation

    CBD
