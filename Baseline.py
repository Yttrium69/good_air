import pandas as pd
import numpy as np
import os

import torch
import torch.nn.functional as F
from sklearn.base import BaseEstimator, TransformerMixin
from typing import List, Tuple, Type
from model import Unet_1D
from scipy.stats import mode
from fastdtw import fastdtw
import pickle
import ruptures as rpt

class Baseline(BaseEstimator, TransformerMixin):
    SENSOR_LIST=['SO2', 'CO', 'O3', 'NO']
    WRONG_CODE=-99
    KEYWORD='BaseLine'
    def __init__(self,
                data,
                key,
                labels:List=None):
        """[summary]
        Args:
            diff_rate (float, optional): different rate to think of abnormal. Defaults to 2.3.
        """
        self.data_seq_len = 2160
        self.class_n = 2
        self.key = key
        with open('Specifications.pkl', 'rb') as f:
            self.groups = pickle.load(f)

        self.main_data = {}
        for key in np.unique(data['AREA_INDEX'].to_numpy()):
            self.main_data[key] = data[data['AREA_INDEX'] == key].sort_values(by=['MDATETIME'])

        if labels == None:
            self.labels_ = {"SO2_CODE":None,"CO_CODE":None, "O3_CODE":None, "PM10_CODE":None, 
                            "PM25_CODE":None, "NO_CODE":None, "NO2_CODE":None, "NOX_CODE":None}
        else:
            self.labels_ = {i:None for i in labels}

    def get_dtw(self, key, item, code):
        dtw_window_size = 6
        _item = item
        if item == 'NO':
            _item = 'NO2'
        area1, area2 = (self.groups[key][_item][0], self.groups[key][_item][1])
        if area1 == 0 or area2 == 0:
            print('unvalid near station for ', key, 'near_area :', area1, area2)
            return code, [], []
        signal = self.main_data[key][item].fillna(0).replace(999999, 0).to_numpy()
        try:
            comp_signal1 = self.main_data[area1][item].fillna(0).replace(999999, 0).to_numpy()
            comp_signal2 = self.main_data[area2][item].fillna(0).replace(999999, 0).to_numpy()
        except Exception as e:
            print('error occured during get near station values', e)
            return code, [], []

        rate = 1440
        for idx in range(0, len(signal) - rate, int(rate/2)):
            half_size = int(dtw_window_size / 2)

            tmp_signal = signal[idx:idx+rate]
            tmp_comp_signal1 = comp_signal1[idx:idx+rate]
            tmp_comp_signal2 = comp_signal2[idx:idx+rate]

            alog = rpt.Binseg(model='rbf').fit(tmp_signal)
            res = alog.predict(pen=30)
            res = [0] + res

            dtw = []
            for i in range(tmp_signal.size):
                if i < half_size:
                    dtw.append(fastdtw(tmp_signal[i:i+dtw_window_size], tmp_comp_signal1[i:i+dtw_window_size])[0])
                elif i > tmp_signal.size - half_size:
                    dtw.append(fastdtw(tmp_signal[i-dtw_window_size:i], tmp_comp_signal1[i-dtw_window_size:i])[0])
                else:
                    dtw.append(fastdtw(tmp_signal[i-half_size:i+half_size], tmp_comp_signal1[i-half_size:i+half_size])[0])
            
            dtw2 = []
            for i in range(tmp_signal.size):
                if i < half_size:
                    dtw2.append(fastdtw(tmp_signal[i:i+dtw_window_size], tmp_comp_signal2[i:i+dtw_window_size])[0])
                elif i > tmp_signal.size - half_size:
                    dtw2.append(fastdtw(tmp_signal[i-dtw_window_size:i], tmp_comp_signal2[i-dtw_window_size:i])[0])
                else:
                    dtw2.append(fastdtw(tmp_signal[i-half_size:i+half_size], tmp_comp_signal2[i-half_size:i+half_size])[0])

            for ii in range(len(res) - 1):
                tmp = dtw[res[ii]:res[ii + 1]]
                tmp2 = dtw2[res[ii]:res[ii + 1]]
                if ((tmp > np.percentile(dtw, 50)).sum() > (len(tmp) * 0.6)) & ((tmp2 > np.percentile(dtw2, 50)).sum() > (len(tmp2) * 0.6)):
                    if (code[idx + res[ii]:idx + res[ii + 1]].sum()) > ((res[ii] - res[ii + 1]) * 0.1):
                        code[idx + res[ii]:idx + res[ii + 1]] = True
                    else:
                        code[idx + res[ii]:idx + res[ii + 1]] = False
                else:
                    code[idx + res[ii]:idx + res[ii + 1]] = False

        return code, comp_signal1, comp_signal2

    def fit(self, X, y=None):
        return self
    
    def transform(self, X, y=None):
        for target in Baseline.SENSOR_LIST:
            model = torch.load(f'weights/weights_2160_all/{target}.pt')

            data = self.main_data[self.key].copy()
            # data.index = pd.to_datetime(data['MDATETIME'].to_numpy(copy=True))
            # data = data.loc[pd.to_datetime('2021-08-01 00'):]
            data_len = data['AREA_INDEX'].size

            signal = data[target].fillna(0).replace(999999, 0).to_numpy()
            # label = data[f'{target}_CODE'].to_numpy()
            # label = (label == 3)
            # if f'{target}_ai_CODE' in data.columns:
            #     label2 = data[f'{target}_ai_CODE'].to_numpy()
            #     label = label | label2
            # labels.append(label)
            signal = (signal - signal.min()) / (signal.max() - signal.min())

            prediction = []
            for i in range(0, data_len, self.data_seq_len):
                if i + self.data_seq_len < data_len:
                    input_X = torch.from_numpy(signal[i: i + self.data_seq_len]).unsqueeze(0).unsqueeze(0)
                    y_pred = model(input_X.to(device))
                    out_pred = F.softmax(y_pred, 1).detach().cpu().numpy().argmax(axis=1)
                    prediction.extend(out_pred.squeeze(0))
                else:
                    remain_len = data_len - i
                    input_X = torch.from_numpy(signal[-self.data_seq_len:]).unsqueeze(0).unsqueeze(0)
                    y_pred = model(input_X.to(device))
                    out_pred = F.softmax(y_pred, 1).detach().cpu().numpy().argmax(axis=1)
                    prediction.extend(out_pred.squeeze(0)[-remain_len:])
            
            output = output_sliding_voting(prediction, 7)
            p = (output == 0)
            p, c1, c2 = get_dtw(self.key, target, p)
            X[target + '_CODE'] = np.where(p, Baseline.WRONG_CODE, 0)
        return X

def output_sliding_voting(output,window=5):
    # window size must be odd number
    output = pd.Series(output).rolling(window).apply(lambda x : mode(x)[0][0]).fillna(method='bfill')
    return output.values

def check_duplicated(self, a, t):
    const = (a != np.r_[a[1:], None])
    i = np.where(const)[0]
    i = np.append([0], i)
    dup_ranges = (i[1:] - i[:-1])
    dup_indices = np.where(dup_ranges >= t)[0] + 1
    ranges = np.stack([(i[dup_indices] - dup_ranges[dup_indices - 1]), i[dup_indices]]).T
    ranges += 1
    
    return ranges

# seg_flielist = sorted(os.listdir(f'./air_{data_keyword}/'))
# seg_flielist = [os.path.join(f'./air_{data_keyword}', x) for x in seg_flielist]
# main_data = {}
# for f in seg_flielist:
#     X = pd.read_csv(f)
#     # X.index = pd.to_datetime(X['MDATETIME'].to_numpy(copy=True))
#     # X = X.loc[pd.to_datetime('2021-08-01 00'):]
#     X = X.sort_values(by=['MDATETIME']).reset_index()
#     main_data[X['AREA_INDEX'][0]] = X.copy()

# i = 0
# for signal, pred, filename in zip(signals, predictions, seg_flielist):
#     i += 1
#     output = output_sliding_voting(pred, 7)
#     p = (output == 0)

#     key = int(os.path.splitext(os.path.basename(filename))[0])
#     p, c1, c2 = get_dtw(key, target, p)
    
#     plt.figure(figsize = (15, 4))
#     plt.plot(c1, alpha=0.5, color = 'y')
#     plt.plot(c2, alpha=0.5, color = 'm')
#     plt.plot(signal, color = 'b')
#     idx = np.where(p)[0]
#     plt.scatter(x = idx, y = signal[idx], marker='.', color='r', s=60)
#     # idx = np.where(label)[0]
#     # plt.scatter(x = idx, y = signal[idx], marker='.', color='g')
#     if not os.path.exists(f'img/{model_source}_{data_keyword}/{target}'):
#         os.makedirs(f'img/{model_source}_{data_keyword}/{target}', exist_ok=True)
#     plt.savefig(f'img/{model_source}_{data_keyword}/{target}/{key}.png')
#     with open(f'img/{model_source}_{data_keyword}/{target}_{key}_ai.pkl', 'wb') as f:
#         pickle.dump(p, f)
#     # with open(f'img/{model_source}_{data_keyword}/{target}_{key}_label.pkl', 'wb') as f:
#     #     pickle.dump(label, f)
#     plt.clf()
#     plt.close()