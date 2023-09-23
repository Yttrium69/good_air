from sklearn.base import BaseEstimator, TransformerMixin
import pandas as pd
import numpy as np
from typing import List

class Reverse_pm(BaseEstimator, TransformerMixin):
    SENSOR_LIST=['PM10', 'PM25']
    WRONG_CODE=-99
    KEYWORD='Reverse_PM'
    def __init__(self,
                key,
                high_c:int=35,
                high_margin:int=10,
                low_c:int=10,
                low_margin:int=5):
        """[detect PM10, PM2.5 reverse]
            PM reversal anomaly detection can be divided into two cases as follows.
            The first is that when fine dust is at a high concentration, 
            pm10 is considered a low concentration (less than 35), and 
            if it is less than PM2.5 with a margin of about 10, it is considered a reversal.
            
            Second, if PM10 is at a high concentration, 
            put a margin of about 5 to see the PM reversal. 
            
            At this time, the abnormal code is set to 4.
        Args:
            high_c (int, optional): [description]. Defaults to 35.
            high_margin (int, optional): [description]. Defaults to 10.
            low_c (int, optional): [description]. Defaults to 10.
            low_margin (int, optional): [description]. Defaults to 5.
        """
        self.labels_ = {"PM10_CODE":None, "PM25_CODE":None}
        
        self.high_c_ = high_c
        self.high_margin_ = high_margin
        
        self.low_c_ = low_c
        self.low_margin_ = low_margin
    
    def fit(self, X, y=None):
        return self
    
    def transform(self, X, y = None):
        if isinstance(X, pd.DataFrame):
            for elem in self.SENSOR_LIST:    
                elem_code = np.zeros(shape=X.shape[0], dtype=np.int8)
                if f'{elem}_CODE' in X.keys():
                    elem_code = X[f'{elem}_CODE']
                X[f'{elem}_CODE'] = elem_code
        else:
            raise TypeError("Please Type Check!")

        tmp_X = X[X['PM10'] != 0].copy()
        idx = tmp_X[(tmp_X['PM10'] > self.high_c_) & (tmp_X['PM25'] > tmp_X['PM10'] + self.high_margin_)].index
        idx2 = tmp_X[(tmp_X['PM10'] <= self.high_c_) & (tmp_X['PM25'] > tmp_X['PM10'] + self.low_margin_)].index
        X.loc[idx.append(idx2), ['PM10_CODE', 'PM25_CODE']] = self.WRONG_CODE
        
        return X

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
        rule_detecter = Reverse_pm()
        
        t = rule_detecter.fit_transform(key_data)