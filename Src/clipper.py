import rasterio
import rasterio.mask
from shapely.geometry import Polygon, mapping

def clip_raster(stacked_array, profile, polygon_coords):
    """
    Clips raster based on polygon coordinates.
    Args:
        stacked_array (np.array): stacked raster (bands, h, w)
        profile (dict): raster profile
        polygon_coords (list): list of (lon, lat) tuples
    Returns:
        clipped_array, clipped_profile
    """
    poly = Polygon(polygon_coords)
    geom = [mapping(poly)]

    tmp_profile = profile.copy()
    tmp_profile.update(count=stacked_array.shape[0], driver="GTiff")

    with rasterio.open("temp.tif", "w", **tmp_profile) as tmp:
        for i in range(stacked_array.shape[0]):
            tmp.write(stacked_array[i], indexes=i+1)

    with rasterio.open("temp.tif") as src:
        out_image, out_transform = rasterio.mask.mask(src, geom, crop=True)
        out_meta = src.meta.copy()
        out_meta.update({
            "height": out_image.shape[1],
            "width": out_image.shape[2],
            "transform": out_transform
        })

    return out_image, out_meta


