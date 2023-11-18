import os
import numpy as np
import rasterio
import rasterio.mask
import geopandas as gpd


def safe_divide(numerator, denominator):
    return np.divide(numerator, denominator, out=np.zeros_like(numerator, dtype=float), where=(denominator != 0))


def calculate_chl_a(b5, b6):
    X1 = safe_divide(b6 - b5, b6 + b5)
    return 3248.8 * X1 ** 4 - 4006.3 * X1 ** 3 - 1501.5 * X1 ** 2 - 153.21 * X1 + 4.6857


def calculate_tn(b4, b6):
    X2 = safe_divide(b4, b6)
    return 0.0029 * X2 ** 3 + 0.1759 * X2 ** 2 - 0.5643 * X2 + 1.0893


def calculate_tp(b4, b6, b7):
    X3 = safe_divide(b4 + b6 + b7, 10000)
    return 1.0448 * X3 ** 2 + 0.0242 * X3 + 0.0085


def calculate_cod_mn(b3, b5, b7):
    X4 = safe_divide(b5 - b3 + b7, 10000)
    return -10865 * X4 ** 3 + 2276.5 * X4 ** 2 - 114.02 * X4 + 7.4545


def get_water_mask(vector_path, src):
    gdf = gpd.read_file(vector_path)
    if gdf.crs != src.crs:
        gdf = gdf.to_crs(src.crs)
    geometry = gdf.geometry
    mask = rasterio.mask.geometry_mask(geometry, invert=True, out_shape=(src.height, src.width),
                                       transform=src.transform)
    return mask


input_folder = r"D:\yaoganguochengshuju\EX1"
output_folder = os.path.join(input_folder, "calres")

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Update band mappings for ETM+ and OLI
bands_etm = {"b3": 2, "b4": 3, "b5": 4, "b6": 5, "b7": 6}
bands_oli = {"b3": 3, "b4": 4, "b5": 5, "b6": 6, "b7": 7}

for year in ['2005', '2010', '2016', '2020']:
    raster_file = f"{year}water"  # Assuming no file extension for the main file
    vector_file = f"{year}AWEI_nsh.shp"
    raster_path = os.path.join(input_folder, raster_file)
    vector_path = os.path.join(input_folder, vector_file)

    with rasterio.open(raster_path) as src:
        water_mask = get_water_mask(vector_path, src)
        band_data = src.read()
        sensor_type = "ETM+" if year in ['2005', '2010'] else "OLI"
        bands_mapping = bands_etm if sensor_type == "ETM+" else bands_oli

        b3 = band_data[bands_mapping["b3"] - 1]
        b4 = band_data[bands_mapping["b4"] - 1]
        b5 = band_data[bands_mapping["b5"] - 1]
        b6 = band_data[bands_mapping["b6"] - 1]
        b7 = band_data[bands_mapping["b7"] - 1] if sensor_type == "OLI" else band_data[
            bands_mapping["b6"] - 1]  # Use b6 as b7 for ETM+

        # Apply the water mask
        b3, b4, b5, b6, b7 = [np.where(water_mask, band, np.nan) for band in [b3, b4, b5, b6, b7]]

        # Calculate water quality parameters
        chl_a = calculate_chl_a(b5, b6)
        tn = calculate_tn(b4, b6)
        tp = calculate_tp(b4, b6, b7)
        cod_mn = calculate_cod_mn(b3, b5, b7)

        profile = src.profile
        profile.update(dtype='float32', count=1, driver='ENVI', interleave='band')

        # Save the results in ENVI format
        output_files = {
            "chl_a": chl_a,
            "tn": tn,
            "tp": tp,
            "cod_mn": cod_mn
        }

        for output_name, data in output_files.items():
            output_file_path = os.path.join(output_folder, f"{year}_{output_name}")
            with rasterio.open(output_file_path, 'w', **profile) as dst:
                dst.write(data, 1)

print("Water quality parameters calculated and saved in ENVI format.")
