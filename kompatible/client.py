class Client():

    @property
    def containers(self):
        return _Containers()


class _Containers():
    def run(self, image, command):
        pass