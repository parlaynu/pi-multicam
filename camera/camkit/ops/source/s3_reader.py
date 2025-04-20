from typing import Generator
import os
import time
import numpy as np
import cv2

try:
    import boto3
except:
    boto3 = None


def s3_reader(
    bucket: str, 
    prefix: str, 
    *, 
    seekable: bool = False, 
    profile_name: str = None, 
    region_name: str = None, 
    aws_access_key_id: str = None, 
    aws_secret_access_key: str = None, 
    aws_session_token: str = None,
    endpoint_url: str = None,
    extensions: dict = {'.png', '.jpg', '.jpeg'}
) -> Generator[dict, None, None]:
    """Read images from an AWS S3 or compatible bucket.

    if 'seekable' is True, the contents are downloaded to a temporary file before 
    being yielded.

    The other parameters offer a range of ways to specify how to authenticate and also
    the possibility to connect to alternative providers such as Cloudflare R2. See the
    AWS documentation for details.
    """

    print(f"Building camkit.ops.sources.s3_reader")


    # create the s3 client
    session = boto3.Session(
        profile_name=profile_name,
        region_name=region_name,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        aws_session_token=aws_session_token
    )
    client = session.client('s3', endpoint_url=endpoint_url)

    def gen():
        for idx, key in enumerate(_s3_scanner(client, bucket, prefix, extensions)):
            response = client.get_object(
                Bucket=bucket,
                Key=key
            )
            
            reader = response['Body']
            try:
                ibuf = np.asarray(bytearray(reader.read()))
                img = cv2.imdecode(ibuf, cv2.IMREAD_COLOR)
            finally:
                reader.close()
            
            item = {
                'idx': idx,
                'stamp': time.monotonic_ns(),
                'metadata': {
                    'name': f's3://{bucket}/{key}',
                },
                'main': {
                    'format': 'RGB888',
                    'image': img
                }
            }
            yield item

    return gen()


def _s3_scanner(
    client, # boto3.Client 
    bucket: str, 
    prefix: str, 
    extensions: dict
) -> Generator[dict, None, None]:

    # make sure the extensions are in the correct format
    exts = list(extensions)
    extensions = set()
    for ext in exts:
        if not ext.startswith('.'):
            ext = '.'+ext
        extensions.add(ext)

    def gen():
        resp = client.list_objects_v2(
            Bucket=bucket,
            Prefix=prefix,
        )
        
        while True:
            contents = resp.get('Contents', [])
            for c in contents:
                key = c['Key']

                _, ext = os.path.splitext(key)
                if not ext in extensions:
                    continue

                yield key

            if resp['IsTruncated'] == False:
                break

            ctoken = resp['NextContinuationToken']
            resp = client.list_objects_v2(
                Bucket=bucket,
                Prefix=prefix,
                ContinuationToken=ctoken,
            )

    return gen()

