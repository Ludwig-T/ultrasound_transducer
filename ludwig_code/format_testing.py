import pyvisa    
import time
import matplotlib.pyplot as plt

rm = pyvisa.ResourceManager()
#print(rm.list_resources())

#Set up oscilloscope
scope = rm.open_resource('TCPIP::10.77.76.3::INSTR')
time.sleep(2)
print(scope.query('*IDN?'))

scope.write(":WAVeform:FORMat ASCii")
#scope.write(":WAVeform:FORMat WORD")  # Set waveform data format to ASCII
scope.write(":WAVeform:POINts MAX")    # Set number of waveform points to acquire

scope.write(":WAVeform:SOURce CHANnel2")  # Select Channel as the source
time.sleep(2)
waveform_data_ascii = scope.query(":WAVeform:DATA?")

scope.write(":WAVeform:FORMat BINary")
waveform_data_binary = scope.query_binary_values(":WAVeform:DATA?", datatype="d", is_big_endian=True)
plt.plot(waveform_data_ascii[::10])
plt.plot(waveform_data_binary[::10])
plt.show()