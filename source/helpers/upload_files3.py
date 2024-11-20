import aiofiles
import s3fs
from configparser import ConfigParser


async def upload_to_s3(local_path: str, raw_path: str):
    config = ConfigParser()
    config.read("config.ini")

    
    client_kwargs = {
        'key': config.get("s3", "key"),
        'secret': config.get("s3", "secret"),
        'endpoint_url': config.get("s3", "endpoint"),
        'anon': False
    }

    s3 = s3fs.S3FileSystem(**client_kwargs)

    for local_path, raw_path in zip(local_path, raw_path):
        try:
            async with aiofiles.open(local_path, 'rb') as local_file:
                file_content = await local_file.read()

            # Menggunakan s3fs untuk menulis ke S3
            with s3.open(raw_path, 'wb') as s3_file:
                s3_file.write(file_content)

            if not s3.exists(raw_path):
                print(f"S3 file {raw_path} does not exist after upload.")

        except Exception as e:
            print(f"Error uploading {local_path} to {raw_path}: {e}")