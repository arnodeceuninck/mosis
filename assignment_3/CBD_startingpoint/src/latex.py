from CBD.lib.drawio import *
from CBD.simulator import Simulator
from CBD.converters.latexify import CBD2Latex

DELTA_T = 0.1

dt = 0.0001
epsilon = 0.002
CBDs = [LookUpTable("LookUpTableBlock")]

i = 0
for CBD in CBDs:
    latex = CBD2Latex(CBD, show_steps=True, render_latex=True)
    with open(f"output{i}.tex", "w") as text_file:
        text_file.write(latex.render())
    i += 1
