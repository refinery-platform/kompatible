import argparse
import doctest

import docker
import kompatible

# Wrapper for the built-in doctest to let us specify the value for globals.

parser = argparse.ArgumentParser(description='Run doc tests')
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument('--docker', action='store_true')
group.add_argument('--kompatible', action='store_true')

args = parser.parse_args()
if args.docker:
    sdk = docker
else:
    sdk = kompatible

doctest.testfile('README.md', globs={'sdk': sdk})


