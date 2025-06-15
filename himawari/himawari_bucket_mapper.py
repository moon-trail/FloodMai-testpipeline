import boto3
from botocore import UNSIGNED
from botocore.config import Config

# Anonymous S3 client
s3 = boto3.client('s3', config=Config(signature_version=UNSIGNED))

bucket_name = 'noaa-himawari9'
prefix = ''  # start at the root
delimiter = '/'

def list_s3_prefixes(bucket, prefix='', delimiter='/'):
    response = s3.list_objects_v2(Bucket=bucket, Prefix=prefix, Delimiter=delimiter)
    if 'CommonPrefixes' in response:
        print(f"Directories under '{prefix}':")
        for cp in response['CommonPrefixes']:
            print(cp['Prefix'])
    else:
        print(f"No subdirectories found under prefix '{prefix}'.")

# Example usage:
# list_s3_prefixes(bucket_name, prefix='AHI-L1b-Target/')
list_s3_prefixes(bucket_name, prefix='AHI-L2-FLDK-Clouds/2025/06/15/1500/')
