import numpy as np


def calculate_ndsi(stacked_array, threshold=0.4):
    """Compute NDSI and return snow mask + text summary."""
    green = stacked_array[1]  # B03
    swir = stacked_array[4]   # B11
    ndsi = (green - swir) / (green + swir + 1e-6)
    snow_mask = ndsi > threshold
    return snow_mask, f"Snow pixels detected: {np.sum(snow_mask)}"


def classify_snow(stacked_array, snow_mask):
    """Differentiate dry vs wet snow."""
    nir = stacked_array[3]  # B08
    dry_snow = (snow_mask) & (nir > 0.3)
    wet_snow = (snow_mask) & (nir <= 0.3)
    dry_count, wet_count = np.sum(dry_snow), np.sum(wet_snow)
    return dry_snow, wet_snow, f"Dry snow: {dry_count}, Wet snow: {wet_count}"


def compute_snow_area(snow_mask, resolution=10):
    """Compute snow area in sq km."""
    pixel_area = (resolution**2) / 1e6  # m² → km²
    total_area = np.sum(snow_mask) * pixel_area
    return total_area, f"Total snow area: {total_area:.2f} km²"

