import socket 
import time
import json
import random, math


SIN_LAYERS = 8000

BUTTON_THRESHOLD:float = 0.75
ACCEL_OFFSET_X:float = random.randint(0, 65536)
ACCEL_OFFSET_Y:float = random.randint(0, 65536)
ACCEL_OFFSET_Z:float = random.randint(0, 65536)

ACCEL_SPEED = 0.5
ACCEL_BIAS = 0.1


BUTTON_SPEED = 7
BUTTON_BIAS = 1.0

AMPLITUDE_BIAS = 1.2
FREQUENCY_EXPONENT = 3.6
FREQUENCY_BIAS = 0.00003
#chooses the right function for the job.
def get_value(capability:str, time:float):
    if capability == "accelerometer":
        return get_value_accelerometer(time)
    elif capability == "button_1":
        return get_value_button(time)

#generates accelerometer data
def get_value_accelerometer (time:float):

    

    values = {}
    values["x"] = get_layered_sin_value(time, ACCEL_OFFSET_X, ACCEL_SPEED, ACCEL_BIAS)
    values["y"] = get_layered_sin_value(time, ACCEL_OFFSET_Y, ACCEL_SPEED, ACCEL_BIAS)
    values["z"] = get_layered_sin_value(time, ACCEL_OFFSET_Z, ACCEL_SPEED, ACCEL_BIAS)
    return values

#generates button data
def get_value_button(time:float):
    value = get_layered_sin_value(time, speed=BUTTON_SPEED, bias=BUTTON_BIAS)
    if value > BUTTON_THRESHOLD:
        return 1
    else:
        return 0

def generate_values(time:float):
    
    measures = {}
    for capability in capabilities:
        value = get_value(capability, time)
        measures[capability] = value
    return measures

def get_layered_sin_value(time:float, offset:float=0, speed:float=1.0, bias:float=1.0):
    value = 0
    time = time * speed
    for fractal_sin in sin_functions:
        value += fractal_sin(time+offset)
    return value * bias

def initialize_randomizer_values(sin_layers:int):
    for i in range(sin_layers):
        
        #amplitude = 1/((i+2))#*AMPLITUDE_BIAS)
        #amplitude = 1/sin_layers
        amplitude = 1/math.log(sin_layers)
        frequency = random.random() * (i+1) * FREQUENCY_BIAS
        x_shift = random.random() * 2 * math.pi
        layered_sin_function = lambda x : math.sin( frequency * x + x_shift) * amplitude
        sin_functions.append(layered_sin_function)
sin_functions = []

initialize_randomizer_values(SIN_LAYERS)

IP = '127.0.0.1'
PORT = 5700

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

capabilities = ["accelerometer", "button_1"]

persistent_data = {}

if "accelerometer" in capabilities:
    persistent_data["accel_from_point"] = None 
    persistent_data["accel_to_point"] = None
    persistent_data["accel_move_speed"] = 0
    persistent_data["accel_time_movement_start"] = 0
    pass

timestamp_begin = time.time()
while True:
    time_since_initialization = time.time() - timestamp_begin
    measures = generate_values(time_since_initialization)
    message = json.dumps(measures)
    print(message)
    
    sock.sendto(message.encode(), (IP, PORT))
    time.sleep(0.01)



