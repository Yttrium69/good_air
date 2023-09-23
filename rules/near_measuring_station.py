from tkinter import N
from sklearn.base import BaseEstimator, TransformerMixin
from pandas import DataFrame
from typing import List, Tuple, Type
import numpy as np
import pandas as pd

class Near_measuring_station(BaseEstimator, TransformerMixin):
    SENSOR_LIST=['SO2', 'CO', 'O3', 'PM10', 'PM25', 'NO', 'NO2', 'NOX']
    WRONG_CODE=-99
    KEYWORD='Near_Station'
    def __init__(self,
                data,
                N,
                key,
                near_list,
                diff_rate:float = 2.7,
                labels:List=None):
        """[summary]
        Args:
            diff_rate (float, optional): different rate to think of abnormal. Defaults to 2.3.
        """
        self.N = N
        self.target = key

        self.main_data = {}
        for key in np.unique(data['AREA_INDEX'].to_numpy()):
            self.main_data[key] = data[data['AREA_INDEX'] == key].sort_values(by=['MDATETIME']).reset_index()

        if labels == None:
            self.labels_ = {"SO2_CODE":None,"CO_CODE":None, "O3_CODE":None, "PM10_CODE":None, 
                            "PM25_CODE":None, "NO_CODE":None, "NO2_CODE":None, "NOX_CODE":None}
        else:
            self.labels_ = {i:None for i in labels}
    
    def load_area_specification(self, path):
        spec = pd.read_excel(path)
        spec.columns = ['State', 'City', 'Code', 'Name', 'Adress', 'X', 'Y', 'Info']
        road_idx = spec[spec['State'] == '[도로변대기측정망]'].index[0]
        end_idx = spec[spec['State'] == '[국가배경농도측정망]'].index[0]
        idx = spec['Adress'].dropna().index
        spec = spec.loc[idx].drop([2, road_idx + 2])

        idx = spec[spec['Name'] == '(이전)'].index
        moved_point = spec.loc[idx][['X', 'Y']].to_numpy()
        spec.loc[(idx - 1), ['X', 'Y']] = moved_point
        spec = spec.drop(idx)
        spec = spec.loc[:end_idx]
        spec = spec.drop(spec[spec['Code'].isna()].index)
        spec['Code'] = spec['Code'].astype(int)

        city = spec.loc[:road_idx].reset_index()
        road = spec.loc[road_idx:].reset_index()

        return city, road
    
    def load_area_site(self, path):
        spec = pd.read_csv(path, encoding='cp949')
        spec = spec.rename(columns={'LL_TUDE_X':'X', 'LL_TUDE_Y':'Y', 'AREA_INDEX':'Code'})
        spec['Code'] = spec['Code'].astype(int)
        return spec

    def fit(self, X, y=None):
        return self
    
    def transform(self, X, y=None):
        if isinstance(X, DataFrame):
            key = int(X['AREA_INDEX'][0])
            area_type, key_X, key_Y = self.area_info[self.area_info['Code'] == key][['AREA_TYPE', 'X', 'Y']].to_numpy()[0]
            if area_type == '도시대기':
                target_points = self.area_info[self.area_info['AREA_TYPE'] == '도시대기'][['Code', 'X', 'Y']]
            elif area_type == '교외대기':
                target_points = self.area_info[self.area_info['AREA_TYPE'].isin(['교외대기', '국가배경', '도시대기'])][['Code', 'X', 'Y']]
            elif area_type == '국가배경':
                target_points = self.area_info[self.area_info['AREA_TYPE'].isin(['교외대기', '국가배경', '도시대기'])][['Code', 'X', 'Y']]
            elif area_type == '항만':
                target_points = self.area_info[self.area_info['AREA_TYPE'].isin(['항만', '교외대기', '도시대기'])][['Code', 'X', 'Y']]
        
            # if key in self.area_info_city['Code'].to_numpy():
            #     key_X, key_Y = self.area_info_city[self.area_info_city['Code'] == key][['X', 'Y']].to_numpy()[0]
            #     target_points = self.area_info_city[['Code', 'X', 'Y']].reset_index()
            # elif key in self.area_info_road['Code'].to_numpy():
            #     key_X, key_Y = self.area_info_road[self.area_info_road['Code'] == key][['X', 'Y']].to_numpy()[0]
            #     target_points = self.area_info_road[['Code', 'X', 'Y']].reset_index()
            # else:
            #     return X

            try:
                target_points.loc[:, 'X'] = target_points['X'].astype(float)
                target_points.loc[:, 'Y'] = target_points['Y'].astype(float)
                target_points.loc[:, 'X'] -= key_X
                target_points.loc[:, 'Y'] -= key_Y

                target_points['dist'] = (target_points['X'] ** 2 + target_points['Y'] ** 2) ** 0.5
                target_points = target_points[target_points['dist'] < self.rng]
                target_points = target_points.sort_values('dist')
            except:
                return X
            
            sort_near = target_points[['Code', 'dist']].to_numpy()
            cnt = 0
            near_area = []
            for near_key, dist in sort_near[1:]:
                if cnt >= self.k:
                    break
                if dist > self.rng:
                    break
                if int(near_key) in self.main_data.keys():
                    near_area.append(near_key)
                    cnt += 1
            if len(near_area) == 0:
                return X
            # near_area = sort_near[1:self.k + 1, 0].astype(int)

            tmp = DataFrame()
            for near_key in near_area:
                if not near_key in self.main_data:
                    continue
                if tmp.empty:
                    tmp[Near_measuring_station.SENSOR_LIST] = self.main_data[near_key][Near_measuring_station.SENSOR_LIST]
                else:
                    tmp[Near_measuring_station.SENSOR_LIST] += self.main_data[near_key][Near_measuring_station.SENSOR_LIST]
            tmp /= len(near_area)
            for key in Near_measuring_station.SENSOR_LIST:
                X[key + '_CODE'] = np.where(tmp[key] > X[key] * self.diff_rate, Near_measuring_station.WRONG_CODE, 0)
                X[key + '_CODE'] = np.where(tmp[key] < X[key] * (1 /self.diff_rate), Near_measuring_station.WRONG_CODE, X[key + '_CODE'])
            return X
        else:
            raise TypeError("Please Type Check!")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', type=str, default='../as_hour_2020.txt')
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
        rule_detecter = Near_measuring_station(data = data)
        
        t = rule_detecter.fit_transform(key_data)