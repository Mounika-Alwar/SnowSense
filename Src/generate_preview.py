import numpy as np
import rasterio
import matplotlib.pyplot as plt

def generate_preview(region_path):
    b02 = f"{region_path}/B02_10m.jp2"  # Blue
    b03 = f"{region_path}/B03_10m.jp2"  # Green
    b04 = f"{region_path}/B04_10m.jp2"  # Red

    def read_band(path):
        with rasterio.open(path) as src:
            return src.read(1)

    r = read_band(b04)
    g = read_band(b03)
    b = read_band(b02)

    # normalize to 0-255
    def normalize_band(band):
        return ((band - band.min()) / (band.max() - band.min()) * 255).astype(np.uint8)

    rgb = np.dstack([normalize_band(r), normalize_band(g), normalize_band(b)])
    return rgb


