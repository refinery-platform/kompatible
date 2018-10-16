# kompatible

[![PyPI version](https://badge.fury.io/py/kompatible.svg)](https://badge.fury.io/py/kompatible)

This package exposes a subset of the
[Kubernetes Python Client](https://github.com/kubernetes-client/python/)
with an interface which matches that of the
[Docker SDK for Python](https://docker-py.readthedocs.io/en/stable/).

## Examples

First install this package from pypi: `pip install kompatible`.
Then install the kubernetes client and/or the docker sdk from pypi,
and correspondingly, either
[Minikube](https://kubernetes.io/docs/tutorials/hello-minikube/#create-a-minikube-cluster).
and/or [Docker](https://docs.docker.com/docker-for-mac/install/).

With those tools in place, either
`import kompatible as sdk` or `import docker as sdk`
and the following examples will work, although in the first case
it's Kubernetes pods starting up,
and in the latter it's Docker containers.

(These examples ignore differences in string output between Python 2 and 3,
but differences between `docker` and `kompatible` are highlighted.)

## "Hello World!": Run, list, remove

```
>>> client = sdk.from_env()

>>> [client.containers.run(
...     "alpine", "echo hello world",
...     name='foobar',
...     labels={'foo': 'bar'})]
['hello world\n']

>>> def not_kube(containers):  # Only needed for Docker, on Travis, with k8s started.
...     return [c for c in containers if 'kube' not in c.name]

>>> containers = not_kube(client.containers.list(all=True, filters={}))
>>> [c.name for c in containers]
['foobar']
>>> c = containers[0]

>>> c.logs()
'hello world\n'  # docker
''  # kompatible

>>> c.remove(force=True, v=True)
>>> containers = not_kube(client.containers.list(all=True, filters={}))
>>> assert len(containers) == 0

```

## Container properties

```
>>> len(c.id)
64  # docker
36  # kompatible

>>> len(c.short_id)
10

>>> c.image
<Image: 'alpine:...'>  # docker
'alpine'  # kompatible

>>> c.labels
{'foo': 'bar'}

>>> c.status
'exited'  # docker
{...}  # kompatible

```

## `containers.run` kwargs

```
>>> container_from_run = client.containers.run(
...     "nginx:1.15.5-alpine",
...     name='nginx',
...     labels={'foo': 'bar'},
...     ports={'80/tcp': None},
...     detach=True
... )
>>> container_from_run.attrs['NetworkSettings']['Ports']
{}

>>> container_from_get = client.containers.get('nginx')
>>> attrs = container_from_get.attrs['NetworkSettings']['Ports']['80/tcp']
>>> len(attrs)
1
>>> attrs[0]['HostIp']
'0.0.0.0'  # docker
'10...'  # kompatible
>>> attrs[0]['HostPort']
'...' # docker
80  # kompatible

>>> container_from_get.logs(timestamps=True)
''

```
And connect to that container via HTTP:
```
>>> import requests

# TODO

>>> container_from_get.remove(force=True, v=True)

```

## Subclient stubs

```
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