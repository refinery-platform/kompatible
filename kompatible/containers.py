import time
import logging

from kubernetes import client
from kubernetes.stream import stream

NAMESPACE = 'default'

logging.basicConfig()
logger = logging.getLogger(__name__)


class ContainersClient():

    def __init__(self):
        self.api = client.CoreV1Api()

    def run(self, image, command=None,
            name='anonymous', labels={}, environment={}):
        pod_manifest = {
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
                    "args": [  # TODO: Is this necessary?
                        "/bin/sh",
                        "-c",
                        "while true;do date;sleep 5; done"
                    ],
                    'env': [{'name': n,
                             'value': v} for (n, v) in environment.items()]
                }]
            }
        }

        self.api.create_namespaced_pod(body=pod_manifest, namespace=NAMESPACE)

        while True:
            resp = self.api.read_namespaced_pod(name=name, namespace=NAMESPACE)
            if resp.status.phase != 'Pending':
                break
            time.sleep(1)
        pass

        exec_command = ['/bin/sh', '-c', command]
        resp = stream(self.api.connect_get_namespaced_pod_exec,
                      name, 'default',
                      command=exec_command,
                      stderr=True, stdin=False,
                      stdout=True, tty=False)
        # Return bytes just to match behavior of Docker client.
        return resp.encode()

    def list(self, all=False, filters=None):
        all_pods = self.api.list_pod_for_all_namespaces(watch=False).items
        logger.warn('all_pods: {}'.format(
            [(pod.metadata.name, pod.metadata.namespace) for pod in all_pods]))
        our_pods = [pod for pod in all_pods
                    if pod.metadata.namespace == NAMESPACE]
        return [_ContainerWrapper(self.api, pod) for pod in our_pods]


class _ContainerWrapper():
    def __init__(self, api, pod):
        self._api = api

        meta = pod.metadata
        containers = pod.spec.containers
        if len(containers) > 1:
            raise Exception(
                'Expected single container; not {}'.format(containers))

        self.id = meta.uid
        self.image = containers[0].image
        self.labels = meta.labels
        self.name = meta.name
        self.short_id = self.id[:10]
        self.status = pod.status

    def remove(self, force=None, v=None):
        if not force or not v:
            raise Exception('Unsupported: "force" and "v" must both be True')
        self._api.delete_namespaced_pod(
            self.name, NAMESPACE,
            client.V1DeleteOptions(grace_period_seconds=0))
