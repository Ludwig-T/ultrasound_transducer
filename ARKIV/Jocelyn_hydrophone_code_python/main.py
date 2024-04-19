import serial
import time
import pandas as pd
from os import system


def move_to_each_pos(s, pos):
    """
    Move the CNC machine to each of the location specified.
    Should be run with panda.DataFrame.apply() with three columns: X, Y and Z
    :param s: Serial to communicate with CNC machine
    :param pos: panda.Series containing three columns: X, Y and Z
    :return: Nothing
    """

    pos_str = "X={}, Y={}, Z={}".format(pos['X'], pos['Y'], pos['Z'])
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


df_pos = pd.read_csv("Jocelyn_hydrophone_code_python/coord.csv")
print(df_pos.head())

# By now the code assume that the CNC machine is plugged in the COM3 port of the PC. If it fails to open the port,
# check in the device manager in which port it is connected. You can either plug it in another port or change the
#
# name to 'COMX' (with X=the actual port number) in the following line

s = serial.Serial('COM5', 115200)
s.write("\r\n\r\n".encode())
time.sleep(2)
s.flushInput()

application = df_pos.apply(lambda row: move_to_each_pos(s, row), 1)

# Reset the position before closing the connection
input("Press any key to reset the position and finish the program")
line = "G0 X0 Y0 Z0"
s.write("".join([line, "\n"]).encode())
s.close()

