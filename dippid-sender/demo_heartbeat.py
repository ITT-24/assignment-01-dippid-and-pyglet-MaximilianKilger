from DIPPID import SensorUDP

# use UPD (via WiFi) for communication
PORT = 5700
sensor = SensorUDP(PORT)

def handle_hearbeat(data):
    print(data)

sensor.register_callback('heartbeat', handle_hearbeat)
