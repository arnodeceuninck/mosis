Common Issues and Solutions
===========================
Not all models will simulate flawlessly. Some problems may arise upon the
initialization of the model, or during the simulation itself. Below, the
most common exceptions and/or issues are shown.

AssertionError: Can only add BaseBlock (subclass) instances to a CBD
--------------------------------------------------------------------
This error is thrown whenever you try adding a block using the
:func:`CBD.Core.CBD.addBlock` function if that block does **not** inherit from
the :class:`CBD.Core.BaseBlock` class.

NotImplementedError: BaseBlock has nothing to compute
-----------------------------------------------------
When invalidly inheriting a :class:`CBD.Core.BaseBlock`, this error may occur.
It is a consequence of not overwriting the :func:`CBD.Core.BaseBlock.compute`
method.

ValueError: Specified object/influencer/dependent is not member of this graph
-----------------------------------------------------------------------------
This issue is indicative of an error in the dependency graph construction. Usually,
this is due to an invalid connection between blocks. Make sure to always connect
blocks that have been added to the CBD model. I.e. always call
:func:`CBD.Core.CBD.addBlock` **before** any :func:`CBD.Core.CBD.addConnection`
that includes the same block.

KeyError: 'X'
-------------
This exception occurs if :code:`X` cannot be found. Make sure that :code:`X` is
actually a block or a port in your model.

Cannot solve non-linear algebraic loop.
---------------------------------------
The internal solver of the CBD simulator is a simple `Gaussian-Jordan Linear solver
<https://en.wikipedia.org/wiki/Gaussian_elimination>`_
(see :class:`CBD.solver.GaussianJordanLinearSolver`) that uses row reduction to solve
the algebraic loop. However, if this loop represents a non-linear system, the solver
cannot handle this. Make use of a :class:`CBD.lib.std.DelayBlock` to actively "break"
the loop.

**Hint:** Internally, the :class:`CBD.lib.std.DerivatorBlock` and the
:class:`CBD.lib.std.IntegratorBlock` make use of a :class:`CBD.lib.std.DelayBlock`, hence
they can be used to solve the issue.
