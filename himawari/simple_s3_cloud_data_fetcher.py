import boto3
from botocore import UNSIGNED
from botocore.config import Config
import xarray as xr
import matplotlib.pyplot as plt
import numpy as np
# Step 1: Download the NetCDF file with anonymous S3 access
def download_file():
    s3 = boto3.client('s3', config=Config(signature_version=UNSIGNED))
    bucket_name = 'noaa-himawari9'
    key = 'AHI-L2-FLDK-Clouds/2025/06/15/1500/AHI-CHGT_v1r1_h09_s202506151500212_e202506151509406_c202506151521080.nc'
    local_filename = 'AHI-CHGT_20250615_1500.nc'

    print(f"Downloading {key} from bucket {bucket_name}...")
    s3.download_file(Bucket=bucket_name, Key=key, Filename=local_filename)
    print(f"Downloaded file saved as {local_filename}")
    return local_filename

# Step 2: Load the file and plot the Cloud Top Height
def plot_cloud_top_height(filename):
    ds = xr.open_dataset(filename)

    # Load variables
    chgt = ds['CldTopHght'].values
    lat = ds['Latitude_Pc'].values
    lon = ds['Longitude_Pc'].values

    # Crop to Bangkok area
    mask = (
        (chgt > 0) &
        np.isfinite(lat) &
        np.isfinite(lon) &
        (lat >= 13.5) & (lat <= 14.5) &
        (lon >= 100.3) & (lon <= 101.0)
    )

    chgt_bangkok = chgt[mask]
    lat_bangkok = lat[mask]
    lon_bangkok = lon[mask]

    # Plot in grayscale
    plt.figure(figsize=(8, 6))
    sc = plt.scatter(lon_bangkok, lat_bangkok, c=chgt_bangkok, cmap='gray', s=1)
    plt.colorbar(sc, label='Cloud Top Height (m)', shrink=0.75)
    plt.title('Cloud Top Height over Bangkok')
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.grid(True)
    plt.savefig("Bangkok.png", dpi=300, bbox_inches='tight')
    plt.tight_layout()
    plt.show()
def main():
    filename = download_file()
    plot_cloud_top_height(filename)

if __name__ == '__main__':
    main()
