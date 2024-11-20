from abc import ABC
from loguru import logger
from faker import Faker
from configparser import ConfigParser
from helpers.output import Output

import os

class Controllers(ABC):
    def __init__(self, *args, **kwargs):
        self.config = ConfigParser()
        self.config.read(kwargs.get("config"))
        self.log = logger
        self.faker = Faker()
        self.headless = kwargs.get("headless", False)
        if kwargs.get("destination") == "s3":
            kwargs.update({
                "s3_endpoint": self.config.get("s3", "endpoint"),
                "s3_key": self.config.get("s3", "key"),
                "s3_secret": self.config.get("s3", "secret")
            })

        if kwargs.get("destination"):
            self.output_name = kwargs.get("output")
            self.destination_name = kwargs.get("destination")
            if self.destination_name == "file": os.makedirs(self.output_name, exist_ok=True)
            self.output = Output(*args, **kwargs)



    async def main(self):
        try:
            await self.handler()
        except Exception as e:
            self.exceptions_handler(e)

    async def handler(self):
        pass

    def exceptions_handler(self, e):
        self.log.error(e)