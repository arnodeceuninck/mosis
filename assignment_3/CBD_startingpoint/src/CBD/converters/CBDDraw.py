"""
Useful drawing function to easily draw a CBD model in Graphviz.
"""
import re
from CBD.Core import CBD, InputPortBlock, OutputPortBlock
from CBD.lib.std import *
from CBD.util import hash64
import sys

def draw(cbd, filename, colors=None):
	"""
	Output :class:`CBD` as a graphviz script to filename.

	Warning:
		This function may be removed in the future as DrawIO becomes more important.

	Note:
		The resulting Graphviz file might look "clunky" and messy when rendering with
		the standard dot engine. The :code:`neato`, :code:`twopi` and :code:`circo`
		engines might provide a cleaner and more readable result.

	Args:
		cbd (CBD):      The :class:`CBD` to draw.
		filename (str): The name of the dot-file.
		colors (dict):  An optional dictionary of :code:`blockname -> color`.
	"""
	# f = sys.stdout
	f = open(filename, "w")
	write = lambda s: f.write(s)

	write("""// CBD model of the {n} block
// Created with CBD.converters.CBDDraw
digraph model {{
 splines=ortho;
 label=<<B>{n} ({t})</B>>;
 labelloc=\"t\";
 fontsize=20;
""".format(n=cbd.getPath(), t=cbd.getBlockType()))

	if colors is None:
		colors = {}

	def writeBlock(block):
		"""
		Writes a block to graphviz.

		Args:
			block:  The block to write.
		"""
		if isinstance(block, ConstantBlock):
			label = " {}\\n({})\\n{}".format(block.getBlockType(), block.getBlockName(), block.getValue())
		elif isinstance(block, GenericBlock):
			label = " {}\\n({})\\n{}".format(block.getBlockType(), block.getBlockName(), block.getBlockOperator())
		elif isinstance(block, ClampBlock) and block._use_const:
			label = " {}\\n({})\\n[{}, {}]".format(block.getBlockType(), block.getBlockName(), block.min, block.max)
		elif isinstance(block, (InputPortBlock, OutputPortBlock)):
			label = block.getBlockName()
		else:
			label = block.getBlockType() + "\\n(" + block.getBlockName() + ")"

		shape = "box"
		if isinstance(block, CBD):
			shape="Msquare"
		elif isinstance(block, ConstantBlock):
			shape="ellipse"
		elif isinstance(block, (InputPortBlock, OutputPortBlock)):
			shape="none"

		col = ""
		if block.getBlockName() in colors:
			col = ", color=\"{0}\", fontcolor=\"{0}\"".format(colors[block.getBlockName()])

		write(" {b} [label=\"{lbl}\", shape={shape}{col}];\n".format(b=nodeName(block),
			lbl=label,
			shape=shape,
			col=col))

	def nodeName(block):
		return "node_%d" % id(block)

	for block in cbd.getBlocks():
		writeBlock(block)
		# conn = set()
		for (name, other) in block.getLinksIn().items():
			op = other.output_port
			i = "inter_%d_%s" % (id(other.block), op)
			# conn.add(i)
			if isinstance(block, OutputPortBlock):
				name = ""
			write(" {i} -> {b} [headlabel=\"{inp}\", arrowhead=\"normal\", arrowtail=\"none\", dir=both];\n".format(i=i, b=nodeName(block), inp=name))
		for op in block.getSignals().keys():
			if block.getBlockType() == "OutputPortBlock": continue
			i = "inter_%d_%s" % (id(block), op)
			# if i not in conn: continue
			write(" {i} [shape=point, width=0.01, height=0.01];\n".format(i=i))
			if isinstance(block, InputPortBlock):
				op = ""
			write(" {a} -> {i} [taillabel=\"{out}\", arrowtail=\"invempty\", arrowhead=\"none\", dir=both];\n"\
			      .format(i=i, a=nodeName(block), out=op))

	write("\n}")
	f.close()
