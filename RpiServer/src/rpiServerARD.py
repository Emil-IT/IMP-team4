import serial

class RpiServerARD():
    """docstring for RpiServerARD"""
    def __init__(self, parent):
        self.parent = parent
        incoming = ""
        ser = serial.Serial('/dev/rfcomm1', 9600)
        print('Opened connection on port %s' %ser.name)
        while True:
            incoming = ser.readline().decode()
            self.parent.sensorJSON = incoming
        
        
        
