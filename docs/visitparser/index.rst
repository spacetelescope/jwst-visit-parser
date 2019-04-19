************
visitparser Documentation
************
Tools for parsing information from JWST visit files.

Functionalities
==========================
* Read JWST .vst files
* Return Visit object that contains all parsed information from the .vst file, i.e. ID, groups, sequences, activities
* Produce summaries of activities in tabular format
* Support for producing reports in text format

Where to Find visitparser
==========================
visitparser is hosted and developed at https://github.com/spacetelescope/jwst-visit-parser


Installation
==================
This package is being developed in a python 3.5 environment.

How to install
**************
visitparser is available via astroconda::

   `conda install jwst-visit-parser`

Alternatively, you can clone the repository::

   `git clone https://github.com/spacetelescope/jwst-dms-edb`

and install visitparser like this::

   `cd visitparser`
   `python setup.py install`
or::

   `pip install .`



User Documentation
==================
Example usage:

Reporting Issues / Contributing
===============================
Do you have feedback and feature requests? Is there something missing you would like to see? Please open a new issue or new pull request at https://github.com/spacetelescope/jwst-visit-parser for bugs, feedback, or new features you would like to see. If there is an issue you would like to work on, please leave a comment and we will be happy to assist. New contributions and contributors are very welcome! This package follows the STScI `Code of Conduct <https://github.com/spacetelescope/visitparser/blob/master/CODE_OF_CONDUCT.md>`_ strives to provide a welcoming community to all of our users and contributors.

Coding and other guidelines
###########################
We strive to adhere to the `STScI Style Guides <https://github.com/spacetelescope/style-guides>`_.

How to make a code contribution
###############################
Please see the guidelines for ``jwql``: `<https://github.com/spacetelescope/jwql>`_


Reference API
=============
.. toctree::
   :maxdepth: 1

   parser.rst
