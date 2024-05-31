import pyvisa
import matplotlib.pyplot as plt
import time
import serial
import datetime
import numpy as np
import hickle as hkl
import pandas as pd
from os import system, makedirs
from os.path import join

def histogram_magic(waveform):
    """
    Calculates a voltage value from waveform
    """
    count, bins = np.histogram(waveform, bins=30)
    count_pos, bins_pos = count[bins[1:] > 0], np.concatenate(([bins[bins < 0][-1]], bins[bins > 0]))
    count_neg, bins_neg = count[bins[1:] < 0], bins[bins < 0]

    neg_max_arg = np.argmax(count_neg)
    neg_peak = (bins_neg[neg_max_arg] + bins_neg[neg_max_arg + 1]) / 2
    pos_max_arg = np.argmax(count_pos)
    pos_peak = (bins_pos[pos_max_arg] + bins_pos[pos_max_arg + 1]) / 2

    return pos_peak-neg_peak

#Code interacting with CNC-machine is thanks to previous master student
def move_to_pos(s, pos, wait_for_input=True):
    """
    Move the CNC machine to each of the location specified.
    Should be run with panda.DataFrame.apply() with three columns: X, Y and Z
    :param s: Serial to communicate with CNC machine
    :param pos: panda.Series containing three columns: X, Y and Z
    :return: Nothing
    """

    pos_str = "X={}, Y={}, Z={}".format(pos['X'], pos['Y'], pos['Z'])
    if wait_for_input:
        input("Press Enter to move to position: " + pos_str)
    system('cls')
    g_code = write_g_code(pos)
    s.write(g_code.encode())
    print("Move (" + pos_str + "): " + s.readline().decode().strip())


def write_g_code(pos):
    """
    Write the linear translation in G-code
    :param pos: pandas.Series containing the target position
    :return: String containing the G-code
    """
    return "G0 X{} Y{} Z{}\n".format(pos['X'], pos['Y'], pos['Z'])

def word2float(word_int, y_inc, y_org):
    """
    Converts word-format integers to voltage values
    """
    return word_int*y_inc + y_org


def wait_for_trig(scope):
    """
    Waits for a trigger from the oscilloscope to ensure a updated measurement

    :param scope: pyvisa for scope
    :return: bool for if trigger has happend or not
    """
    has_trigged = False
    safety_index = 0
    while not has_trigged:
        safety_index += 1
        has_trigged = bool(float(scope.query("TER?")))
        if has_trigged:
            return has_trigged
        else:
            time.sleep(0.1)
            if safety_index > 100: return has_trigged


def graceful_exit(s, scope):
    """
    Resets CNC machine and disconnects scope and cnc machine

    :param s: Serial to communicate with CNC machine
    :param scope: pyvisa resource to scope
    """
    time.sleep(2)
    line = "G0 X0 Y0 Z0"
    s.write("".join([line, "\n"]).encode())
    time.sleep(2)
    #scope.exit()
    s.close()
    

def one_measurement(index, pos, y_inc, y_org):
    
    
    move_to_pos(s, pos, wait_for_input=False)
    
    _ = scope.query("TER?") # Clear trigger variable when moving
    if index <= 1:
        time.sleep(2)

    has_trigged = wait_for_trig(scope)
    if not has_trigged: print("Oscilloscope has not triggered")
    
    waveform_data = scope.query_binary_values(":WAVeform:DATA?", datatype="h", is_big_endian=True)
    waveform_data = waveform_data[286228:686241]
    voltage_data = [word2float(datapoint, y_inc, y_org) for datapoint in waveform_data]
    
    return np.array(voltage_data)


def search_max(coordinates_path, y_inc, y_org):
    
    df_pos = pd.read_csv(coordinates_path)
    pos_at_max = False
    value_max = 0
    for index, pos in df_pos.iterrows():

        voltage_data = one_measurement(index, pos, y_inc, y_org)
        
        value = histogram_magic(voltage_data)
        if value > value_max:
            pos_at_max = pos
            
    return pos_at_max, value

def main(output_path, coordinates_path, search_coord_path):
    """
    Based on move_and_measure.py but implemented data transfer in WORD format to speed it up
    """
    global scope
    global s
    rm = pyvisa.ResourceManager()
    #print(rm.list_resources())

    #Set up oscilloscope
    scope = rm.open_resource('TCPIP::10.77.76.3::INSTR')
    time.sleep(2)
    print(scope.query('*IDN?'))

    scope.write(":WAVeform:FORMat WORd")
    scope.write(":WAVeform:POINts MAX")    # Set number of waveform points to acquire
    y_inc = float(scope.query(":WAVeform:YINCrement?"))
    y_org = float(scope.query(":WAVeform:YORigin?"))
    scope.write(":WAVeform:SOURce CHANnel1")
    #scope.write(":WAVeform:BYTeorder MSBFirst")
    
    # Set up CNC machine
    s = serial.Serial('COM5', 115200)
    s.write("\r\n\r\n".encode())
    time.sleep(2)
    s.flushInput()

    pos_centre, value_max= search_max(search_coord_path, y_inc, y_org)
    
    print("Max located at {pos_centre} of {value_max}")
    
    df_pos = pd.read_csv(coordinates_path)
    
    if np.min(df_pos["Z"]) + pos_centre["Z"] < 0:
        pos_centre["Z"] += np.min(df_pos["Z"]) + pos_centre["Z"]
        
    for index, pos in df_pos.iterrows():
        
        pos = pos + pos_centre
        if pos["Z"] < 0:
            print("Position too close to hydrophone, skipping")
            continue
        # Get the current timestamp
        timestamp = time.time()
        dt_object = datetime.datetime.fromtimestamp(timestamp)
        date_str = dt_object.strftime("%Y_%m_%d_%H_%M_%S")

        voltage_data = one_measurement(index, pos, y_inc, y_org)
        
        hkl.dump(voltage_data, join(output_path, f"{pos['X']}_{pos['Z']}_{pos['Y']}_{date_str}.hkl"), mode="w")

    # Close the connection
    graceful_exit(s, scope)

if __name__ == "__main__":
   
    output_dir = "R:/measurements/2nd_3D"
    makedirs(output_dir, exist_ok=True)
    coord_path = "C:/Users/tiston/code/coord_meas.csv"
    search_coord_Path = "C:/Users/tiston/code/coord_search.csv"
    try:
        main(output_dir, coord_path, search_coord_Path)

    except KeyboardInterrupt:
        graceful_exit(s, scope)
        pass

# 286228 to 686241




