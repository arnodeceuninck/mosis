#!/usr/bin/python3
# This file was automatically generated from drawio2cbd with the command:
#   C:/Users/dogukan/Desktop/UA/2021-2022/mosis/assignment_3/DrawioConvert/__main__.py -F CBD -e LookUpTableBlock -sSrgv LookUpTableBlock.drawio.xml -E delta=0.1

from LookUpTableBlock import *
from CBD.simulator import Simulator

DELTA_T = 0.1

cbd = LookUpTableBlock("LookUpTableBlock")

# Run the Simulation
sim = Simulator(cbd)
sim.setDeltaT(DELTA_T)
sim.run(10)

# TODO: Process Your Simulation Results