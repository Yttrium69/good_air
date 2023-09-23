from flask import Flask, jsonify, render_template, url_for, request, json
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
from model import AisDataAir, AisDataAbnrm
from methods import parse_date, dnsty_of
import json
import plotly.graph_objects as go
import plotly.express as px
import plotly
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import os
import pickle
import numpy as np
from methods import *
from detector import detect
# from flask_sqlalchemy import sessionmaker

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://ais:aisUser1%40%40@e2m3.iptime.org:5432/airinfo"
item_cd = ['', 'SO2', 'NO2', 'O3', 'CO', 'PM10', 'PM25', 'NO', 'NOX']
db = SQLAlchemy(app)

@app.route('/button1_select', methods = ['GET', 'POST'])
def button1_select():
    st_date = '2023010101'
    ed_date = '2023063023'
    
    # area_list = [111121, 111122, 111123, 111124, 111125, 111131, 111141, 111142, 111143, 111151, 111152, 111154, 111161, 111162, 111171, 111181, 111191, 111201, 111202, 111212, 111213, 111221, 111231, 111232, 111241, 111242, 111251, 111261, 111262, 111263, 111264, 111273, 111274, 111275, 111281, 111282, 111291, 111301, 111311, 111312]
    # area_list = [533112, 533113, 533114, 533115, 533116, 633122, 633123, 633124, 633125, 633131, 633132, 633133, 633211, 633213, 633214, 633215, 633311, 633312, 633313, 633361, 633362, 633363, 633411, 633412, 633461, 633462, 633463, 633471, 633472, 633481, 633482, 633491, 634111]
    # area_list = [437111, 437112, 437113, 437114, 437115, 437116, 437117, 437118, 437119, 437120, 437121, 437122, 437123, 437124, 437125, 437131, 437132, 437133, 437141, 437151, 437152, 437153, 437154, 437156, 437161, 437162, 437171, 437172, 437173, 437181, 437191, 437201, 437202, 437203, 437211, 437221, 437371, 437401, 437402, 437411, 437412, 437413, 437421, 437431, 437432, 437541, 437542, 437551, 437561, 437571, 437581, 437591]
    # area_list = [422209, 422207, 437124, 221281, 221152] + [221112, 221131, 221172, 221221, 221241, 221283, 221284, 221901,
    #    422114, 422132, 422133, 422141, 422171, 422202, 422204, 422206,
    #    437112, 437114, 437115, 437116, 437120]
    
    columns = [AisDataAir.data_knd_cd, AisDataAir.msrmt_ymdh, AisDataAir.msrstn_cd]
    columns_name = ['DATA_CD', 'MDATETIME', 'AREA_INDEX',]
    for matter in ['PM10', 'PM25', 'O3', 'SO2', 'CO', 'NO', 'NO2', 'NOX']:
        columns.append(dnsty_of(matter, AisDataAir))
        columns_name.append(matter)
        columns.append(dnsty_flag_of(matter, AisDataAir))
        columns_name.append(matter + '_FLAG')
    
    query =  db.session.query(AisDataAir).with_entities(*columns).filter(
                                                      AisDataAir.data_knd_cd == 'DATAR1',
                                                      st_date<=AisDataAir.msrmt_ymdh, 
                                                      AisDataAir.msrmt_ymdh<=ed_date, 
                                                      )#AisDataAir.msrstn_cd.in_(area_list))
    print(query)
    print('query1 start')
    df = pd.read_sql_query(query.statement, db.engine)
    df.columns = columns_name
    print('query1 end')

    # wrong
    wrong_columns = [AisDataAbnrm.msrmt_ymdh, AisDataAbnrm.msrstn_cd, AisDataAbnrm.cntmn_dtl_cd, AisDataAbnrm.abnrm_data_se_cd]
    wrong_columns_name = ['MDATETIME', 'AREA_INDEX', 'DATA_CD', 'WRONG_CODE']
    
    print('query2 start')
    query =  db.session.query(AisDataAbnrm).with_entities(*wrong_columns).filter(
                                                                    st_date<=AisDataAbnrm.msrmt_ymdh, 
                                                                    AisDataAbnrm.msrmt_ymdh<=ed_date, 
                                                                    )#AisDataAbnrm.msrstn_cd.in_(area_list))
    wrong = pd.read_sql_query(query.statement, db.engine)
    wrong.columns = wrong_columns_name
    area_list = df['AREA_INDEX'].unique()

    wrong['MDATETIME'] = wrong['MDATETIME'].astype(str)
    date = []
    for d in wrong['MDATETIME'].to_numpy(copy=True):
        try:
            converted_d = pd.to_datetime(d, format='%Y%m%d%H')
        except:
            d = d[:-2] + '00'
            converted_d = pd.to_datetime(d, format='%Y%m%d%H') + timedelta(days=1)
        date.append(converted_d)
    wrong['MDATETIME'] = date
    wrong.index = wrong['MDATETIME'].to_numpy(copy=True)
    print('query2 end')
    
    for matter in ['PM10', 'PM25', 'O3', 'SO2', 'CO', 'NO', 'NO2', 'NOX']:
        df[f'{matter}_LABEL'] = np.zeros(df['MDATETIME'].size)
        idx = df[df[f'{matter}_FLAG'] != 1].index
        df.loc[idx, matter] = None

    df['MDATETIME'] = df['MDATETIME'].astype(str)
    date = []
    for d in df['MDATETIME'].to_numpy():
        try:
            converted_d = pd.to_datetime(d, format='%Y%m%d%H')
        except:
            d = d[:-2] + '00'
            converted_d = pd.to_datetime(d, format='%Y%m%d%H') + timedelta(days=1)
        date.append(converted_d)
    df['MDATETIME'] = date
    df.index = df['MDATETIME'].to_numpy(copy=True)
    df = df.sort_index().reset_index()

    print('query end')

    for area in area_list:
        tmp = df[df['AREA_INDEX'] == area].copy()
        org_index = tmp.index
        tmp.index = tmp['MDATETIME'].to_numpy(copy=True)
        for cd in range(1, 9):
            try:
                wrong_tmp = wrong[(wrong['AREA_INDEX'] == area) & (wrong['DATA_CD'] == cd)].copy()
                tmp.loc[wrong_tmp.index, [f'{item_cd[cd]}_LABEL']] = wrong_tmp['WRONG_CODE'].to_numpy(copy=True)
                df.loc[org_index, [f'{item_cd[cd]}_LABEL']] = tmp[f'{item_cd[cd]}_LABEL'].to_numpy(copy=True)
            except Exception as e:
                print(e)
                pass

    for key in area_list:
        X = df[df['AREA_INDEX'] == key].sort_values(by=['MDATETIME'])
        for matter in ['PM10', 'PM25', 'O3', 'SO2', 'CO', 'NO', 'NO2', 'NOX']:
            idx = X[X[f'{matter}_FLAG'] != 1].index
            X.loc[idx, [matter]] = pd.NA
        X.to_csv(f'air_2023_test/{int(key)}.csv', index=False)
    
    print('end')
    return (f'<script>alert("완료"); location.href="/";</script>')

@app.route('/button2_select', methods = ['GET', 'POST'])
def button2_select():
    start_date = '2023010101'
    end_date = '2023063023'
    area_list = [111121, 111122, 111123, 111124, 111125, 111131, 111141, 111142, 111143, 111151, 111152, 111154, 111161, 111162, 111171, 111181, 111191, 111201, 111202, 111212, 111213, 111221, 111231, 111232, 111241, 111242, 111251, 111261, 111262, 111263, 111264, 111273, 111274, 111275, 111281, 111282, 111291, 111301, 111311, 111312]
    area_list += [533112, 533113, 533114, 533115, 533116, 633122, 633123, 633124, 633125, 633131, 633132, 633133, 633211, 633213, 633214, 633215, 633311, 633312, 633313, 633361, 633362, 633363, 633411, 633412, 633461, 633462, 633463, 633471, 633472, 633481, 633482, 633491, 634111]
    area_list += [437111, 437112, 437113, 437114, 437115, 437116, 437117, 437118, 437119, 437120, 437121, 437122, 437123, 437124, 437125, 437131, 437132, 437133, 437141, 437151, 437152, 437153, 437154, 437156, 437161, 437162, 437171, 437172, 437173, 437181, 437191, 437201, 437202, 437203, 437211, 437221, 437371, 437401, 437402, 437411, 437412, 437413, 437421, 437431, 437432, 437541, 437542, 437551, 437561, 437571, 437581, 437591]
    columns = [AisDataAbnrm.msrmt_ymdh, AisDataAbnrm.msrstn_cd, AisDataAbnrm.cntmn_dtl_cd, AisDataAbnrm.abnrm_data_se_cd]
    columns_name = ['MDATETIME', 'AREA_INDEX', 'DATA_CD', 'WRONG_CODE']
    
    query =  db.session.query(AisDataAbnrm).with_entities(*columns).filter(start_date<=AisDataAbnrm.msrmt_ymdh, 
                                                                    AisDataAbnrm.msrmt_ymdh<=end_date, 
                                                                    )# AisDataAbnrm.msrstn_cd.in_(area_list))
    print(query)
    print('query start')
    df = pd.read_sql_query(query.statement, db.engine)
    df.columns = columns_name
    
    print(df)
    print(df['AREA_INDEX'].unique())
    # print(df[df['AREA_INDEX'] == 111141])
    # print(df[(df['WRONG_CODE'] == 3) | (df['WRONG_CODE'] == 6)]['AREA_INDEX'].unique())
    
    return (f'<script>alert("완료"); location.href="/";</script>')

@app.route('/test', methods = ['GET', 'POST'])
def main():
    return render_template('test.html')


if __name__ == '__main__':
    app.run(debug=True, host="165.246.44.130")
