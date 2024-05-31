import csv
import matplotlib.pyplot as plt


def plot_xz_plane(filename):
    x_values = []
    z_values = []
    with open(filename, 'r') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Skip header
        for row in reader:
            x_values.append(float(row[0]))
            z_values.append(float(row[2]))

    plt.scatter(x_values, z_values, s=1)  # Adjust 's' to change the size of points
    plt.xlabel('X')
    plt.ylabel('Z')
    plt.title('X-Z Plane')
    plt.grid(True)
    plt.axis('image')
    plt.show()


def generate_coordinates(specifications, filename):
    size = 0
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["X", "Y", "Z"])  # Write header

        min_x, max_x, step_x = specifications.get('X')
        min_y, max_y, step_y = specifications.get('Y')
        min_z, max_z, step_z = specifications.get('Z')
        MIN_x, MAX_x, STEP_x = specifications.get('X_big')
        MIN_z, MAX_z, STEP_z = specifications.get('Z_big')
        # Convert step sizes to integers by multiplying them by a suitable factor
        step_x_factor = int(1 / step_x)
        step_y_factor = int(1 / step_y)
        step_z_factor = int(1 / step_z)

        """    
        y = min_y
        zigzag = True
        while y <= max_y:
            x = MIN_x
            while x <= MAX_x:
                if min_x - STEP_x <= x < max_x:
                    x_var_step = step_x
                else:
                    x_var_step = STEP_x
                z = MIN_z
                while z <= MAX_z:
                    if min_x - STEP_x <= x < max_x and min_z - STEP_z <= z < max_z:
                        z_var_step = step_z
                    else:
                        z_var_step = STEP_z
                    writer.writerow([x, y, z])
                    size += 1
                    z += z_var_step
                x += x_var_step
            y += step_y
        """

        for y in range(int(min_y * step_y_factor), int(max_y * step_y_factor) + 1, 1):
            for i, x in enumerate(range(int(min_x * step_x_factor), int(max_x * step_x_factor) + 1, 1)):
                if i % 2 == 1: # Change every other to create zig-zag pattern
                    for z in range(int(max_z * step_z_factor), int(min_z * step_z_factor) - 1, -1):
                        writer.writerow([x / step_x_factor, y / step_y_factor, z / step_z_factor])
                        size += 1
                else:
                    for z in range(int(min_z * step_z_factor), int(max_z * step_z_factor) + 1, 1):
                        writer.writerow([x / step_x_factor, y / step_y_factor, z / step_z_factor])
                        size += 1
        
    return size

if __name__ == "__main__":

    specifications_search = {
        #    (min, max, step)
        'X': (-2, 2, 0.1),  # Horizontal
        'Y': (0, 0, 0.25),   # Hydrophone direction (should be in [0, inf) ) to go away from hydrophone
        'Z': (-2, 2, 0.1),   # Vertical
        "X_big" : (-1, 1, 0.1),
        "Z_big" : (-1, 1, 0.1)
    }
    
    specifications_meas = {
        #    (min, max, step)
        'X': (-0.5, 0.5, 0.5),  # Horizontal
        'Y': (0, 6, 0.075),   # Hydrophone direction (should be in [0, inf) ) to go away from hydrophone
        'Z': (-1.5, 1.5, 0.075),   # Vertical
        "X_big" : (-1, 1, 0.1),
        "Z_big" : (-1, 1, 0.1)
    }
    

    size_1 = generate_coordinates(specifications_search, "coord_search.csv")
    size_2 = generate_coordinates(specifications_meas, "coord_meas.csv")
    size = size_2
    time_per_measurement = 10859/8829 # s
    print(f"Time to complete search: {size_1 * time_per_measurement / (60)} minuits.")
    print(f"Total time to complete measurement: {size * time_per_measurement / (60 * 60)} days.")
    print(f"Total time including data analyis: {size * (time_per_measurement + 1 / 3.1 ) / (60 * 60 * 24)} days")
    print(f"Esstimated data size: {size_2 * 3208328 / 1024 ** 3} GB") # Old size 8022792
    print(f"Number of data points: {size_2}")
    plot_xz_plane("coordinates_2.csv")