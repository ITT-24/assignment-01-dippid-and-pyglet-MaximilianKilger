import socket 
import time
import json
import random, math

BUTTON_THRESHOLD = 0.6
ACCEL_OFFSET_X = 0
ACCEL_OFFSET_Y = 2347
ACCEL_OFFSET_Z = 76348
SPEED = 0.025

AMPLITUDE_BIAS = 1.2
FREQUENCY_EXPONENT = 3.6
FREQUENCY_BIAS = 0.0005
#chooses the right function for the job.
def get_value(capability, time):
    if capability == "accelerometer":
        return get_value_accelerometer(time)
    elif capability == "button_1":
        return get_value_button(time)

#generates accelerometer data
def get_value_accelerometer (time):
    values = {}
    values["x"] = get_layered_sin_value(time, ACCEL_OFFSET_X)
    values["y"] = get_layered_sin_value(time, ACCEL_OFFSET_Y)
    values["z"] = get_layered_sin_value(time, ACCEL_OFFSET_Z)
    return values


def get_value_button(time):
    value = get_layered_sin_value(time)
    if value > BUTTON_THRESHOLD:
        return 1
    else:
        return 0

def generate_values(time):
    time = time * SPEED
    measures = {}
    for capability in capabilities:
        value = get_value(capability, time)
        measures[capability] = value
    return measures

def get_layered_sin_value(time, offset=0):
    value = 0
    for fractal_sin in sin_functions:
        value += fractal_sin(time+offset)
    return value

def initialize_randomizer_values(sin_layers):
    for i in range(sin_layers):
        
        amplitude = 1/((i+2)*AMPLITUDE_BIAS)
        frequency = random.random() * (i+1) ** FREQUENCY_EXPONENT * FREQUENCY_BIAS
        x_shift = random.random() * 2 * math.pi
        layered_sin_function = lambda x : math.sin( frequency * x + x_shift) * amplitude
        sin_functions.append(layered_sin_function)
SIN_LAYERS = 50
sin_functions = []

initialize_randomizer_values(SIN_LAYERS)

IP = '127.0.0.1'
PORT = 5700

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

capabilities = ["accelerometer", "button_1"]

timestamp_begin = time.time()
while True:
    time_since_initialization = time.time() - timestamp_begin
    measures = generate_values(time_since_initialization)
    message = json.dumps(measures)
    print(message)
    
    sock.sendto(message.encode(), (IP, PORT))
    time.sleep(0.01)



