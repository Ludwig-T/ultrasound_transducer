import csv
import numpy as np
from itertools import product
from typing import NamedTuple


# Appelable par commandline aussi?
# Limites à tester aussi?
# - oui, tester min < max
# - entre -150 et 150 pour x inclus
# - entre -90 et 90 pour y
# - entre -20 et 20 pour z
# - steps >= 0.1

# X,Y,Z
# lists


class CSVArgs(NamedTuple):
    ax0_min: int
    ax0_max: int
    ax0_step: int
    ax1_min: int
    ax1_max: int
    ax1_step: int
    ax2_min: int
    ax2_max: int
    ax2_step: int


def makecsv(csvargs:CSVArgs, filename="coord.csv"):
    '''
    Creates a csv file containing the coordinates that the CNC machine will visit.

    @param csvargs: CSVArgs object containing all min, max and step values required.
    @param filename: Name of the csv file, with .csv extension.
    @returns None
    '''
    
    # TODO: Asserts

    # Create coordinates
    ax0 = np.arange(csvargs.ax0_min * 10, (csvargs.ax0_max + 0.1) * 10, csvargs.ax0_step * 10, dtype=np.single)
    ax1 = np.arange(csvargs.ax1_min * 10, (csvargs.ax1_max + 0.1) * 10, csvargs.ax1_step * 10, dtype=np.single)
    ax2 = np.arange(csvargs.ax2_min * 10, (csvargs.ax2_max + 0.1) * 10, csvargs.ax2_step * 10, dtype=np.single)
    ax0, ax1, ax2 = ax0 / 10, ax1 / 10, ax2 / 10
    lines = list(product(ax0, ax1, ax2))
    
    # Write lines to csv
    with open(filename, 'w', newline='') as csv_file:
        writer = csv.writer(csv_file, delimiter=',')
        writer.writerow(['X', 'Y', 'Z'])
        for line in lines:
            writer.writerow(line)


# Test this beautiful code

csvargs = CSVArgs(
    ax0_min = -1,
    ax0_max = 1,
    ax0_step = 0.5,
    ax1_min = 0,
    ax1_max = 0,
    ax1_step = 10,
    ax2_min = -0.5,
    ax2_max = 0.5,
    ax2_step = 0.1,
)

makecsv(csvargs)





