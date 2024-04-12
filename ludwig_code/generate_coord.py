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

        for x in range(int(min_x * step_x_factor), int(max_x * step_x_factor) + 1, 1):
            for y in range(int(min_y * step_y_factor), int(max_y * step_y_factor) + 1, 1):
                for z in range(int(min_z * step_z_factor), int(max_z * step_z_factor) + 1, 1):
                    writer.writerow([x / step_x_factor, y / step_y_factor, z / step_z_factor])
                    size += 1
    return size

if __name__ == "__main__":
    specifications = {
        #    (min, max, step)
        'X': (-1.2, 1.2, 0.05),  # Horizontal
        'Y': (0, 0, 1),       # Hydrophone direction
        'Z': (-1.2, 1.2, 0.05)   # Vertical
    }
    size = generate_coordinates(specifications, "coordinates_light.csv")
    print(size)