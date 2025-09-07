import rasterio
from rasterio.enums import Resampling
import numpy as np
import os

def load_and_stack_bands(region_path: str) -> tuple[np.ndarray, dict]:
    """
    Load Sentinel-2 bands for a region, resample 20m bands to 10m, 
    and stack into a single multiband array.

    Args:
        region_path (str): folder path where Sentinel-2 bands are stored

    Returns:
        tuple:
            stacked_array (numpy.ndarray): shape = (bands, height, width)
            profile (dict): raster metadata of reference band
    """
    # Bands required (fixed for snow analysis)
    band_files = [
        "B02_10m.jp2",  # Blue
        "B03_10m.jp2",  # Green
        "B04_10m.jp2",  # Red
        "B08_10m.jp2",  # NIR
        "B11_20m.jp2",  # SWIR1 (resampled)
        "B12_20m.jp2"   # SWIR2 (resampled)
    ]

    # Reference band for resolution alignment (always 10m)
    reference_band = os.path.join(region_path, "B02_10m.jp2")

    with rasterio.open(reference_band) as ref:
        ref_data = ref.read(1)
        ref_profile = ref.profile
        ref_height, ref_width = ref_data.shape

    stacked = []
    for fname in band_files:
        path = os.path.join(region_path, fname)
        with rasterio.open(path) as src:
            if "20m" in fname:  # resample to 10m grid
                data = src.read(
                    out_shape=(src.count, ref_height, ref_width),
                    resampling=Resampling.bilinear
                )[0]
            else:  # already 10m
                data = src.read(1)
        stacked.append(data)

    stacked_array = np.stack(stacked, axis=0)  # (bands, height, width)
    return stacked_array, ref_profile


