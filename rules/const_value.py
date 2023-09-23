from os import dup
from sklearn.base import BaseEstimator, TransformerMixin
from pandas import DataFrame
from typing import List, Tuple
import numpy as np
import pandas as pd

class Ab_KeepSameValue(BaseEstimator, TransformerMixin):
    SENSOR_LIST=['SO2', 'CO', 'O3', 'PM10', 'PM25', 'NO', 'NO2', 'NOX']
    WRONG_CODE=-99
    KEYWORD='SameValue'
    def __init__(self,
                keep_time,
                key,
                labels:List=None):
        """[detect one element's same value persistence ]

        Args:
            time (int, optional): [The value of the time that is 
                                    keepping]. Defulats to 10.
            labels (List, optional): 
                    [Dectiting List]. Defaults to None.
                    ex) ["SO2_CODE", "CO2_CODE", "O3_CODE"]
        """
        if labels == None:
            self.labels_ = {"SO2_CODE":None,"CO_CODE":None, "O3_CODE":None, "PM10_CODE":None, 
                            "PM25_CODE":None, "NO_CODE":None, "NO2_CODE":None, "NOX_CODE":None}
        else:
            self.labels_ = {i:None for i in labels}
        
        self.time_ = keep_time
    
    def fit(self, X, y=None):
        return self
    
    def check_duplicated(self, a, t)->List[List[Tuple]]:
        const = (a != np.r_[a[1:], None])
        i = np.where(const)[0]
        i = np.append([0], i)
        dup_ranges = (i[1:] - i[:-1])
        dup_indices = np.where(dup_ranges >= t)[0] + 1
        ranges = np.stack([(i[dup_indices] - dup_ranges[dup_indices - 1]), i[dup_indices]]).T
        ranges += 1
        
        return ranges
    
    def transform(self, X, y = None):
        if isinstance(X, DataFrame):
            dup_list = {}
            for elem in Ab_KeepSameValue.SENSOR_LIST:
                elem_code = np.zeros(shape=X.shape[0], dtype=np.int8)
                
                if f'{elem}_CODE' in X.keys():
                    elem_code = X[f'{elem}_CODE'].to_numpy(copy=True)
                
                idx = X[X[elem] == 0].index
                tmp = X.loc[idx, [elem]].to_numpy(copy=True)
                X.loc[idx, [elem]] = 9999
                
                T = X[elem].to_numpy() #Time Split List
                dup_list[elem] = self.check_duplicated(T, self.time_)
                
                for i in dup_list[elem]:
                    #Time Laps Start~End
                    elem_code[i[0]:i[1]] = Ab_KeepSameValue.WRONG_CODE #label change
                
                X[f'{elem}_CODE'] = elem_code
                X.loc[idx, [elem]] = tmp
            return X, dup_list
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
    
    # model = Ab_KeepSameValue(cut=10)
    for key in key_list:
        print(f'{key} proccessing...')
        key_data = data[data['AREA_INDEX'] == key].reset_index()
        rule_detecter = Ab_KeepSameValue(keep_time=10)
        
        t = rule_detecter.fit_transform(key_data)