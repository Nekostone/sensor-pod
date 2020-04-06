import serial
import time
import csv
import numpy as np
from file_utils import save_as_npy, load_npy
from visualizer import init_heatmap, update_heatmap

"""
Initialization
Serial Parameters - Port, Baud Rate, Start Byte
Program Mode - Plot (Debug) / Write Mode
"""

# SERIAL_PORT = 'COM5' # for windows
SERIAL_PORT = "/dev/ttyUSB0" # for linux
BAUD_RATE = 115200
ARRAY_SHAPE = (24,32)

DEBUG_MODE = 1
WRITE_MODE = 0

def get_nan_value_indices(df):
  """
  :return: an array of indices of the nan values in the input data frame
  """
  return np.argwhere(np.isnan(df))

def interpolate_values(df, nan_value_indices):
    """
    :param: 23x32 data frame obtained from get_nan_value_indices(df)
    :return: 24x32 array
    """
    for indx in nan_value_indices:
        x = indx[0]
        y = indx[1]
        df[x][y] = (df[x][y+1] + df[x+1][y] + df[x-1][y] + df[x][y-1]) / 4
    return df

def threshold_df(df, min_value, max_value):
    """
    :param 24x32 data frame
    :return: a thresholded dataframe
    """
    df[df > max_value] = max_value
    df[df < min_value] = min_value
    return df


def divide_grid_into_areas(array):
    """
    Divides a 24x32 array into 8x12x8 array
    :return: 8x12x8 array
    """
    result = np.zeros((8, 12, 8))
    block_number = 0
    for i in range(2):
        for j in range(4):
            result[block_number] = array[i * 12:(i + 1) * 12, j * 8:(j + 1) * 8]
            block_number += 1
    return result

def run_arduino(forever, num_samples=3000, mode=DEBUG_MODE):
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE)
    ser.reset_output_buffer()
    counter = 0

    to_read = forever or counter < num_samples
    plot = None
    if mode == DEBUG_MODE:
        min_temp = 28
        max_temp = 40
        plot = init_heatmap("MLX90640 Heatmap", ARRAY_SHAPE, min_temp, max_temp)
        
    while to_read:
        try:
            ser_bytes = ser.readline()
            decoded_string = ser_bytes.decode("utf-8", errors='ignore').strip("\r\n")
            values = decoded_string.split(",")[:-1]
            array = np.array(values)    
            print(array.shape)
            if array.shape[0] == ARRAY_SHAPE[0] * ARRAY_SHAPE[1]:
                df = np.reshape(array.astype(float), ARRAY_SHAPE)
                nan_value_indices = get_nan_value_indices(df)
                df = interpolate_values(df, nan_value_indices)
                max_temp = np.amax(df)
                min_temp = np.amin(df)
                df = threshold_df(df, min_temp, max_temp)

                if mode == DEBUG_MODE:
                    print("Number of times replotted: ", counter)
                    update_heatmap(df, plot)
                    print("Saving npy object...")
                    save_as_npy(df)

                elif mode == WRITE_MODE:
                    save_as_npy(df)
                
            counter += 1

        except KeyboardInterrupt:
            raise
        except Exception as e:
            print(e)
            break

if __name__ == "__main__":
    run_arduino(forever=True)
