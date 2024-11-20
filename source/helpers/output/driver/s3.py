import atexit
import json
import s3fs

from helpers.output.driver import OutputDriver


class S3OutputDriver(OutputDriver):
    name = "s3"
    
    def __init__(self, access_key: str, secret_key: str, endpoint: str, bucket: str, *args, **kwargs):
        super(S3OutputDriver, self).__init__(*args, **kwargs)
        self.bucket = bucket
        self.client_kwargs = {
            'key': access_key,
            'secret': secret_key,
            'endpoint_url': endpoint,
            'anon': False
        }
        self.client = s3fs.core.S3FileSystem(**self.client_kwargs)
        
        atexit.register(self.close)
    
    def put(self, output, **kwargs):
        path = kwargs.get('s3_path')
        
        if isinstance(output, dict):
            output = json.dumps(output)
            mode = "w"
        elif isinstance(output, bytes):
            mode = "wb"
        else:   
            raise ValueError("output must be a dictionary or bytes.")

        self.log.info(f"Sending file to s3....")
        with self.client.open(f"{self.bucket}/{path}", mode) as f:
            f.write(output)
    
    def close(self):
        pass