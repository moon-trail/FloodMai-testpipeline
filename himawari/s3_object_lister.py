import boto3
from botocore import UNSIGNED
from botocore.config import Config

s3 = boto3.client('s3', config=Config(signature_version=UNSIGNED))

bucket_name = 'noaa-himawari9'
prefix = 'AHI-L2-FLDK-Clouds/2025/06/15/1500/'

response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)

for obj in response.get('Contents', []):
    print(obj['Key'])
