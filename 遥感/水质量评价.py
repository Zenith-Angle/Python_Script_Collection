import os
import numpy as np
import rasterio


def calculate_tli(chl_a, tn, tp, cod_mn, weights):
    tli_chl_a = 10 * (2.5 + 1.086 * np.log(chl_a))
    tli_tn = 10 * (5.453 + 1.694 * np.log(tn))
    tli_tp = 10 * (9.436 + 1.624 * np.log(tp))
    tli_cod_mn = 10 * (0.109 + 2.661 * np.log(cod_mn))

    tli_values = {
        "tli_chl_a": tli_chl_a,
        "tli_tn": tli_tn,
        "tli_tp": tli_tp,
        "tli_cod_mn": tli_cod_mn
    }

    # Calculate the weighted sum for the total TLI
    total_tli = np.nansum([tli_values[key] * weight for key, weight in weights.items()], axis=0)

    return tli_values, total_tli


input_folder = r"D:\yaoganguochengshuju\EX1\calres"
output_folder = os.path.join(input_folder, "assessment")

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

weights = {
    "tli_chl_a": 0.32606,
    "tli_tn": 0.21924,
    "tli_tp": 0.23007,
    "tli_cod_mn": 0.22462
}

for year in ['2005', '2010', '2016', '2020']:
    files = {
        "chl_a": os.path.join(input_folder, f"{year}_chl_a"),
        "tn": os.path.join(input_folder, f"{year}_tn"),
        "tp": os.path.join(input_folder, f"{year}_tp"),
        "cod_mn": os.path.join(input_folder, f"{year}_cod_mn")
    }

    # Read the data for each parameter
    data = {param: rasterio.open(file).read(1) for param, file in files.items()}

    # Calculate the TLI values for each parameter and the total TLI
    tli_values, total_tli = calculate_tli(data['chl_a'], data['tn'], data['tp'], data['cod_mn'], weights)

    # Define profile for output file
    profile = rasterio.open(files['chl_a']).profile
    profile.update(dtype='float32', count=1, driver='ENVI', interleave='band')

    # Save the TLI results for each parameter and the total TLI
    for param, tli_data in tli_values.items():
        output_path = os.path.join(output_folder, f"{year}_{param}.dat")
        with rasterio.open(output_path, 'w', **profile) as dst:
            dst.write(tli_data.astype('float32'), 1)

    # Save the total TLI
    total_tli_path = os.path.join(output_folder, f"{year}_total_tli.dat")
    with rasterio.open(total_tli_path, 'w', **profile) as dst:
        dst.write(total_tli.astype('float32'), 1)

print("TLI calculations completed and saved in ENVI format.")
