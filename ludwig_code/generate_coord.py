import csv

def generate_coordinates(specifications, filename):
    size = 0
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["X", "Y", "Z"])  # Write header

        min_x, max_x, step_x = specifications.get('X', (0, 0, 1))
        min_y, max_y, step_y = specifications.get('Y', (0, 0, 1))
        min_z, max_z, step_z = specifications.get('Z', (0, 0, 1))

        for x in range(min_x, max_x + 1, step_x):
            for y in range(min_y, max_y + 1, step_y):
                for z in range(min_z, max_z + 1, step_z):
                    writer.writerow([x, y, z])
                    size += 1
    return size
filename = "coordinates.csv"  # Specify the filename for the CSV file

# Generate the CSV file


if __name__ == "__main__":
    specifications = {
        'X': (-50, 50, 10),  # (min, max, step)
        'Y': (0, 0, 1),      # (min, max, step)
        'Z': (-10, 10, 10)       # (min, max, step)
    }
    size = generate_coordinates(specifications, "coordinates_light.csv")
    print(size)