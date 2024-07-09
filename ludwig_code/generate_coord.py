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
    """Generates a csv of coordinates from specifications

    Args:
        specifications (dict): Dictionary of specification of size and step size of measurement (see example)
        filename (str): The name/path of the output file

    Returns:
        int: number of coordinates
    """
    
    size = 0
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["X", "Y", "Z"])  # Write header

        min_x, max_x, step_x = specifications.get('X')
        min_y, max_y, step_y = specifications.get('Y')
        min_z, max_z, step_z = specifications.get('Z')
                
        step_x_factor = 1 / step_x
        step_y_factor = 1 / step_y
        step_z_factor = 1 / step_z


        for y in range(int(min_y * step_y_factor), int(max_y * step_y_factor) + 1, 1):
            for i, x in enumerate(range(int(min_x * step_x_factor), int(max_x * step_x_factor) + 1, 1)):
                if i % 2 == 1: # Change every other to create zig-zag pattern
                    for z in range(int(max_z * step_z_factor), int(min_z * step_z_factor) - 1, -1):
                        writer.writerow([round(x / step_x_factor, 3), round(y / step_y_factor, 3), round(z / step_z_factor, 3)])
                        size += 1
                else:
                    for z in range(int(min_z * step_z_factor), int(max_z * step_z_factor) + 1, 1):
                        writer.writerow([round(x / step_x_factor, 3), round(y / step_y_factor, 3), round(z / step_z_factor, 3)])
                        size += 1
        
    return size

if __name__ == "__main__":

    specifications_search = {
        #    (min, max, step)
        'X': (-5, 5, 0.75),  # Horizontal
        'Y': (0, 30, 3),   # Hydrophone direction (should be in [0, inf) ) to go away from hydrophone
        'Z': (-5, 5, 0.75)   # Vertical
    }
    
    specifications_meas = {
        #    (min, max, step)
        'X': (0, 0, 0.075),  # Horizontal
        'Y': (0, 30, 0.075),   # Hydrophone direction (should be in [0, inf) ) to go away from hydrophone
        'Z': (-3, 3, 0.075)   # Vertical
    }
    """
    specifications_meas = {
        #    (min, max, step)
        'X': (-3, 3, 0.075),  # Horizontal
        'Y': (0, 0, 0.15),   # Hydrophone direction (should be in [0, inf) ) to go away from hydrophone
        'Z': (-3, 3, 0.075)   # Vertical
    }"""
    
    """
    specifications_meas = {
        #    (min, max, step)
        'X': (-2.2, 2.2, 0.05),  # Horizontal
        'Y': (0, 0, 0.075),   # Hydrophone direction (should be in [0, inf) ) to go away from hydrophone
        'Z': (-2.2, 2.2, 0.05),   # Vertical
        "X_big" : (-1, 1, 0.1),
        "Z_big" : (-1, 1, 0.1)
    }
    """
    
    

    size_1 = generate_coordinates(specifications_search, "coord_search.csv")
    size_2 = generate_coordinates(specifications_meas, "coord_meas.csv")
    size = size_2
    time_per_measurement = 10859/8829 # s
    
    time_hour = size * time_per_measurement / (60 * 60)
    time_day = time_hour / 24
    # print(f"Time to complete search: {size_1 * time_per_measurement / (60)} minuits.")
    print(f"Total time to complete measurement: {time_day} days.")
    print(f"That is {time_hour} hours.")
    # print(f"Total time including data analyis: {size * (time_per_measurement + 1 / 3.1 ) / (60 * 60 * 24)} days")
    # print(f"Esstimated data size: {size_2 * 3208328 / 1024 ** 3} GB") # Old size 8022792
    # print(f"Number of data points: {size_2}")
    plot_xz_plane("coord_search.csv")