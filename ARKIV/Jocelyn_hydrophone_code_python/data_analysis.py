import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import RBFInterpolator
import os.path

coord = []
z = []

# Processed results are saved at the end so we don't need to recompute it everytime
# If you changed something to the raw results and wanna compute it again, just delete results.npz

if os.path.isfile("Jocelyn_hydrophone_code_python/processed_data/results.npz"):
    file = np.load("Jocelyn_hydrophone_code_python/processed_data/results.npz")
    coord = file["coord"]
    z = file["z"]
else:
    folder = "Jocelyn_hydrophone_code_python/raw_results"
    for file in os.listdir(folder):
        name = os.fsdecode(file)
        coord_str = name[:len(name)-4].split("_")
        x_file = float(coord_str[0])
        y_file = float(coord_str[1])
        coord.append([x_file, y_file])
        data = np.genfromtxt(folder+"/"+name, delimiter=',', skip_header=22)

        count, bins = np.histogram(data[data[:, 2] > 2, 1], bins=30)
        count_pos, bins_pos = count[bins[1:] > 0], np.concatenate(([bins[bins < 0][-1]], bins[bins > 0]))
        count_neg, bins_neg = count[bins[1:] < 0], bins[bins < 0]

        neg_max_arg = np.argmax(count_neg)
        neg_peak = (bins_neg[neg_max_arg] + bins_neg[neg_max_arg + 1]) / 2
        pos_max_arg = np.argmax(count_pos)
        pos_peak = (bins_pos[pos_max_arg] + bins_pos[pos_max_arg + 1]) / 2

        z.append(pos_peak-neg_peak)
        to_print = name + " " + coord_str[0] + " " + coord_str[1] + " {}"
        print(to_print.format(z[-1]))
    np.savez("Jocelyn_hydrophone_code_python/processed_data/results.npz", coord=coord, z=z)

coord = np.asarray(coord)
x = coord[:, 0]
y = coord[:, 1]


X = np.linspace(min(x), max(x))
Y = np.linspace(min(y), max(y))
X, Y = np.meshgrid(X, Y)  # 2D grid for interpolation

# You can change/remove kernel="gaussian" for other types of interpolation
interp = RBFInterpolator(list(zip(x, y)), np.asarray(z), kernel="gaussian", epsilon=1)
n = 50j
Z = interp(np.mgrid[min(x):max(x):n, min(y):max(y):n].reshape(2, -1).T)
# You can add the argument cmap= "..." to change the colormap of the plot
# For more info on what type of colormap you can choose, visit: https://matplotlib.org/stable/tutorials/colors/colormaps.html
plt.pcolormesh(X, Y, Z.reshape(50, 50), shading='auto')
# Comment the following line to remove the black dots
plt.plot(x, y, "ok", label="input point")
plt.legend()
plt.colorbar()
plt.axis("equal")
plt.show()
