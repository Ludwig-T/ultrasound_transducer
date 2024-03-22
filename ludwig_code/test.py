import pyvisa
import csv
import numpy as np
rm = pyvisa.ResourceManager()

#print(rm.list_resources())
scope = rm.open_resource('TCPIP::10.77.76.3::INSTR')
print(scope.query('*IDN?'))

# Set up the oscilloscope to acquire waveform data from Channel 2
scope.write(":WAVeform:FORMat ASCii")  # Set waveform data format to ASCII
scope.write(":WAVeform:POINts MAX")    # Set number of waveform points to acquire
scope.write(":WAVeform:SOURce CHANnel2")  # Select Channel 2 as the source
scope.write(":WAVeform:DATA?")            # Request waveform data

# Read waveform data
waveform_data = scope.read()

# 286228 to 686241

# Close the connection
scope.close()

# Save waveform data to a CSV file
with open("waveform_data_channel1.csv", "w", newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["Index", "Voltage"])  # Write header
    for index, voltage in enumerate(waveform_data.split(',')):
        writer.writerow([index + 1, voltage.strip()])


