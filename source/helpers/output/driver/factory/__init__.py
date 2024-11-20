from exception.exception import OutputDriverNotRecognizeException
from helpers.output.driver.file import FileOutputDriver
from helpers.output.driver.s3 import S3OutputDriver
from helpers.output.driver.std import StdOutputDriver


class OutputDriverFactory:
    @staticmethod
    def create_output_driver(*args, **kwargs):
        destination = kwargs.get("destination")
        assert destination, "Destination is required"
        if destination == "s3":
            return OutputDriverFactory.create_s3_output_driver(*args, **kwargs)
        elif destination == "file":
            return OutputDriverFactory.create_file_output_driver(*args, **kwargs)
        else:
            raise OutputDriverNotRecognizeException()

    @staticmethod
    def create_std_output_driver(*args, **kwargs):
        return StdOutputDriver(*args, **kwargs)
        
    @staticmethod
    def create_s3_output_driver(*args, **kwargs):
        return S3OutputDriver(
            bucket=kwargs.pop("output"),
            access_key=kwargs.pop("s3_key"),
            secret_key=kwargs.pop("s3_secret"),
            endpoint=kwargs.pop("s3_endpoint"),
            *args,
            **kwargs
        )

    @staticmethod
    def create_file_output_driver(*args, **kwargs):
        return FileOutputDriver(kwargs.pop("output"), *args, **kwargs)