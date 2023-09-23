from textwrap import indent
from sklearn.base import BaseEstimator, TransformerMixin
from typing import List
import numpy as np
import pandas as pd

class Rule_combiner(BaseEstimator, TransformerMixin):
    def __init__(self,
                wrong_code,
                rules,
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
        
        self.code = wrong_code
        self.rules = rules
        self.sensor_list = []


    def fit(self, X, y=None):
        return self
    
    def transform(self, X, y = None):
        if isinstance(X, pd.DataFrame):
            _min = 33
            for rule in self.rules:
                if len(rule.SENSOR_LIST) < _min:
                    self.sensor_list = rule.SENSOR_LIST
                    _min = len(self.sensor_list)

            cds = {}
            for elem in self.sensor_list:
                cds[elem] = []
            
            SAME_FLAG = False
            for (i, rule) in enumerate(self.rules):
                try:
                    if rule.KEYWORD == 'SameValue':
                        TMP, dup_list = rule.fit_transform(X.copy())
                        SAME_FLAG=True
                    else:
                        TMP = rule.fit_transform(X.copy())
                    
                    for elem in self.sensor_list:
                        cd = list(TMP[TMP[f'{elem}_CODE'] == -99].index)
                        cds[elem].append(cd)
                except Exception as e:
                    print('Error : ', e)
                    pass

            for elem in self.sensor_list:
                indices = []
                for i in range(0, len(cds[elem])):
                    if SAME_FLAG:
                        for dup in dup_list[elem].copy():
                            tmp = list(set(cds[elem][i]).intersection(range(dup[0], dup[1])))
                            if len(tmp) > ((dup[1] - dup[0]) / 2):
                                pass
                            else:
                                try:
                                    dup_list.remove(dup)
                                except:
                                    pass
                    else:
                        if i == 0:
                            continue
                        if i == 1:
                            indices = list(set(cds[elem][0]).intersection(cds[elem][1]))
                        else:
                            indices = list(set(indices).intersection(cds[elem][i]))
            
                if len(cds[elem]) == 1:
                    X.loc[cds[elem][0], f'{elem}_CODE'] = self.code
                else:
                    if SAME_FLAG:
                        for dup in dup_list[elem]:
                            X.loc[list(range(dup[0], dup[1])), f'{elem}_CODE'] = self.code
                    else:
                        X.loc[indices, f'{elem}_CODE'] = self.code
            return X
        else:
            raise TypeError("Please Type Check!")