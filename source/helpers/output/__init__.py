from loguru import logger

from helpers.output.driver.factory import OutputDriverFactory


class Output:
    def __init__(self, *args, **kwargs):
        self.driver = OutputDriverFactory.create_output_driver(*args, **kwargs)
        self.log = logger
        self.log.debug(f"using {self.driver.name} output driver")

    def put(self, output: str, **kwargs):
        self.driver.put(output, **kwargs)