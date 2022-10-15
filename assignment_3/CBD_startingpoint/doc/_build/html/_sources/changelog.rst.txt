Changelog
=========

.. code-block:: text

    Version 1.3
        *   Optimized LaTeX renderer. Now, it can also output a stepwise
            trace of the system.
        *   Renamed CBD.py -> Core.py to prevent "from CBD.CBD import CBD"
        +   Added simple equation to CBD converter: eq2CBD.
        *   Extracted simulation clock to custom block.
        -   Removed "old" Variable Step Size simulation system.
        +   Added Runge-Kutta preprocessor with generic Butcher Tableau.
        *   Made tests succeed once again.

    Version 1.2
        +   Added "multi-rate" simulation.
        *   Extracted topological sort to Schedule system.
        +   Added Variable Step Size simulation.
        *   Increased documentation coverage.

    Version 1.1
        +   Created Dashboard Example
        +   Added live plotting
        +   Added "endpoints" and "io" modules

    Version 1.0
        *   Reworked old "single-file" version to better structure.
        +   Added realtime simulation (in the PyPDEVS backends).
        +   Added progress bars.
        *   Made algebraic loop solver flexible and more efficient.
        +   Added docs.
