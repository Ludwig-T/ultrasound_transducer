import os
import pickle
import pandas as pd
import matplotlib.pyplot as plt

def load_data_from_folder(folder_path):
    data = {}  # Dictionary to store data for each coordinate

    # Iterate over files in the folder
    i = 0
    for file_name in os.listdir(folder_path):
        i += 1
        print(f"Loading file {i}")
        if file_name.endswith('.csv'):
            # Extract coordinates from the file name
            coordinates = tuple(map(float, file_name.split('_')[:2]))

            # Load CSV file into a DataFrame
            file_path = os.path.join(folder_path, file_name)
            df = pd.read_csv(file_path)

            # Calculate mean voltage
            mean_voltage = df['Voltage'].mean()

            # Store mean voltage for the coordinate
            data[coordinates] = mean_voltage
    
    filename = "data.pkl"
    with open(filename, 'wb') as file:  # 'wb' mode opens the file in binary write mode
    # Use pickle.dump() to save the dictionary to the file
        pickle.dump(data, file)

    return data

def plot_mean_voltages(data):
    print("Plotting data")
    # Extract coordinates and mean voltages from the dictionary
    coordinates, mean_voltages = zip(*data.items())

    # Plot mean voltages for each coordinate
    plt.figure(figsize=(10, 6))
    plt.scatter(*zip(*coordinates), c=mean_voltages, cmap='viridis', s=100)
    plt.colorbar(label='Mean Voltage')
    plt.xlabel('X Coordinate')
    plt.ylabel('Y Coordinate')
    plt.title('Mean Voltages for Coordinates')
    plt.grid(True)
    plt.show()

# Folder path containing CSV files
folder_path = "C:/Users/tiston/code/ludwig_code/raw_data3"

# Load data from folder
data = load_data_from_folder(folder_path)

# Plot mean voltages
plot_mean_voltages(data)