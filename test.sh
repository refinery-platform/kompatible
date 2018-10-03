#!/usr/bin/env bash
set -o errexit

start() { echo travis_fold':'start:$1; echo $1; }
end() { echo travis_fold':'end:$1; }
die() { set +v; echo "$*" 1>&2 ; sleep 1; exit 1; }
# Race condition truncates logs on Travis: "sleep" might help.
# https://github.com/travis-ci/travis-ci/issues/6018

start preflight

docker info
docker info | grep 'Operating System' \
    || die 'Make sure Docker is running'

kubectl cluster-info
# TODO: What is a good check for kubernetes?

docker ps -a
[ -z "`docker ps -qa`" ] \
    || die 'Kill containers before running tests: "docker ps -qa | xargs docker stop | xargs docker rm"'

kubectl get pods
[ -z "`kubectl get pods`" ] \
    || die 'Kill pods before running tests: "kubectl delete pods --all"'  # Can take a while...

end preflight

start doctest
python doctest_runner.py --docker
python doctest_runner.py --kompatible
end doctest

#start coverage
#echo; echo 'Tests:'
#COVERAGE_FILE=.coverage.test coverage report
#echo; echo 'Doctests:'
#COVERAGE_FILE=.coverage.doctest coverage report
#echo; echo 'Union:'
#coverage combine
#coverage report --fail-under 100
#end coverage

start docker
docker system df
# TODO: Make assertions about the disk usage we would expect to see.
end docker

start format
flake8 --exclude build . || die "Run 'autopep8 --in-place -r .'"
end format

start isort
isort --recursive . --verbose --check-only || die "See ERRORs: Run 'isort --recursive .'"
end isort

start wheel
python setup.py sdist bdist_wheel
end wheel