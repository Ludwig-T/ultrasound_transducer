import pyvisa
import csv
import time
import serial
import datetime
import numpy as np
import pandas as pd
from os import system


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
    

def main(result_folder_name):
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

    df_pos = pd.read_csv("coordinates_light.csv")

    for index, pos in df_pos.iterrows():
        # Get the current timestamp
        timestamp = time.time()
        dt_object = datetime.datetime.fromtimestamp(timestamp)
        date_str = dt_object.strftime("%Y_%m_%d_%H_%M_%S")

        move_to_pos(s, pos, wait_for_input=False)
        _ = scope.query("TER?") # Clear trigger variable when moving
        if index <= 1:
            time.sleep(2)

          # Select Channel as the source
        has_trigged = wait_for_trig(scope)
        if not has_trigged: print("Oscilloscope has not triggered")
        waveform_data = scope.query_binary_values(":WAVeform:DATA?", datatype="h", is_big_endian=True)
        voltage_data = [word2float(datapoint, y_inc, y_org) for datapoint in waveform_data]
        # Can't send commands to cnc machine too fast, also
        # too fast measurements indicate faulty measurement.
        """if time.time() - timestamp < 2:
            print(f"Too fast measurement for {pos['X']}_{pos['Z']}_{date_str}")
            time.sleep(5)"""

        # Save waveform data to a CSV file
        with open(f"ludwig_code/{result_folder_name}/{pos['X']}_{pos['Z']}_{date_str}.csv", "w", newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Index", "Voltage"])  # Write header
            for index, voltage in enumerate(voltage_data):
                writer.writerow([index + 1, str(voltage)])

    # Close the connection
    graceful_exit(s, scope)

if __name__ == "__main__":
   try:
      main("result_quick")
   except KeyboardInterrupt:
      graceful_exit(s, scope)
      pass

# 286228 to 686241




