import numpy as np
from scipy.ndimage import gaussian_filter



def normalize(stacked_array):
    """Normalize to 0-1 range per band."""
    normed = []
    for band in stacked_array:
        b_min, b_max = np.min(band), np.max(band)
        normed.append((band - b_min) / (b_max - b_min + 1e-6))
    return np.stack(normed)



def denoise(stacked_array, sigma=1):
    """Apply Gaussian filter to each band."""
    return np.stack([gaussian_filter(band, sigma=sigma) for band in stacked_array])
