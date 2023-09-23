# from pytest import param
from sklearn.pipeline import Pipeline
import numpy as np
import pandas as pd
from rules.reverse_pm import Reverse_pm
from rules.const_value import Ab_KeepSameValue
from rules.nono2nox import NoNo2Nox
from rules.sudden_chg import Sudden_chg
from rules.near_measuring_station import Near_measuring_station
from rules.rule_combiner import Rule_combiner
from Baseline import Baseline
# from baseline import BaseLine
import json

def detect(params, data, target_rules, target_key, near_list):
    item_list = ['PM10', 'PM25', 'NO', 'NO2', 'NOX', 'SO2', 'O3', 'CO']
    data = data.reset_index(drop=True).fillna(0)

    for item in item_list:
        data[item + '_CODE'] = np.zeros(data[item].size)

    rule_set = {
        'Near_Station': Near_measuring_station(
            data,
            N=params['Near_station']['x'],
            key=target_key,
            near_list=near_list
        ),
        'Sudden_Chg': Sudden_chg(
            k=params['Sudden_chg']['k'],
            threshold=params['Sudden_chg']['Threshold'],
            key=target_key
        ),
        'SameValue': Ab_KeepSameValue(keep_time=params['Same_value']['x'], key=target_key),
        'NO_rate': NoNo2Nox(key=target_key, margin=params['NO_rate']['x']),
        'Reverse_PM': Reverse_pm(
            key=target_key,
            high_c=params['PM_Reverse']['x1'],
            high_margin=params['PM_Reverse']['x2'],
            low_margin=params['PM_Reverse']['x3'],
        ),
        'BaseLine': Baseline(data = data, key=target_key)
    }
    cd = {
        'Sudden_Chg' : 2,
        'SameValue' : 1,
        'NO_rate' : 7,
        'Reverse_PM' : 4,
        'BaseLine' : 3,
        'Near_Station' : 5
    }

    rule_detecter = []
    rules = []
    for (i, step) in enumerate(target_rules):
        # if step in ['Near_Station', 'BaseLine']:
        #     continue
        # rules.append(rule_set[rule_name])
        rule_detecter.append((f'{cd[step]}', Rule_combiner(wrong_code=cd[step], rules=[rule_set[step]])))

    if len(rule_detecter) >= 1:
        rule_detecter = Pipeline(rule_detecter)

        targets = data['AREA_INDEX'].unique()

        result = []
        for key in [target_key]:
            print(f'{key} proccessing...')
            key_data = data[data['AREA_INDEX'] == key].reset_index(drop=True)

            t = rule_detecter.fit_transform(key_data)
            result.append(t)
            # except Exception as e:
            #     print(f'Exeption occured during proccessing {key}', e)
        result = pd.concat(result).reset_index(drop=True)
    else:
        result = data
    
    for item in item_list:
        idx = result[result[f'{item}_FLAG'] != 1].index
        result.loc[idx, item] = None
    result.index = pd.to_datetime(result['MDATETIME'].to_numpy(copy=True))

    return result