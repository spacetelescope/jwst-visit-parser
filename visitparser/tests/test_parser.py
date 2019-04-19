#! /usr/bin/env python
"""Tests for the ``parser`` module.

Authors
-------

    - Johannes Sahlmann


Use
---

    These tests can be run via the command line (omit the ``-s`` to
    suppress verbose output to ``stdout``):

    ::

        pytest -s test_parser.py


    All tests will pass locally if the VISIT_PARSER_TEST_DATA
    environment variable is set to the directory containing
    the test data set retrieved from STScI.

"""

import glob
import os

import pytest

from ..parser import parse_visit_file

# attempt to retrieve local directory with test data
try:
    test_data_dir = os.environ['VISIT_PARSER_TEST_DATA']
except KeyError:
    test_data_dir = None

environment_variable = pytest.mark.skipif(test_data_dir is None, reason='Environment variable VISIT_PARSER_TEST_DATA not set.')

print(environment_variable)

@environment_variable
def test_parse_visit_file(verbose=True):
    """Parse all .vst files in test data directory."""

    if verbose:
        print()  # new line in pytest screen output

    out_dir = os.path.join(test_data_dir, 'out')
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    for visit_file in glob.glob(os.path.join(test_data_dir, '**/*.vst')):
        visit = parse_visit_file(visit_file)
        if verbose:
            print('Processing {}'.format(visit_file))
            print(visit)
        assert len(visit.script_statements) >= 1
