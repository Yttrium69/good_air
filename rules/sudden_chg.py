
from sklearn.base import BaseEstimator, TransformerMixin
from typing import List
import numpy as np
import pandas as pd

class Sudden_chg(BaseEstimator, TransformerMixin):
    SENSOR_LIST=['SO2', 'CO', 'O3', 'PM10', 'PM25', 'NO', 'NO2', 'NOX']
    WRONG_CODE=-99
    KEYWORD='Sudden_Chg'
    def __init__(self,
                k,
                threshold,
                key,
                labels:List=None):
        """[detect one element's same value persistence ]
        Args:
            threshold (double) : threshold value, if not pass this argument, 
                                call setVar method to calculate threshold value
            labels (List, optional): 
                    [Dectiting List]. Defaults to None.
                    ex) ["SO2", "CO2", "O3"]
        Returns:
            "array" of int : if detect error, than value of index is 2. (normal value is 0)
        """
        if labels == None:
            self.labels_ = {"SO2_CODE":None,"CO_CODE":None, "O3_CODE":None, "PM10_CODE":None, 
                            "PM25_CODE":None, "NO_CODE":None, "NO2_CODE":None, "NOX_CODE":None}
        else:
            self.labels_ = {i:None for i in labels}
        
        self.k = k
        self.thres = threshold

    def fit(self, X, y=None):
        return self
    
    def transform(self, X, y = None):
        if isinstance(X, pd.DataFrame):
            for elem in Sudden_chg.SENSOR_LIST:    
                elem_code = np.zeros(shape=X.shape[0], dtype=np.int8)
                if f'{elem}_CODE' in X.keys():
                    elem_code = X[f'{elem}_CODE']
                T = X[elem].to_numpy()
                T = np.where(T==np.nan, 0, T)
                t1 = np.zeros(T.shape)
                t2 = np.zeros(T.shape)
                t1[1:] = abs(T[1:] - T[:-1])
                t2[:-1] = abs(T[:-1] - T[1:])
                t = (t1 + t2) / 2

                if self.thres == 0:
                    var = np.nanvar(t, axis=0) #ddof = 0
                    std = np.sqrt(var)
                    mean = np.nanmean(t)
                    tt = self.k * std + mean
                else:
                    tt = self.thres
                
                elem_code= np.where(t>tt,
                                    Sudden_chg.WRONG_CODE,
                                    elem_code)
                
                X[f'{elem}_CODE'] = elem_code
            
            return X
        else:
            raise TypeError("Please Type Check!")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()  
    parser.add_argument('--data', type=str, default='../test.txt')
    args = parser.parse_args()
    
    def load_data(path):
        data = pd.read_csv(path, delimiter=',')
        key_list = np.unique(data['AREA_INDEX'].to_numpy())
        print(f'number of detected keys: {len(key_list)}')
        return key_list, data
    
    key_list, data = load_data(args.data)
    
    for key in key_list:
        print(f'{key} proccessing...')
        key_data = data[data['AREA_INDEX'] == key].reset_index()
        rule_detecter = Sudden_chg(threshold=10)
        
        t = rule_detecter.fit_transform(key_data)
        print(t)