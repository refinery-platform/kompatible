import logging
import time
from sys import version_info

from kubernetes import client
from kubernetes.stream import stream

NAMESPACE = 'default'

logging.basicConfig()
logger = logging.getLogger(__name__)


class ContainersException(Exception):
    pass


class ContainersClient():

    def __init__(self):
        if version_info[0] == 2:
            # On Python2 (not Python3) was hitting:
            #      File ".../stream/stream.py", line 32, in stream
            #        return func(*args, **kwargs)
            #      File ".../client/apis/core_v1_api.py", line 835,
            #        in connect_get_namespaced_pod_exec
            #        (data) = self.connect_get_namespaced_pod_exec
            #        _with_http_info(name, namespace, **kwargs)
            #      File ".../client/apis/core_v1_api.py", line 935,
            #        in connect_get_namespaced_pod_exec_with_http_info
            #        collection_formats=collection_formats)
            #      File ".../client/api_client.py", line 321, in call_api
            #        _return_http_data_only, collection_formats,
            #        _preload_content, _request_timeout)
            #      File ".../client/api_client.py", line 155, in __call_api
            #        _request_timeout=_request_timeout)
            #      File ".../stream/stream.py", line 27,
            #        in _intercept_request_call
            #        return ws_client.websocket_call(config, *args, **kwargs)
            #      File ".../stream/ws_client.py", line 255, in websocket_call
            #        raise ApiException(status=0, reason=str(e))
            #    ApiException: (0)
            #    Reason: hostname '192.168.99.100' doesn't match either of
            #      'minikubeCA', 'kubernetes.default.svc.cluster.local',
            #      'kubernetes.default.svc', 'kubernetes.default',
            #      'kubernetes', 'localhost'
            config = client.Configuration()
            config.verify_ssl = False
            client.Configuration.set_default(config)
        self.api = client.CoreV1Api()

    def _ports_spec(self, ports):
        ports_spec = []
        for k, v in ports.items():
            if v is not None:
                raise ContainersException(
                    'Unexpected non-None in port dict values: {}'.format(
                        ports))
            port_components = k.split('/')
            if len(port_components) != 2:
                raise ContainersException(
                    'Expected the form port/protocol, not "{}"'.format(k))
            [port_number, protocol] = port_components
            ports_spec.append({
                'containerPort': int(port_number),
                'protocol': protocol.upper()
            })
        return ports_spec

    def _manifest(self, name=None, labels=None, image=None,
                  ports_spec=None, environment=None):
        return {
            'apiVersion': 'v1',
            'kind': 'Pod',
            'metadata': {
                'name': name,
                'labels': labels
            },
            'spec': {
                'containers': [{
                    'image': image,
                    'name': name,
                    'labels': labels,
                    "args": [
                        # There is no analog to Docker detach:
                        # The pod exits when the last process exits.
                        "/bin/sh",
                        "-c",
                        "while true; do sleep 1; done"
                    ],
                    'ports': ports_spec,
                    'env': [{'name': n,
                             'value': v} for (n, v) in environment.items()]
                }]
            }
        }

    def run(self, image, command=None, name='anonymous',
            labels={}, environment={}, ports={}, detach=False):
        ports_spec = self._ports_spec(ports)
        pod_manifest = self._manifest(
            name=name, labels=labels, image=image,
            ports_spec=ports_spec, environment=environment)

        pod = self.api.create_namespaced_pod(
            body=pod_manifest, namespace=NAMESPACE)

        while True:
            resp = self.api.read_namespaced_pod(name=name, namespace=NAMESPACE)
            if resp.status.phase != 'Pending':
                break
            time.sleep(1)
        pass

        if detach:
            if command is not None:
                raise ContainersException(
                    '"command" and "detach" kwargs are incompatible')
            return _ContainerWrapper(self.api, pod)

        kwargs = {
            'stderr': True, 'stdin': False, 'stdout': True, 'tty': False
        }
        if command is not None:
            kwargs['command'] = ['/bin/sh', '-c', command]
        stream_response = stream(self.api.connect_get_namespaced_pod_exec,
                                 name, 'default', **kwargs)
        # Return bytes just to match behavior of Docker client.
        return stream_response.encode()

    def get(self, name):
        # TODO: Handle lookup by ID.
        return _ContainerWrapper(
            self.api, self.api.read_namespaced_pod(name, 'default'))

    def list(self, all=False, filters=None):
        all_pods = self.api.list_pod_for_all_namespaces(watch=False).items
        our_pods = [pod for pod in all_pods
                    if pod.metadata.namespace == NAMESPACE]
        return [_ContainerWrapper(self.api, pod) for pod in our_pods]


class _ContainerWrapper():
    def __init__(self, api, pod):
        self._api = api

        meta = pod.metadata
        containers = pod.spec.containers
        if len(containers) > 1:
            raise ContainersException(
                'Expected single container; not {}'.format(containers))
        container = containers[0]

        if container.ports is None:
            ports = {}
        else:
            ports = {
                '{}/{}'.format(
                    p.container_port,
                    p.protocol.lower()
                ): [{
                    'HostIp': p.host_ip,
                    'HostPort': p.host_port
                }]
                for p in container.ports
            }

        self.id = meta.uid
        self.attrs = {
            'NetworkSettings': {'Ports': ports}
        }
        self.image = container.image
        self.labels = meta.labels
        self.name = meta.name
        self.short_id = self.id[:10]
        self.status = pod.status

    def remove(self, force=None, v=None):
        if not force or not v:
            raise ContainersException(
                'Unsupported: "force" and "v" must both be True')
        self._api.delete_namespaced_pod(
            self.name, NAMESPACE,
            client.V1DeleteOptions(grace_period_seconds=0))
