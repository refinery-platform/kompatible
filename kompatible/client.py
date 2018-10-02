import time

from kubernetes import client, config
from kubernetes.stream import stream

config.load_kube_config()


class Client():

    @property
    def containers(self):
        return _Containers()


class _Containers():
    def run(self, image, command):
        api = client.CoreV1Api()
        name = 'todo-foobar'

        pod_manifest = {
            'apiVersion': 'v1',
            'kind': 'Pod',
            'metadata': {
                'name': name
            },
            'spec': {
                'containers': [{
                    'image': image,
                    'name': name,
                    "args": [  # TODO: Is this necessary?
                        "/bin/sh",
                        "-c",
                        "while true;do date;sleep 5; done"
                    ]
                }]
            }
        }

        api.create_namespaced_pod(body=pod_manifest, namespace='default')

        while True:
            resp = api.read_namespaced_pod(name=name, namespace='default')
            if resp.status.phase != 'Pending':
                break
            time.sleep(1)
        pass

        exec_command = ['/bin/sh', '-c', command]
        resp = stream(api.connect_get_namespaced_pod_exec, name, 'default',
                      command=exec_command,
                      stderr=True, stdin=False,
                      stdout=True, tty=False)
        # Return bytes just to match behavior of Docker client.
        return resp.encode()
