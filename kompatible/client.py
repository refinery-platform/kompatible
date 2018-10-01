import time

from kubernetes import client, config


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
                    "args": [
                        "/bin/sh",
                        "-c",
                        "while true;do date;sleep 5; done"
                    ]
                }]
            }
        }

        resp = api.create_namespaced_pod(body=pod_manifest,
                                         namespace='default')

        while True:
            resp = api.read_namespaced_pod(name=name,
                                           namespace='default')
            if resp.status.phase != 'Pending':
                break

            time.sleep(1)
        pass