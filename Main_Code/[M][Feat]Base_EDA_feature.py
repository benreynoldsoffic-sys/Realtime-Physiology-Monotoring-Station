import numpy as np
import neurokit2 as nk
def EDA_features(Data):
    """
----Description:
        This function leverages the neurokit 2 function eda_phasic in 
        order to exstract key features. The possible exstractable values are as
        follows: 
            EDA_Phasic, EDA_Tonic
            
----Parameters:
        Full data set, though it can also handle just EDA data

----Returns:
        Selected EDA features:
        - Tonic:  Mean, Min, Max
        - Phasic: Mean, Min, Max
    """
    EDA_phasic_tonic  = nk.eda_phasic(nk.standardize(Data["EDA"]), sampling_rate=250)

    EDA_phasic = np.array(EDA_phasic_tonic["EDA_Phasic"])
    EDA_tonic  = np.array(EDA_phasic_tonic["EDA_Tonic"])
    

    return [EDA_tonic.mean(),EDA_tonic.min(),EDA_tonic.max(),EDA_phasic.mean(),EDA_phasic.min(),EDA_phasic.max()]
