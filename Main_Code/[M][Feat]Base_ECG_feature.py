import numpy as np
import neurokit2 as nk
def ECG_features(Data):
    """
----Description:
        This function leverages the neurokit 2 function ecg_peaks in 
        order to exstract key features. The possible exstractable values are as
        follows: 
            HRV_MeanNN, HRV_SDNN, HRV_SDANN1, HRV_SDNNI1, HRV_SDANN2,	
            HRV_SDNNI2, HRV_SDANN5, HRV_SDNNI5, HRV_RMSSD, HRV_SDSD, HRV_SampEn, 	
            HRV_ShanEn, HRV_FuzzyEn, HRV_MSEn, HRV_CMSEn, HRV_RCMSEn, HRV_CD, 
            HRV_HFD, HRV_KFD, HRV_LZC.
            
----Parameters:
        Full data set, though it can also handle just ECG data

----Returns:
        Selected ECG Features: RMSSD, SDNN, pNN50
    """
    # Find peaks
    peaks, info = nk.ecg_peaks(Data["ECG"], sampling_rate=100)

    # Compute HRV indices
    
    Ret_hrv = nk.hrv(peaks, sampling_rate=100, show=True)

    return [Ret_hrv["HRV_RMSSD"],Ret_hrv["HRV_SDNN"],Ret_hrv["HRV_pNN50"]]

## Example Main: ##
# # Get data: Given in Neurokit2 examples Link bellow:
# #       https://pypi.org/project/neurokit2/
# data = nk.data("bio_resting_8min_100hz")
# ECG_features(data)
