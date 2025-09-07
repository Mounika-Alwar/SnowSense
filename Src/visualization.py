import plotly.express as px
import numpy as np

def visualize_results(ndsi_mask: np.ndarray,
                      dry_snow: np.ndarray,
                      wet_snow: np.ndarray,
                      snow_area: float,
                      downsample_factor: int = 4):
    """
    Visualize snow analysis results using Plotly, with automatic downsampling.

    Args:
        ndsi_mask (np.ndarray): binary snow mask (NDSI)
        dry_snow (np.ndarray): dry snow mask
        wet_snow (np.ndarray): wet snow mask
        snow_area (float): total snow area in km²
        downsample_factor (int): factor to downsample large rasters for plotting

    Returns:
        figs: list of Plotly figure objects [fig1, fig2, fig3]
    """

    # --- Downsample and convert to uint8 ---
    def downsample(array):
        if array.ndim == 3:  # multi-band
            return array[:, ::downsample_factor, ::downsample_factor].astype(np.uint8)
        else:  # 2D mask
            return array[::downsample_factor, ::downsample_factor].astype(np.uint8)

    ndsi_mask_small = downsample(ndsi_mask)
    dry_snow_small = downsample(dry_snow)
    wet_snow_small = downsample(wet_snow)

    # --- Snow mask figure ---
    fig1 = px.imshow(ndsi_mask_small,
                     color_continuous_scale="Blues",
                     title="Snow Mask (NDSI)")

    # --- Dry vs wet snow figure ---
    snow_type_array = np.zeros_like(ndsi_mask_small, dtype=int)
    snow_type_array[dry_snow_small > 0] = 1
    snow_type_array[wet_snow_small > 0] = 2
    fig2 = px.imshow(snow_type_array,
                     color_continuous_scale=["lightgray", "blue", "cyan"],
                     title="Dry vs Wet Snow (1=Dry, 2=Wet)")

    # --- Snow area bar plot ---
    fig3 = px.bar(x=["Snow Area (km²)"],
                  y=[snow_area],
                  title="Total Snow Area")

    return [fig1, fig2, fig3]


