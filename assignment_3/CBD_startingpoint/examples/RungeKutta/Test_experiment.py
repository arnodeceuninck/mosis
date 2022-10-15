#!/usr/bin/python3
# This file was automatically generated from drawio2cbd with the command:
#   /home/red/git/DrawioConvert/__main__.py Test.drawio -e Test -Ssfargv -F CBD -E delta=0.1

from Test import *
import numpy as np
from CBD.simulator import Simulator

DELTA_T = 0.1

cbd = Test("Test")

# Run the Simulation
sim = Simulator(cbd)
sim.setDeltaT(DELTA_T)
sim.run(1.4)

s = cbd.getSignal("y")
L = len(s)

print("+------------+------------+------------+------------+")
print("|    TIME    |    VALUE   |    TAN T   |    ERROR   |")
print("+------------+------------+------------+------------+")
for i in range(L):
	t, v = s[i]
	a = np.tan(t)
	e = a - v
	print(f"| {t:10.7f} | {v:10.7f} | {a:10.7f} | {e:10.7f} |")
print("+------------+------------+------------+------------+")
