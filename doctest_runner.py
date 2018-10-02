import argparse
import doctest

parser = argparse.ArgumentParser(description='Run doc tests')
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument('--docker', action='store_true')
group.add_argument('--kompatible', action='store_true')

args = parser.parse_args()
if args.docker:
    import docker as sdk
else:
    import kompatible as sdk

(failure_count, test_count) = doctest.testfile('README.md', globs={'sdk': sdk})
print('{}: fail / total = {} / {}'.format(
    sdk.__name__, failure_count, test_count))
if failure_count > 0:
    exit(1)
