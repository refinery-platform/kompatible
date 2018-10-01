# kompatible

This package exposes a subset of the
[Kubernetes Python Client](https://github.com/kubernetes-client/python/)
with an interface which matches that of the
[Docker SDK for Python](https://docker-py.readthedocs.io/en/stable/).

## Examples

Assuming you have installed both Minikube and Docker, and the corresponding
Python clients, then the following lines will produce the same output,
regardless of the underlying technology. Either `import docker as sdk`
or `import kompatible as sdk` and then

```
>>> client = sdk.from_env()
>>> client.containers.run("alpine", "echo hello world")
b'hello world\n'

```