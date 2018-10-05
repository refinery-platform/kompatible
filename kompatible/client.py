from kubernetes import config
from kubernetes.client import configuration

from .api import ApiClient
from .containers import ContainersClient
from .images import ImagesClient
from .volumes import VolumesClient

config.load_kube_config()
configuration.assert_hostname = False
# Trying to fix network problems on python2.7.
# https://github.com/kubernetes-client/python/issues/144#issuecomment-282909931


class Client():

    @property
    def containers(self):
        return ContainersClient()

    @property
    def api(self):
        return ApiClient()

    @property
    def images(self):
        return ImagesClient()

    @property
    def volumes(self):
        return VolumesClient()
