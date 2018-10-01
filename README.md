# kompatible

This package exposes a subset of the
[Kubernetes Python Client](https://github.com/kubernetes-client/python/)
with an interface which matches that of the
[Docker SDK for Python](https://docker-py.readthedocs.io/en/stable/).

## Examples

First, checkout this project, and install dependencies:
`pip install -r requirements-dev.txt`.
Then, make sure you have installed and started
[Docker](https://docs.docker.com/docker-for-mac/install/)
and [Minikube](https://kubernetes.io/docs/tutorials/hello-minikube/#create-a-minikube-cluster)

With those tools in place, the following lines will produce the same output,
regardless of the underlying technology. Either `import docker as sdk`
or `import kompatible as sdk` and then

```
>>> client = sdk.from_env()
>>> client.containers.run("alpine", "echo hello world")
b'hello world\n'

```