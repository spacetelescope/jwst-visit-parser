This package is archived and no longer maintained
---------------------------------------------------


Python tools for parsing information from JWST visit files
----------------------------------------------------------

.. image:: https://travis-ci.com/spacetelescope/jwst-visit-parser.svg?branch=master
    :target: https://travis-ci.com/spacetelescope/jwst-visit-parser

.. image:: https://readthedocs.org/projects/jwst-visit-parser/badge/?version=latest
    :target: https://jwst-visit-parser.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

.. image:: http://img.shields.io/badge/powered%20by-AstroPy-orange.svg?style=flat
    :target: http://www.astropy.org
    :alt: Powered by Astropy Badge

.. image:: https://zenodo.org/badge/181723904.svg
   :target: https://zenodo.org/badge/latestdoi/181723904

Installation
------------
Install from the repository


Example usage
-------------

Code::

    from visitparser import parser
    visitparser.parser.parse_visit_file('V00783001001.vst')

will return something like::

    Visit  V00783001001:  1 dithers,  2 groups,  14 observation statements. Uses ['NIRISS Internal Flat']


Example visit files
-------------------
Since JWST .vst files are marked as `not public` they cannot be included in this repository. Please download the directory at TBD to your local machine and set the VISIT_PARSER_TEST_DATA environment variable to the location of that folder, e.g. `export VISIT_PARSER_TEST_DATA=your/path`. This will allow you to run the tests and the examples locally.

Examples of .vst files can also be accessed at https://outerspace.stsci.edu/display/OPGS/Observation+Plan+Generation+System#ObservationPlanGenerationSystem-OPProductsforReview

Some usage examples are included in `run_visit_parser.py <https://github.com/spacetelescope/jwst-visit-parser/blob/master/examples/run_visit_parser.py>`_




Citation
--------

If you find this package useful, please consider citing the Zenodo record using the DOI badge above.


License
-------

This project is Copyright (c) Space Telescope Science Institute and licensed under
the terms of the Aura license. This package is based upon
the `Astropy package template <https://github.com/astropy/package-template>`_
which is licensed under the BSD 3-clause licence. See the licenses folder for
more information.

