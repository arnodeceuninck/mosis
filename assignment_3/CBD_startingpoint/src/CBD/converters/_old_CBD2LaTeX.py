"""The LaTeX generator for a given CBD model.

All basic building blocks (from :mod:`CBD.lib.std`) have a
pre-defined latex representation. If this needs to be overwritten,
a :func:`latex()` member function can be added to all blocks to
overwrite the given representation. Blocks for which no LaTeX is
defined will be ignored in the generation.
"""
from CBD.Core import CBD
import re

def latexify(cbd):
	"""Does the actual conversion of a :class:`CBD`.

	Warning:
		This does not work for :class:`BaseBlock` instances.
	"""
	assert isinstance(cbd, CBD)
	ltx = []

	# Create blocks
	created = set()
	for block in cbd.getBlocks():
		if block is not None:
			n = _BASE_LATEX_MAP.get(block.getBlockType(), None)
			if callable(n):
				n = n(block)
			if isinstance(n, str):
				n = n.format(path=block.getPath())
			if hasattr(block, "latex"):
				n = block.latex()
			if n is not None and len(n) > 0:
				created.add(block.getPath())
				ltx.append(n)

	# Create connections
	for block in cbd.getBlocks():
		tp = block.getBlockType()
		path = block.getPath()
		if path not in created: continue
		for k, v in block.getLinksIn().items():
			if tp == "OutputPortBlock":  # Special case
				ltx.append("{path}(t) &=& {vpath}.{v.output_port}(t)".format(path=path, vpath=v.getPath(), v=v))
			elif v.block.getBlockType() == "InputPortBlock":  # Special case
				ltx.append("{path}.{k}(t) &=& {vpath}(t)".format(path=path, vpath=v.getPath(), k=k))
			else:
				ltx.append("{path}.{k}(t) &=& {vpath}.{v.output_port}(t)".format(path=path, vpath=v.getPath(), k=k, v=v))

	lstr = "\\\\\n".join(ltx)
	if cbd._parent is not None:
		return lstr
	path = cbd.getPath()
	lstr = re.sub(r'\b%s\.' % path, '', lstr).replace('\n', '\n\t\t')
	return _sanitize("""
\\documentclass[11pt]{article}
\\begin{document}
Equations for the `$%s$' block:
$$\\left\\{
    \\begin{array}{rcll}
        %s
    \\end{array}
\\right.$$
\\end{document}
""" % (path.replace('_', r'\_'), lstr))


_BASE_LATEX_MAP = {
	'ConstantBlock': lambda block: "{path}.OUT(t) &=& %s" % block.getValue(),
	'NegatorBlock': "{path}.OUT(t) &=& -{path}.IN1(t)",
	'InverterBlock': "{path}.OUT(t) &=& 1 / {path}.IN1(t)",
	'AdderBlock': "{path}.OUT(t) &=& {path}.IN1(t) + {path}.IN2(t)",
	'ProductBlock': "{path}.OUT(t) &=& {path}.IN1(t) * {path}.IN2(t)",
	'ModuloBlock': "{path}.OUT(t) &\equiv& {path}.IN1(t) \mod {path}.IN2(t)",
	'RootBlock': "{path}.OUT(t) &=& {path}.IN1(t)^{{\\frac{{1}}{{{path}.IN2(t)}}}}",
	'AbsBlock': "{path}.OUT1(t) &=& \\vert {path}.IN1(t)\\vert",
	'IntBlock': "{path}.OUT1(t) &=& \\lfloor {path}.IN1(t)\\rfloor",
	'ClampBlock': "{path}.OUT1(t) &=& \\min\\left(\\max\\left({path}.IN1(t), {block.min}\\right), {block.max}\\right)",
	'GenericBlock': lambda block: "{path}.OUT1(t) &=& \\%s\\left({path}.IN1(t)\\right)" % block.getBlockOperator(),
	'MultiplexerBlock': "{path}.OUT1(t) = \\left\\{{\\begin{{array}}{{lcr}}{path}.IN1(t) &\\textrm{{if }}{path}.select(t) == 0\\\\ "
						"{path}.IN2(t) &\\textrm{{otherwise}}\\end{{array}}\\right.",
	'LessThanBlock': "{path}.OUT1(t) &=& \\left\\{{\\begin{{array}}{{lcr}}1 &\\textrm{{if }}{path}.IN1(t) < {path}.IN2(t)\\\\ "
					 "0 &\\textrm{{otherwise}}\\end{{array}}\\right.",
	'EqualsBlock': "{path}.OUT1(t) &=& \\left\\{{\\begin{{array}}{{lcr}}1 &\\textrm{{if }}{path}.IN1(t) = {path}.IN2(t)\\\\ "
				   "0 &\\textrm{{otherwise}}\\end{{array}}\\right.",
	'LessThanOrEqualsBlock': "{path}.OUT1(t) &=& \\left\\{{\\begin{{array}}{{lcr}}1 &\\textrm{{if }}{path}.IN1(t) \\leq {path}.IN2(t)\\\\ "
							 "0 &\\textrm{{otherwise}}\\end{{array}}\\right.",
	'NotBlock': "{path}.OUT1(t) &=& \\left\\{{\\begin{{array}}{{lcr}}1 &\\textrm{{if }}{path}.IN1(t) = 0\\\\ "
				"0 &\\textrm{{otherwise}}\\end{{array}}\\right.",
	'OrBlock': lambda block: "{path}.OUT1(t) &=& %s" % r'\lor '.join(["{path}.IN%d(t)" % (i + 1) for i in range(block.getNumberOfInputs())]),
	'AndBlock': lambda block: "{path}.OUT1(t) &=& %s" % r'\land '.join(["{path}.IN%d(t)" % (i + 1) for i in range(block.getNumberOfInputs())]),
	'DelayBlock': "{path}.OUT1(t) &=& \\left\\{{\\begin{{array}}{{lcr}}{path}.IC(t) &\\textrm{{if }}t = 0\\\\ "
				  "{path}.IN1(t - 1) &\\textrm{{otherwise}}\\end{{array}}\\right.",
	'TimeBlock': "{path}.OUT1(t) &=& t",
	'LoggingBlock': None,

	'AddOneBlock': "{path}.OUT1(t) &=& {path}.IN1(t) + 1",
	'DerivatorBlock': "{path}.OUT1(t) &=& \\frac{{d}}{{dt}}\\left({path}.IN1(t)\\right)",
	'IntegratorBlock': "{path}.OUT1(t) &=& \\int {path}.IN1(t)\\ dt"
}
"""LaTeX base definitions for all base blocks."""

def _sanitize(latex):
	"""Sanitizes the input."""
	return re.sub("_", '\\_', latex)
