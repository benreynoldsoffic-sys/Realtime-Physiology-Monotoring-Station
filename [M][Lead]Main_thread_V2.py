import numpy as np
import pandas as pd
import neurokit2 as nk
import matplotlib.pyplot as plt
from threading import Thread, Lock
import time

global TERMINATE
# Setting Global variables for data input, this

def ECG_features(thread_ret,index_ret,Data):
    """
    ----Description:
        This function leverages the neurokit 2 function ecg_peaks in 
        order to examine key features. The list of possible extractable 
        features are as follows: 
            HRV_MeanNN, HRV_SDNN, HRV_SDANN1, HRV_SDNNI1, HRV_SDANN2,   
            HRV_SDNNI2, HRV_SDANN5, HRV_SDNNI5, HRV_RMSSD, HRV_SDSD, HRV_SampEn,    
            HRV_ShanEn, HRV_FuzzyEn, HRV_MSEn, HRV_CMSEn, HRV_RCMSEn, HRV_CD, 
            HRV_HFD, HRV_KFD, HRV_LZC.
    ----Parameters:
        Full data set, though it can also handle just ECG data
    ----Returns:
        Selected ECG Features: RMSSD, SDNN, pNN50
    """
    # Lock the data array to prevent edits during feature exstraction:
    ecg_lock.acquire()
    cont = True
    hold = time.time()
    while cont:
        if Data == TERMINATE: cont = False
        else: 
            # Lock the data array to prevent edits during feature exstraction:
            ecg_lock.acquire()
            # Find peaks
            peaks,_ = nk.ecg_peaks(Data, sampling_rate=100)

            # Compute HRV indices
            
            Ret_hrv = nk.hrv(peaks, sampling_rate=100, show=False)
            thread_ret[index_ret] = [Ret_hrv["HRV_RMSSD"],Ret_hrv["HRV_SDNN"],Ret_hrv["HRV_pNN50"]]
            
            ecg_lock.release()
            time.sleep(0.01)
        

        # Setting automatic emergency completion, specifically fo if the thread goes rouge
        # it will always terminate regardless of any other termination sequences
        if (time.time()-hold) > 5:
            cont = False

    return 

def EDA_features(thread_ret,index,Data):
    """
    ----Description:
        This function leverages the neurokit 2 function eda_phasic in 
        order to examine key features. The list of possible extractable 
        features are as follows: 
            EDA_Phasic, EDA_Tonic
            
    ----Parameters:
         Full data set, though it can also handle just EDA data

    ----Returns:
        Selected EDA features:
        - Tonic:  Mean, Min, Max
        - Phasic: Mean, Min, Max
    """
    EDA_phasic_tonic  = nk.eda_phasic(nk.standardize(Data), sampling_rate=250)

    EDA_phasic = np.array(EDA_phasic_tonic["EDA_Phasic"])
    EDA_tonic  = np.array(EDA_phasic_tonic["EDA_Tonic"])
    
    thread_ret[index] = [EDA_tonic.mean(),EDA_tonic.min(),EDA_tonic.max(),EDA_phasic.mean(),EDA_phasic.min(),EDA_phasic.max()]
    return 

def RSP_features(thread_ret,index,Data,t=60*8):
    """
----Description:
        This function leverages the neurokit 2 function ecg_peaks in 
        order to examine key features. The list of possible extractable 
        features are as follows: 
            RSP_Raw, RSP_Clean, RSP_Peaks, RSP_Troughs, RSP_Rate, RSP_Amplitude
            RSP_Phase, RSP_Phase_Completion, RSP_RVT
            
----Parameters:
        Full data set, though it can also handle just ECG data

----Returns:
        Selected ECG Features: RMSSD, SDNN, pNN50
    """
    # Extract rsp
    signals,_ = nk.rsp_process(Data, sampling_rate=100)
    # Break up rsp features
    rsp_rate = np.array(signals["RSP_Rate"])
    rsp_amplitude = np.array(signals["RSP_Amplitude"])
    # Send data back
    thread_ret[index] = [(rsp_rate.sum()/t),np.median(rsp_amplitude)]
    return 


if __name__ == "__main__":
    
    # Setting global locks
    global ecg_lock
    global eda_lock
    global rsp_lock
    
    # Setting global data 
    global ecg_data
    global eda_data
    global rsp_data
    
    # Deffining global locks
    ecg_lock = Lock()
    eda_lock = Lock()
    rsp_lock = Lock()
    
    # Deffining global states
    TERMINATE = "TERMINATE"
    
    # Setting counters to trak number of active threads (c_thread)
    # and debuging counter for error determination (step)
    c_thread = 0
    step = 0
    
    # Cycle the Exstraction functions
    name_feat = [ECG_features,EDA_features,RSP_features]
    type_feat = ["ECG","EDA","RSP"]
    
    # Initialize thread support variables
    threads = []
    thread_ret = [None] * 3
    
        # Generating ECG temporary data files and testing lock
    ecg_lock.acquire()
    ecg_data = []
    eda_lock.acquire()
    eda_data = []
    rsp_lock.acquire()
    rsp_data = []
    
        # Unlocking data files for examination
    ecg_lock.release()
    eda_lock.release()
    rsp_lock.release()
    
    data_full = [] * 3
    # Load & Split test data
    split_dfs = np.array_split(nk.data("bio_resting_8min_100hz"), 3, axis=0)
    for count in range(0,2):
        data_1 = pd.DataFrame(split_dfs[0][type_feat[count]])
        data_2 = pd.DataFrame(split_dfs[1][type_feat[count]])
        data_3 = pd.DataFrame(split_dfs[2][type_feat[count]])
        data_full[count] = [data_1,data_2,data_3]
        # print(data_1.info())

# ##__Step 1/2: Generating threads__##

#     # Generating ECG temporary data files and testing lock
#     ecg_lock.acquire()
#     ecg_data = []
#     eda_lock.acquire()
#     eda_data = []
#     rsp_lock.acquire()
#     rsp_data = []
    
#     # Unlocking data files for examination
#     ecg_lock.release()
#     eda_lock.release()
#     rsp_lock.release()

#     t_feat = Thread(target=name_feat[0], args=(thread_ret,0,ecg_data,),daemon=True)
#     threads.append(t_feat)
#     print("Success...Created Thread 1 | ECG")
    
#     # Generating EDA examiner thread
#     t_feat = Thread(target=name_feat[1], args=(thread_ret,1,eda_data,),daemon=True)
#     threads.append(t_feat)
#     print("Success...Created Thread 2 | EDA")
    
#     # Generating RSP examiner thread
#     t_feat = Thread(target=name_feat[2], args=(thread_ret,2,rsp_data,),daemon=True)
#     threads.append(t_feat)
#     print("Success...Created Thread", count," | ", )


#     for c in range(0,2):
# ##__Step 5/6: Load next set of data__##
#         # Wait for all threads to complete their examination then lock them before
#         # moving onto loading the next set of data
#         ecg_lock.acquire()
#         eda_lock.acquire()
#         rsp_lock.acquire()
        
#         # Load the next set of data 
#         ecg_data = ecg_total[c]
#         eda_data = eda_total[c]
#         rsp_data = rsp_total[c]
        
#         # Release the locks and allow the next set of data to be examined
#         ecg_lock.release()
#         eda_lock.release()
#         rsp_lock.release()
        
# ##__Step 3/4: Start all threads__##
#         if c == 0: 
#             for t in threads: t.start()
#             ecg_lock.acquire()
#         eda_lock.acquire()
#         rsp_lock.acquire()
        
#         # Load the next set of data 
#         ecg_data = ecg_total[c]
#         eda_data = eda_total[c]
#         rsp_data = rsp_total[c]
        
#         # Release the locks and allow the next set of data to be examined
#         ecg_lock.release()
#         eda_lock.release()
#         rsp_lock.release()


# #     # Wait for other programs to complete before continuing to next round of data
# #     while ecg_lock.locked(): 
# #         ecg_lock.acquire()
        
# #         ecg_lock.release()

# #     s_time = time.time()
# #     # Step 5/6: Wait for all threads to complete and 
# #     for t in threads:
# #         t.join()
# #         print("Terminated Thread:", c_thread)
# #         c_thread = c_thread - 1
# #     e_time = time.time()

# #     # Threading is now done moving to data exstraction and examination:
# #     # print("Return:",thread_ret[0])
# #     # print("Return:",thread_ret[1])
# #     print("Return:",thread_ret[2])

# #     # Print the updated array
# #     print("Updated array:", threads)
# #     # Print the updated array
# #     print("Updated array:", (e_time-s_time))