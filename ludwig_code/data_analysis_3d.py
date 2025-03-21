# Code by Ludwig Tiston
# 
# This script displays the results and, if necessary,
# preforms post-processing.
# 
import os
import numpy as np
import pandas as pd
from tqdm import tqdm
import hickle as hkl
import matplotlib.pyplot as plt
from os.path import join
import multiprocessing as mp
from scipy.ndimage import gaussian_filter


def process_file(func_in):
    """Code for running in parallel. Found not to be useful
    as disc speed was the limiting factor.

    Args:
        func_in (tuple): tuple with path to filename and folder path of file

    Returns:
        tuple: A tuple containing the coordinates (list of floats), the value (float), 
        and the standard deviation (float or NaN if not applicable).
    """
    
    file = func_in[0]
    folder = func_in[1]
    
    name = os.fsdecode(file)
    coord_str = name[:len(name)-4].split("_")
    x_file = float(coord_str[0])
    y_file = float(coord_str[1])
    z_file = float(coord_str[2])
    coord = [x_file, y_file, z_file]
    data = hkl.load(folder+"/"+name)
    if coord_str[3] == "val":
        selected_values = data[:]
        std = np.std(selected_values)
        count, bins = np.histogram(selected_values, bins=30)
        count_pos, bins_pos = count[bins[1:] > 0], np.concatenate(([bins[bins < 0][-1]], bins[bins > 0]))
        count_neg, bins_neg = count[bins[1:] < 0], bins[bins < 0]

        neg_max_arg = np.argmax(count_neg)
        neg_peak = (bins_neg[neg_max_arg] + bins_neg[neg_max_arg + 1]) / 2
        pos_max_arg = np.argmax(count_pos)
        pos_peak = (bins_pos[pos_max_arg] + bins_pos[pos_max_arg + 1]) / 2

        value = pos_peak - neg_peak
    else:
        value = data
        std = np.nan
    return coord, value, std


def process_data(processed_file, folder, cores=1):
    """Reads and, if necessary, processes data

    Args:
        processed_file (filepath): path to output file (should be .npz)
        folder (filepath): path to folder with data 
        cores (int, optional): Number of cores to use, a bit unstable if not 1. Defaults to 1.

    Returns:
        tuple: A tuple containing the coordinates (list of floats), the value (float), 
        and the standard deviation (float or NaN if not applicable).
    """
    coord = []
    value = []
    std = []

    if os.path.isfile(processed_file):
        print("Loading preprocsesed file")
        file = np.load(processed_file)
        coord = file["coord"]
        value = file["value"]
        std = file["std"]
    else:
        print("Let the processing COMMENCE", flush=True)
        files = os.listdir(folder)
        print(files)
        if len(files) == 1:
            df = pd.read_csv(join(folder, files[0]))  # Read the CSV file
            coord = df[['X', 'Y', 'Z']].values.tolist()  # Extract coordinates
            value = df['Value'].values.tolist()  # Extract values
            std = None
        else:
            try:
                if cores == 1:
                    for file in tqdm(files):
                        c, v, s = process_file((file, folder))
                        coord.append(c)
                        value.append(v)
                        std.append(s)
                else:   
                    with mp.Pool(processes=cores) as pool, tqdm(total=len(files)) as pbar:
                        results = pool.imap(process_file, [(file, folder) for file in files])

                        for result in results:
                            coord.append(result[0])
                            value.append(result[1])
                            std.append(result[2])
                            pbar.update(1)
                
            except Exception as e:
                np.savez(processed_file.replace(".npz", "_partial.npz"), coord=coord, value=value, std=std)
                
            np.savez(processed_file, coord=coord, value=value, std=std)
        
    return coord, value, std


if __name__ == "__main__":
    
    name = "longitudal_26june"
    processed_file = f"R:/measurements/{name}.npz" # filename of processed file
    folder = f"R:/measurements/{name}" # filename of folder with data inside
    plane_to_plot = 0 # What plane to plot later.
    smooth = False # If smoothing should be applied.
    interpolation = "none" #"nearest"
    cmap = "jet"
    
    plane_dict = {
        0: "X [mm]",
        1: "Y [mm]",
        2: "Z [mm]"
    }
    coord, value, std = process_data(processed_file, folder)
    # Assuming coord and value are numpy arrays
    coord = np.asarray(coord)
    print(coord.shape)
    print(f"Shape of data:")
    print(f"X: {max(coord[:,0]) - min(coord[:,0])} mm")
    print(f"Y: {max(coord[:,1]) - min(coord[:,1])} mm")
    print(f"Z: {max(coord[:,2]) - min(coord[:,2])} mm")
    value = np.asarray(value)
    zs = np.unique(coord[:, plane_to_plot])

    # Initialize variables for vmin and vmax
    vmin = np.min(value)
    vmax = np.max(value)

    planes = [0, 1, 2]
    planes.remove(plane_to_plot)
    
    for z in zs:
        # Create a DataFrame for this specific z-value
        mask = coord[:, plane_to_plot] == z
        x = coord[mask, planes[1]]
        y = coord[mask, planes[0]]
        v = value[mask]

        df = pd.DataFrame({
            'X': x,
            'Y': y,
            'Value': v
        })


        # Pivot the DataFrame to create a grid
        grid_df = df.pivot(index='Y', columns='X', values='Value').sort_index(ascending=False)
        
        if smooth:
            grid_df = gaussian_filter(grid_df, sigma=1)
        # Create a new figure and axis
        fig, ax = plt.subplots(figsize=(6, 6))
        im = ax.imshow(grid_df, cmap=cmap, interpolation=interpolation, vmin=vmin, vmax=vmax, extent=[np.min(x), np.max(x), np.min(y), np.max(y)])
        ax.set_title(f"Slice in {plane_dict[plane_to_plot].split(' ')[0]}-plane")# = {z:.2f}")
        ax.set_xlabel(plane_dict[planes[1]])
        ax.set_ylabel(plane_dict[planes[0]])

        # Add a colorbar for this subplot
        cbar = fig.colorbar(im, ax=ax, orientation='vertical')
        cbar.set_label('MPa')

        plt.tight_layout()
        plt.show()
