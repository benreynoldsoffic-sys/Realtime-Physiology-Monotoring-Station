"""
Created on Tue Jul  6 12:38:00 2021 by Greg Bales
https://github.com/greg1877/Trust_LSL

Modified 4/02/2025 by Benjamin reynolds

@author: GB_SurfaceBook
"""
import biopacndt_B as biopacndt # Module to interact with BIOPAC hardware
import sys
import time
from datetime import datetime
import socket  # Module for handling socket programming
import time

# Biopac Specific constants
srate = 2000  # Sampling rate (in Hz)
rest_time = 1 / srate  # Rest period between samples based on sampling rate

# Function to send BIOPAC data to the connected client
def send_biopac_data(data, client_socket,srate=2000):
    try:

        # Format the sample as a comma-separated string for transmission
        message = ','.join(map(str, data)) + '\n'  # Access inner list
        client_socket.sendall(message.encode('utf-8'))  # Send data to client

    except KeyboardInterrupt:  # Allow graceful interruption with Ctrl+C
        print("Data streaming interrupted. Stopping...")






    """
Created on Tue Jul  6 12:38:00 2021 by Greg Bales
https://github.com/greg1877/Trust_LSL

Modified 2/14/2022 by Jacob Kintz

@author: GB_SurfaceBook
"""

srate = 2000
rest_time = 1/srate

def local_clock():
    return time.time()

class StreamData:
    def __init__(self, server):
        self.__server = server
        self.__chanData = []  # initialize the data point list of acquired amplitudes.

    def handleAcquiredData(self, hardwareIndex, frame, channelsInSlice):
        self.__chanData.append(list(frame))  # change the tuple into a list

    def returnList(self):
        lastSample = len(self.__chanData)
        if (lastSample > 1):
            return self.__chanData[lastSample - 1:]  # append the list to chanData


# Start Biopac Server
print("Attempting to connect to Acknowledge ")
acq_server = biopacndt.AcqNdtQuickConnect()
if not acq_server:
    print("Could not connect to AcqKnowledge Server ")
    sys.exit()
else:
    print("Established connection to AcqKnowledge Server")

enabledChannels = acq_server.DeliverAllEnabledChannels()  # Change if only specific channels are required
singleConnectPort = acq_server.getSingleConnectionModePort()

data_server = biopacndt.AcqNdtDataServer(singleConnectPort, enabledChannels)
stream_data = StreamData(acq_server)
print(stream_data)
data_server.RegisterCallback("OutputData", stream_data.handleAcquiredData)

# START THE SERVER
data_server.Start()
print("Aquisition server started ... wait 2 seconds ")
print(stream_data)

# %% PRINT SOME CHANNEL INFORMATION
acq_server.DeliverAllEnabledChannels()
time.sleep(2)
HOST = 'localhost'
PORT = 12345
# Create a TCP socket for the server
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))  # Bind the socket to the specified host and port
server_socket.listen(1)  # Listen for incoming connections (max 1 client at a time)
print(f"Server listening on {HOST}:{PORT}")

# Accept a client connection
client_socket, client_address = server_socket.accept()


# Create BIOPAC Stream
start_time = time.time()
sent_samples = 0


try:
    while True:
        elapsed_time = local_clock() - start_time
        required_samples = int(srate * elapsed_time) - sent_samples
        if required_samples > 0:
            for sample_ix in range(1):
                # get sample from BIOPAC stream
                print(stream_data)

                temp = stream_data.returnList()
                if temp is None:
                    mysample = [float("nan"), float("nan"), float("nan")]
                else:
                    mysample = temp[0] # This is a hack to obtain the list within the list
                try:
                    # Start sending data to the connected client
                    send_biopac_data(mysample, client_socket,stream_data)
                except Exception as e:
                    print(f"An Error Occurred:\n {e}")  # Handle unexpected errors
                    server_socket.close()  # Close the server socket
                    client_socket.close()  # Close the client socket
                    sys.exit()

                sent_samples += required_samples
            # now send it and wait for a bit before trying again.

            # 4/4/2022 - Greg had this sleep timer in his original code, but we found it broke the sample rate
            # (got values around 700 Hz instead of 2000 Hz) so we have removed it. Does not seem to be
            # causing any issues for now without the sleep timer
            # time.sleep(rest_time)  #The sleep time is 1/srate
except KeyboardInterrupt:
    data_server.Stop()
    print("Stopping the data server ")
    time.sleep(2)
    print("Cleaning up...")
    del data_server
    del stream_data
    del acq_server
    print("All Finished ")
# %%
