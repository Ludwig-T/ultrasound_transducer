import csv

def generate_coordinates(specifications, filename):
    size = 0
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["X", "Y", "Z"])  # Write header

        min_x, max_x, step_x = specifications.get('X')
        min_y, max_y, step_y = specifications.get('Y')
        min_z, max_z, step_z = specifications.get('Z')

        # Convert step sizes to integers by multiplying them by a suitable factor
        step_x_factor = int(1 / step_x)
        step_y_factor = int(1 / step_y)
        step_z_factor = int(1 / step_z)

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
    specifications = {
        #    (min, max, step)
        'X': (-0.4, 0.4, 0.02),  # Horizontal
        'Y': (0, 1.5, 0.01),   # Hydrophone direction
        'Z': (-0.4, 0.4, 0.02)   # Vertical
    }
    size = generate_coordinates(specifications, "coordinates_2.csv")
    time_per_measurement = 1 # s
    print(f"Total time to complete measurement: {size * time_per_measurement / (60 * 60 * 24)} days.")
    print(f"Esstimated data size: {size * 3208328 / 1024 ** 3} GB") # Old size 8022792
    print(f"Number of data points: {size}")