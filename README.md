# kompatible

[![PyPI version](https://badge.fury.io/py/kompatible.svg)](https://badge.fury.io/py/kompatible)

This package exposes a subset of the
[Kubernetes Python Client](https://github.com/kubernetes-client/python/)
with an interface which matches that of the
[Docker SDK for Python](https://docker-py.readthedocs.io/en/stable/).

## Examples

First, checkout this project, and install dependencies:
`pip install -r requirements-dev.txt`.
Then, make sure you have installed and started
[Docker](https://docs.docker.com/docker-for-mac/install/)
and/or [Minikube](https://kubernetes.io/docs/tutorials/hello-minikube/#create-a-minikube-cluster)

With those tools in place, either
`import docker as sdk` or `import kompatible as sdk`
and the following examples will work, although in the first case
it's Docker containers starting up,
and in the latter it's Kubernetes pods.

## "Hello World!": Run, list, remove

```python
>>> client = sdk.from_env()

>>> [client.containers.run(
...     "alpine", "echo hello world",
...     name='foobar',
...     labels={'foo': 'bar'})]
[...'hello world\n']

>>> def not_kube(containers):  # Only needed for Docker, on Travis, with k8s started.
...     return [c for c in containers if 'kube' not in c.name]

>>> containers = not_kube(client.containers.list(all=True, filters={}))
>>> [c.name for c in containers]
[...'foobar']
>>> c = containers[0]

>>> c.remove(force=True, v=True)
>>> containers = not_kube(client.containers.list(all=True, filters={}))
>>> assert len(containers) == 0

```

## Container properties

```python
>>> assert c.id
>>> assert c.image
>>> c.labels
{...'foo': ...'bar'}
>>> assert c.short_id
>>> assert c.status

```

## `containers.run` kwargs

```python

```

## Subclients

```python
>>> assert client.api
>>> assert client.containers
>>> assert client.images
>>> assert client.volumes

```

## TODO

```
client.api.base_url

client.containers.run(image_name,
    name=container_spec.container_name,
    ports={'{}/tcp'.format(container_spec.container_port): None},
    detach=True,
    labels=labels,
    volumes=volumes,
    nano_cpus=int(container_spec.cpus * 1e9),
    environment=environment,
    mem_reservation='{}M'.format(new_mem_reservation_mb))
client.containers.get(name_or_id)
    container.logs(timestamps=True)
    container.attrs['NetworkSettings']
    container.attrs['Config']['Labels']
    container.remove(force=True, v=True)
client.containers.list(all=True, filters=filters)

client.images
client.images.pull  # Used by script, but not used by runtime.
# For Kubernetes, consider https://kubernetes.io/docs/concepts/containers/images/#pre-pulling-images
# We would need to make sure that every image is on every node we start up.
# Mayber other Container registries are faster than DockerHub, in which
# case pre-caching might be less important?

client.volumes
client.volumes.create(driver='local').name
```