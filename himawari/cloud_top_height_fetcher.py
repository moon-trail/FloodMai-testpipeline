import boto3
from botocore import UNSIGNED
from botocore.config import Config
import xarray as xr
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import os

# Setup S3
s3 = boto3.client('s3', config=Config(signature_version=UNSIGNED))
bucket_name = 'noaa-himawari9'
base_prefix = 'AHI-L2-FLDK-Clouds/'

# Your region of interest
region_lat_range = (13.8, 13.9)
region_lon_range = (100.5, 100.6)

# Manual start and end dates (inclusive)
start_date = datetime(2025, 6, 16)
end_date = datetime(2025, 6, 18)

def list_s3_files(bucket, prefix):
    response = s3.list_objects_v2(Bucket=bucket, Prefix=prefix)
    return [obj['Key'] for obj in response.get('Contents', []) if obj['Key'].endswith('.nc')]

def extract_features(filename):
    with xr.open_dataset(filename) as ds:
        chgt = ds['CldTopHght'].values
        lat = ds['Latitude_Pc'].values
        lon = ds['Longitude_Pc'].values

    mask = (
        (chgt > 0) & np.isfinite(lat) & np.isfinite(lon) &
        (lat >= region_lat_range[0]) & (lat <= region_lat_range[1]) &
        (lon >= region_lon_range[0]) & (lon <= region_lon_range[1])
    )

    if not np.any(mask):
        return pd.DataFrame()

    ts = extract_timestamp_from_filename(filename)
    return pd.DataFrame({
        'Timestamp': [ts] * np.sum(mask),
        'Latitude': lat[mask],
        'Longitude': lon[mask],
        'CloudTopHeight': chgt[mask]
    })

def extract_timestamp_from_filename(fn):
    parts = fn.split('_')
    for p in parts:
        if p.startswith('s2025'):
            return datetime.strptime(p[1:15], '%Y%m%d%H%M%S')
    return None

def download_and_process(prefix):
    files = list_s3_files(bucket_name, prefix)
    if not files:
        print(f"❌ No files found for prefix: {prefix}")
        return None

    # Pick the first .nc file (typically from start of hour)
    file_key = files[0]
    local_file = os.path.basename(file_key)
    try:
        print(f"⬇️ Downloading {file_key}")
        s3.download_file(bucket_name, file_key, local_file)
        df = extract_features(local_file)
        if not df.empty:
            print(f"✅ Extracted {len(df)} points")
        else:
            print(f"⚠️ No valid data in file")
        return df
    except Exception as e:
        print(f"❌ Error downloading/processing {file_key}: {e}")
        return None
    finally:
        if os.path.exists(local_file):
            os.remove(local_file)

output_file = 'cloud_heights_filtered.csv'


def save_to_csv(df, output_file):
    if df is not None and not df.empty:
        write_header = not os.path.exists(output_file)
        df.to_csv(output_file, mode='a', header=write_header, index=False)
        print(f"📄 Appended {len(df)} rows to {output_file}")
    else:
        print("⚠️ No data to write for this hour.")

def main():
    print(f"📅 Processing data from {start_date.date()} to {end_date.date()}")
    current_time = start_date
    while current_time <= end_date:
        print(f"\n📅 Processing hour: {current_time.strftime('%Y-%m-%d %H:%M')}")
        prefix = current_time.strftime(base_prefix + '%Y/%m/%d/%H00/')
        df = download_and_process(prefix)
        save_to_csv(df, output_file)
        current_time += timedelta(hours=1)

    print(f"\n✅ Finished processing from {start_date.date()} to {end_date.date()}")
    print(f"📁 Data saved to: {output_file}")

main()