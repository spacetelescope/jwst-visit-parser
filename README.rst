Python tools for parsing information from JWST visit files
----------------------------------------------------

.. image:: https://travis-ci.org/spacetelescope/jwst-visit-parser.svg?branch=master
    :target: https://travis-ci.org/spacetelescope/jwst-visit-parser

.. image:: https://badge.fury.io/py/visitparser.svg
    :target: https://badge.fury.io/py/visitparser

.. image:: http://img.shields.io/badge/powered%20by-AstroPy-orange.svg?style=flat
    :target: http://www.astropy.org
    :alt: Powered by Astropy Badge

Python interface to the JWST DMS Engineering Database


Installation
------------
From PyPi::

    pip install visitparser


Example usage
-------------

Code::

    from astropy.time import Time
    from visitparser.edb_interface import query_single_mnemonic


Contributing
------------

``visitparser`` is open source

Please see the ``jwql`` contribution guide for how to contribute to visitparser:
https://github.com/spacetelescope/jwql#software-contributions



License
-------

This project is Copyright (c) Space Telescope Science Institute and licensed under
the terms of the Aura license. This package is based upon
the `Astropy package template <https://github.com/astropy/package-template>`_
which is licensed under the BSD 3-clause licence. See the licenses folder for
more information.

