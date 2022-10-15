# CBD Simulator Framework
```
 Copyright the Modelling, Simulation and Design Lab (MSDL)
           http://msdl.cs.mcgill.ca/

 Author(s): Marc Provost
            Hans Vangheluwe
            Joachim Denil
            Claudio Gomes
            Randy Paredis
  
 Purpose: simulates CBD models in Python.

 Requires Python version >= 2.7 or >= 3.6
```
### Installation and Updates
The simulator can easily be installed with one of the following commands, from
the `src` directory (one of the following options suffices).
```
# BUILDING:
python setup.py install --user

# UPDATING:
python -m pip install .
```

Note that these commands assume `python` and `pip` refer to either Python 2 or
Python 3, depending on your system.

_**Note:** Some editors allow you to "mark" a directory as a source root. Use
this option in your favorite IDE to use the library in a project without the
need for installing it. Alternatively, the `src` directory could also be added
to the `PYTHONPATH` variable._

To update your version to the newest simulator version, obtain the latest
version from the repository and run one of the above commands once more.

### Documentation
Take a look at the documentation (in the `doc/` folder) for more details
on this framework. This includes detailed API descriptions, use cases and
examples (both simple and complex).

_The HTML-version of the documentation can be built from within the `doc/`
folder with the `make html` command._

