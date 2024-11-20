import atexit
import os

from helpers.output.driver import OutputDriver


class FileOutputDriver(OutputDriver):
    name = "file"

    def __init__(self, path, *args, **kwargs):
        super(FileOutputDriver, self).__init__(*args, **kwargs)
        if path:
            self.path = path
            # if not os.path.exists(os.path.dirname(self.path)):
            #     os.makedirs(os.path.dirname(self.path))
            # self.file = open(path, "a")
        atexit.register(self.close)

    def put(self, output: str, **kwargs):
        if kwargs.get("path"):
            self.path = kwargs.get("path")
            # if not os.path.exists(os.path.dirname(self.path)):
            #     os.makedirs(os.path.dirname(self.path))
            # self.file = open(self.path, "a")
            # self.file.write(output)
            # self.file.close()
        else:
            if not self.path:
                raise Exception("directory not found")
            else:
                self.file.write(output)

    def close(self):
        pass
        # if self.file:
            # self.file.close()