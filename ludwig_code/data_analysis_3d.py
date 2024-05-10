import numpy as np
import pandas as pd
from tqdm import tqdm
import seaborn as sns
import hickle as hkl
import matplotlib.pyplot as plt
from scipy.interpolate import RBFInterpolator
import os.path

def process_data(processed_file, folder):
    
    
    coord = []
    value = []
    std = []
    

    if os.path.isfile(processed_file):
        file = np.load(processed_file)
        coord = file["coord"]
        value = file["value"]
        std = file["std"]
    else:
        print("Commencing Processing")
        for file in tqdm(os.listdir(folder)):
            name = os.fsdecode(file)
            coord_str = name[:len(name)-4].split("_")
            x_file = float(coord_str[0])
            y_file = float(coord_str[1])
            z_file = float(coord_str[2])
            coord.append([x_file, y_file, z_file])
            data = hkl.load(folder+"/"+name)
            selected_values = data[:]
            std.append(np.std(selected_values))
            count, bins = np.histogram(selected_values, bins=30)
            count_pos, bins_pos = count[bins[1:] > 0], np.concatenate(([bins[bins < 0][-1]], bins[bins > 0]))
            count_neg, bins_neg = count[bins[1:] < 0], bins[bins < 0]

            neg_max_arg = np.argmax(count_neg)
            neg_peak = (bins_neg[neg_max_arg] + bins_neg[neg_max_arg + 1]) / 2
            pos_max_arg = np.argmax(count_pos)
            pos_peak = (bins_pos[pos_max_arg] + bins_pos[pos_max_arg + 1]) / 2

            value.append(pos_peak-neg_peak)
            to_print = name + " " + coord_str[0] + " " + coord_str[1] + " {}"

        np.savez(processed_file, coord=coord, value=value, std=std)
        
    return coord, value, std

if __name__ == "__main__":
        
    processed_file = "R:/measurements/new_hp_2.npz"
    folder = "R:/measurements/new_hp_2"
    coord, value, std = process_data(processed_file, folder)

    # Assuming coord and value are numpy arrays
    coord = np.asarray(coord)
    value = np.asarray(value)
    zs = np.unique(coord[:, 2])

    # Initialize variables for vmin and vmax
    vmin = np.min(value)
    vmax = np.max(value)

    for z in zs:
        # Create a DataFrame for this specific z-value
        mask = coord[:, 2] == z
        x = coord[mask, 0]
        y = coord[mask, 1]
        v = value[mask]

        df = pd.DataFrame({
            'X': x,
            'Y': y,
            'Value': v
        })


        # Pivot the DataFrame to create a grid
        grid_df = df.pivot(index='Y', columns='X', values='Value').sort_index(ascending=False)

        # Create a new figure and axis
        fig, ax = plt.subplots(figsize=(6, 6))
        im = ax.imshow(grid_df, cmap="viridis", interpolation='nearest', vmin=vmin, vmax=vmax, extent=[np.min(x), np.max(x), np.min(y), np.max(y)])
        ax.set_title(f"Z = {z:.2f} mm")
        ax.set_xlabel("X [mm]")
        ax.set_ylabel("Y [mm]")

        # Add a colorbar for this subplot
        cbar = fig.colorbar(im, ax=ax, orientation='vertical')
        cbar.set_label('MPa')

        plt.tight_layout()
        plt.show()
