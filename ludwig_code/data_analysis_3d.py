import numpy as np
import hickle as hkl
import matplotlib.pyplot as plt
from scipy.interpolate import RBFInterpolator
import os.path

coord = []
value = []
std = []
# Processed results are saved at the end so we don't need to recompute it everytime
# If you changed something to the raw results and wanna compute it again, just delete results.npz


processed_file = "ludwig_code/processed_data/results19_2.npz"
if os.path.isfile(processed_file):
    file = np.load(processed_file)
    coord = file["coord"]
    value = file["value"]
    std = file["std"]
else:
    folder = "ludwig_code/result_hkl"
    for file in os.listdir(folder):
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
        print(to_print.format(value[-1]))
    np.savez(processed_file, coord=coord, value=value, std=std)

coord = np.asarray(coord)
x = coord[:, 0]
y = coord[:, 1]
# Comment the following line to remove the black dots

plt.tricontourf(x, y, value/0.13)
plt.colorbar(label="MPa")
plt.axis("image")
plt.xlabel("X [cm]")
plt.ylabel("Y [cm]")
plt.show()
"""
plt.tricontourf(x, y, std)
plt.colorbar()
plt.axis("image")
plt.xlabel("X [cm]")
plt.ylabel("Y [cm]")
plt.show()"""