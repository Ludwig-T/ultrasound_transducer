import pyvisa
import time
import serial
import datetime
import numpy as np
import hickle as hkl
import pandas as pd
import os
import csv
import psutil
from os import system
from os.path import join
from data_analysis_3d import process_data

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
    

def main(output_path, coordinates_path, processed_filename, store="raw"):
    """
    Based on move_and_measure.py but implemented data transfer in WORD format to speed it up
    """
    global scope
    global s
    global f
    rm = pyvisa.ResourceManager()
    #print(rm.list_resources())
    
    print(f"Saving outputs to folder: {output_path}")
    os.makedirs(output_dir, exist_ok=True)
    if len(os.listdir(output_path)) == 0:
        print("    Warning that folder is not empty")
    print(f"Reading coordinates from file: {coordinates_path}")
    print(f"Saving processed data to: {processed_filename}")
    print("")
    
    if store == "val": 
        f = open(join(output_path, "data_values.csv"), "w", newline="")
        csv_writer = csv.writer(f)
        csv_writer.writerow(["Value", "X", "Y", "Z"])  # Write header
        
    
    #Set up oscilloscope
    scope = rm.open_resource('TCPIP::10.77.76.3::INSTR')
    time.sleep(2)
    print(scope.query('*IDN?'))

    scope.write(":WAVeform:FORMat WORd")
    scope.write(":WAVeform:POINts MAX")
    y_inc = float(scope.query(":WAVeform:YINCrement?"))
    y_org = float(scope.query(":WAVeform:YORigin?"))
    scope.write(":WAVeform:SOURce CHANnel1")
    
    # Set up CNC machine
    s = serial.Serial('COM5', 115200)
    s.write("\r\n\r\n".encode())
    time.sleep(2)
    s.flushInput()

    df_pos = pd.read_csv(coordinates_path)
    flush_count = 0
    for index, pos in df_pos.iterrows():
        # Get the current timestamp
        timestamp = time.time()
        dt_object = datetime.datetime.fromtimestamp(timestamp)
        date_str = dt_object.strftime("%Y_%m_%d_%H_%M_%S")

        move_to_pos(s, pos, wait_for_input=False)
        if index <= 1:
            time.sleep(2)
            
        time.sleep(0.02)
        retries = 0
        while retries < 20:
            try:
                _ = scope.query("TER?")
                break
            except pyvisa.errors.VisaIOError:
                print("Timeout expired. Retrying...")
                retries += 1
                time.sleep(2)
        else:
            print("Maximum number of retries exceeded. Exiting.")
        

        has_trigged = wait_for_trig(scope)
        if not has_trigged: print("Oscilloscope has not triggered")
        
        waveform_data = scope.query_binary_values(":WAVeform:DATA?", datatype="h", is_big_endian=True)
        waveform_data = waveform_data[286228:686241]
        voltage_data = [word2float(datapoint, y_inc, y_org) for datapoint in waveform_data]
        voltage_data = np.array(voltage_data)
        if store == "raw":
            hkl.dump(voltage_data, join(output_path, f"{pos['X']}_{pos['Z']}_{pos['Y']}_raw_{date_str}.hkl"), mode="w", compression="gzip")
        elif store == "val":
            flush_count += 1
            val = histogram_magic(voltage_data)
            csv_writer.writerow([val, pos['X'], pos['Z'], pos['Y']])
            if flush_count > 50:
                process = psutil.Process()
                memory_info = process.memory_info()
                ram_usage = memory_info.rss / (1024 ** 2)  # Convert to MB
                print(f"RAM Usage: {ram_usage:.2f} MB")

                f.flush()
                os.fsync(f)
                flush_count = 0
                
                process = psutil.Process()
                memory_info = process.memory_info()
                ram_usage = memory_info.rss / (1024 ** 2)  # Convert to MB
                print(f"RAM Usage: {ram_usage:.2f} MB")
        else:
            raise ValueError("Invalid value for argument store", str(store))
    
    if store == "val": f.close()
    # Close the connection
    graceful_exit(s, scope)
    
    if store == "raw":
        process_data(processed_filename, output_path)

if __name__ == "__main__":
   
    output_dir = "R:/measurements/10may"
    processed_filename = "R:/measurements/10may.npz"
    coord_path = "C:/Users/tiston/code/coord_meas.csv"
    store = "val"  # Store raw data or processed single value
    try:
        main(output_dir, coord_path, processed_filename, store)

    finally:
        print("closing")
        graceful_exit(s, scope)
        process_data(processed_filename, output_dir)
        f.close()


# 286228 to 686241




