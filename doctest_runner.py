import argparse
import doctest
from re import sub

IGNORE_DOCKER = doctest.register_optionflag('IGNORE_DOCKER')
IGNORE_KOMPATIBLE = doctest.register_optionflag('IGNORE_KOMPATIBLE')


class UnfussyOutputChecker(doctest.OutputChecker):
    def check_output(self, want, got, optionflags):
        # Ignore differences in strings between 2 and 3:
        got = sub(r"\bu'", "'", got)  # python 2
        got = sub(r"\bb'", "'", got)  # python 3

        # Allow different assertions for docker and kompatible:
        if optionflags & IGNORE_KOMPATIBLE:
            want = sub(r'.+# kompatible\s+', '', want)
        if optionflags & IGNORE_DOCKER:
            want = sub(r'.+# docker\s+', '', want)
        want = sub(r'\s+# (docker|kompatible)', '', want)

        # Handle any other optionflags
        return doctest.OutputChecker.check_output(self, want, got, optionflags)


def get_args():
    parser = argparse.ArgumentParser(description='Run doc tests')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--docker', action='store_true')
    group.add_argument('--kompatible', action='store_true')
    return parser.parse_args()


def get_sdk(args):
    if args.docker:
        import docker as sdk
    else:
        import kompatible as sdk
    return sdk


def get_options(args):
    if args.docker:
        return IGNORE_KOMPATIBLE
    else:
        return IGNORE_DOCKER


def main():
    filename = 'README.md'
    with open(filename) as f:
        readme = f.read()

    args = get_args()
    examples = doctest.DocTestParser().get_doctest(
        string=readme, globs={'sdk': get_sdk(args)},
        name=filename, filename=None, lineno=0)

    runner = doctest.DocTestRunner(
        checker=UnfussyOutputChecker(),
        optionflags=get_options(args) | doctest.ELLIPSIS)
    runner.run(examples)
    (failed, attempted) = runner.summarize()
    if failed > 0:
        exit(1)


if __name__ == '__main__':
    main()
