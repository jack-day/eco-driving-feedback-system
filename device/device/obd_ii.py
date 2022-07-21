"""
OBD-II Connection and Emulation

Provides an OBD-II connection based on the 'obd' value in the config.ini. If it
is set to 'emulated', a connection will be emulated using Assetto Corsa
to supply the simulted data. Otherwise the OBD-II connection will be provided
using the python-obd library.
"""
import socket
import json
import obd
from config import CONFIG

SERVER_HOST = CONFIG['emulatedOBDServerHost']
SERVER_PORT = int(CONFIG['emulatedOBDServerPort'])
HEADER_SIZE = 64
ENCODING = 'utf-8'


# Emulation client
# -------------------------------------------------------------------------
class EmulatorClient:
    """Emulator client to request data from the OBD2 Assetto Corsa app"""

    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((SERVER_HOST, SERVER_PORT))
        self.connected = True

    def disconnect(self):
        """Disconnects from the OBD2 AC app"""
        self.send('!disconnect')

    # Sending and receiving socket messages
    # - Messages are sent in two parts:
    #     1. Header - With it's size fixed to HEADER_SIZE,
    #        it contains the length of the data message to be sent
    #     2. Message - The actual data
    # -------------------------------------------------------------------------
    def send(self, data):
        """Sends socket messages to the OBD2 AC app"""
        msg = str(data).encode(ENCODING)
        msgLen = len(msg)

        header = str(msgLen).encode(ENCODING)
        # Pad the header to ensure it meets the set header size
        header += b' ' * (HEADER_SIZE - len(header))

        self.client.send(header)
        self.client.send(msg)

    def recv(self):
        """Receives socket messages from the OBD2 AC app"""
        msgLen = self.client.recv(HEADER_SIZE).decode(ENCODING)
        if not msgLen:
            return

        msgLen = int(msgLen)
        msg = self.client.recv(msgLen).decode(ENCODING)
        return msg

    # Retrieve OBD data from Assetto Corsa
    # -------------------------------------------------------------------------
    def query(self, pid):
        """Sends PID requests to retreive
        simulated data from the OBD2 AC app"""
        if not self.connected:
            return 'disconnected'
        self.send(pid)
        return self.recv()


# OBD Connection Emulation
# -------------------------------------------------------------------------
class EmulatedOBD:
    """Emulated OBD-II connection,
    acts the same as the OBD class from python-obd"""

    def __init__(self):
        self.emulator = EmulatorClient()

    def status(self):
        """Returns the OBD connection status"""
        if self.emulator.connected is True:
            return obd.OBDStatus.CAR_CONNECTED
        else:
            return obd.OBDStatus.NOT_CONNECTED

    @property
    def is_connected(self):
        """Returns whether a connection is established with the vehicle"""
        return self.status() == obd.OBDStatus.CAR_CONNECTED

    def close(self):
        """Closes the OBD connection"""
        self.emulator.disconnect()

    def query(self, cmd, force=False):
        """Primary API function, sends commands to the car"""
        msg = self.emulator.query(cmd.pid)

        if msg:
            val = json.loads(msg)
            response = obd.OBDResponse(cmd, {'data': val})
            response.value = val
            return response
        else:
            raise BrokenPipeError


# OBD connection
# -------------------------------------------------------------------------
def OBDConnect():
    """Opens a connection to the OBD interface"""
    return EmulatedOBD()
