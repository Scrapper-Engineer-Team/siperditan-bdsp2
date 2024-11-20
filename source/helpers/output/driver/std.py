from helpers.output.driver import OutputDriver


class StdOutputDriver(OutputDriver):
    name = "std"

    def __init__(self, *args, **kwargs):
        super(StdOutputDriver, self).__init__(*args, **kwargs)

    def put(self, output: str, **kwargs):
        print(output)

    def close(self):
        pass