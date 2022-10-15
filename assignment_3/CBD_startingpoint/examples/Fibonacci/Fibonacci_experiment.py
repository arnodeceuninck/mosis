#!/usr/bin/python3
# This file was automatically generated from drawio2cbd with the command:
#   /home/red/git/DrawioConvert/__main__.py Fibonacci.xml -F CBD -e FibonacciGen -gvaf

from CBD.lib.endpoints import SignalCollectorBlock
from Fibonacci_simple import *
from Fibonacci_complex import *
from CBD.simulator import Simulator
import matplotlib.pyplot as plt


cbd = FibonacciGen("FibonacciGen")

# Run the Simulation
sim = Simulator(cbd)
sim.run(10)

data = cbd.getSignal('OUT1')
t, v = [t for t, _ in data], [v for _, v in data]

print(v)
fig = plt.figure()
ax = fig.subplots()
ax.set_title("Fibonacci Numbers")
ax.set_xlabel("N")
ax.set_ylabel("Value")
ax.scatter(t, v)
plt.show()
