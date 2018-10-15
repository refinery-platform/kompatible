import argparse
import doctest
from re import sub


class UnfussyOutputChecker(doctest.OutputChecker):
    def check_output(self, want, got, optionflags):
        got = sub(r"\bu'", "'", got)  # python 2
        got = sub(r"\bb'", "'", got)  # python 3
        return super().check_output(want, got, optionflags)


def get_sdk():
    parser = argparse.ArgumentParser(description='Run doc tests')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--docker', action='store_true')
    group.add_argument('--kompatible', action='store_true')

    args = parser.parse_args()
    if args.docker:
        import docker as sdk
    else:
        import kompatible as sdk
    return sdk


def main():
    filename = 'README.md'
    with open(filename) as f:
        readme = f.read()
    examples = doctest.DocTestParser().get_doctest(
        string=readme, globs={'sdk': get_sdk()},
        name=filename, filename=None, lineno=0)

    runner = doctest.DocTestRunner(checker=UnfussyOutputChecker())
    runner.run(examples)
    (failed, attempted) = runner.summarize()
    if failed > 0:
        exit(1)


if __name__ == '__main__':
    main()
