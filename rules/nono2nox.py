from sklearn.base import BaseEstimator, TransformerMixin
from typing import List, Tuple
import numpy as np
import pandas as pd


class NoNo2Nox(BaseEstimator, TransformerMixin):
    SENSOR_LIST=['NO', 'NO2', 'NOX']
    WRONG_CODE = -99
    KEYWORD='NO_Ratio'
    def __init__(self,
                key,
                margin:float = 0.005):
        """[summary]
        Args:
            margin (float, optional): It gonna be used for customizing detect marginal value. Defaults to 0.005.
        """
        self.margin_ = margin

    def fit(self, X, y=None):
        return self
    
    def transform(self, X, y = None):
        if isinstance(X, pd.DataFrame):
            for elem in NoNo2Nox.SENSOR_LIST:    
                elem_code = np.zeros(shape=X.shape[0], dtype=np.int8)
                if f'{elem}_CODE' in X.keys():
                    elem_code = X[f'{elem}_CODE']
                X[f'{elem}_CODE'] = elem_code
        else:
            raise TypeError("Please Type Check!")
        
        NO = X['NO'].to_numpy()
        NO = np.where(NO==np.nan, 0, NO)
        NO2 = X['NO2'].to_numpy()
        NO2 = np.where(NO2==np.nan, 0, NO2)
        NOX = X['NOX'].to_numpy()
        NOX = np.where(NOX==np.nan, 0, NOX)
        
        elem_code = np.where(np.add(NO2, NO) >= NOX+self.margin_, 
                                    NoNo2Nox.WRONG_CODE, 
                                    X[f'{elem}_CODE'])
        
        for elem in NoNo2Nox.SENSOR_LIST:
            X[f'{elem}_CODE'] = elem_code
            
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
        rule_detecter = NoNo2Nox()
        
        t = rule_detecter.fit_transform(key_data)
        print(t[['NO', 'NO2', 'NOX', 'NO_CODE']])