"""
Created on Tue Jul  6 12:38:00 2021 by Greg Bales
https://github.com/greg1877/Trust_LSL

Modified 2/14/2022 by Jacob Kintz

@author: GB_SurfaceBook
"""
import biopacndt
import sys
import time
from datetime import datetime
from pylsl import StreamInfo, StreamOutlet, local_clock

srate = 2000
rest_time = 1/srate

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
data_server.RegisterCallback("OutputData", stream_data.handleAcquiredData)

# START THE SERVER
data_server.Start()
print("Aquisition server started ... wait 2 seconds ")

# %% PRINT SOME CHANNEL INFORMATION
acq_server.DeliverAllEnabledChannels()
time.sleep(2)


# Create BIOPAC Stream

# %% STREAM INFORMATION
name = 'Biopac Data'
stream_type = 'PsychoPhys'
n_channels = 3
channel_names = ["EDA", "ECG", "RSP"]
help_string = 'SendData.py -s <sampling_rate> -n <stream_name> -t <stream_type>'
stream_info = StreamInfo(name, stream_type, n_channels, srate, 'float32', 'myuid33333')
stream_outlet = StreamOutlet(stream_info)

# Send data

start_time = local_clock()
sent_samples = 0

try:
    while True:
        elapsed_time = local_clock() - start_time
        required_samples = int(srate * elapsed_time) - sent_samples
        if required_samples > 0:
            #4/24/22 - had for range(required_samples). Would occasionally have the elapsed time be not often and
            # end up having reqired samples >>1. This would waste a bunch of time sending 30+ samples back to back 
            # at basically the same time and also make sent sample extrememly large cause it to have to wait a while
            # before sending having required samples be back to >1 
            #for sample_ix in range(required_samples):
            for sample_ix in range(1):
                # get sample from BIOPAC stream
                temp = stream_data.returnList()
                if temp is None:
                    mysample = [float("nan"), float("nan"), float("nan")]
                else:
                    mysample = temp[0] # This is a hack to obtain the list within the list
                stream_outlet.push_sample(mysample)
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
