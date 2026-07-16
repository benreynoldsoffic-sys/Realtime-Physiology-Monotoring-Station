import numpy as np
import neurokit2 as nk
import matplotlib.pyplot as plt

def RSP_features(Data,t):
    """
----Description:
        This function leverages the neurokit 2 function ecg_peaks in 
        order to exstract key features. The possible exstractable values are as
        follows: 
            RSP_Raw, RSP_Clean, RSP_Peaks, RSP_Troughs, RSP_Rate, RSP_Amplitude
            RSP_Phase, RSP_Phase_Completion, RSP_RVT
            
----Parameters:
        Full data set, though it can also handle just ECG data

----Returns:
        Selected ECG Features: RMSSD, SDNN, pNN50
    """
    # Extract rsp
    signals,_ = nk.rsp_process(Data["RSP"], sampling_rate=100)
    
    # Break up rsp features
    rsp_rate = np.array(signals["RSP_Rate"])
    rsp_amplitude = np.array(signals["RSP_Amplitude"])

    return [(rsp_rate.sum()/t)]

## Example Main: ##
# # Get data: Given in Neurokit2 examples Link bellow:
# #       https://pypi.org/project/neurokit2/
# data = nk.data("bio_resting_8min_100hz")
# plt.plot(RSP_features(data,60*8))
# plt.show()
