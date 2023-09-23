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
db = SQLAlchemy(app)

data = pd.DataFrame()
checked_rules = []
checked_rules2 = []
checked_plants_list = []
elems_left = []
elems_right = []
search_form_node = search_form()
cd = {
    'Sudden_Chg' : 2,
    'SameValue' : 1,
    'NO_rate' : 7,
    'Reverse_PM' : 4,
}
item_cd = ['', 'SO2', 'NO2', 'O3', 'CO', 'PM10', 'PM25', 'NO', 'NOX']

with app.app_context():
    db.create_all()

@app.route('/db_connected', methods=['GET', 'POST'])
def hello_world():
    if (request.method == "GET"):
        date = "2021122013"
        max_cnt = 10
    elif(request.method == "POST"):
        year = int(request.form.get("year"))
        month =int(request.form.get("month"))
        date = int(request.form.get("date"))
        hour = int(request.form.get("hour"))

        date = f'{year:04d}{month:02d}{date:02d}{hour:02d}'
        max_cnt = int(request.form.get("max_cnt"))
    gogo =  db.session.query(AisDataAir).filter(AisDataAir.msrmt_ymdh == date).limit(max_cnt)
    try:
        return render_template("show_db.html", item = gogo)
    except:
        return (f'<script>alert("데이터가 없습니다."); location.href="/";</script>')

def draw_plot():
    global data
    # fig = make_subplots(specs=[[{"secondary_y": True}]], )
    fig = go.Figure()

    for area in checked_plants_list:
        tmp = data[data['AREA_INDEX'] == area]
        for matter in elems_left:
            idx = tmp[tmp[f'{matter}_FLAG'] == 1].index
            fig.add_trace(
                go.Scatter(x=tmp.index, y=tmp[matter], name=f'{area}_{matter}', ),
            )
            if area == checked_plants_list[0]:
                for rule in checked_rules2:
                    idx = tmp[tmp[f'{matter}_CODE'] == cd[rule]].index
                    fig.add_trace(
                        go.Scatter(x=idx, y=tmp.loc[idx, matter], mode='markers', marker={'size':7}, name=rule)
                    )
                
        for matter in elems_right:
            idx = tmp[tmp[f'{matter}_FLAG'] == 1].index
            fig.add_trace(
                go.Scatter(x=tmp.index, y=tmp[matter], name=f'{area}_{matter}', yaxis='y2'),
            )
            if area == checked_plants_list[0]:
                for rule in checked_rules2:
                    idx = tmp[tmp[f'{matter}_CODE'] == cd[rule]].index
                    fig.add_trace(
                        go.Scatter(x=idx, y=tmp.loc[idx, matter], mode='markers',marker={'size':5}, name=rule, yaxis='y2')
                    )
    
    fig.update_layout(
        autosize=False,
        width=1560,
        height=550,
        yaxis2=dict(
            overlaying='y',
            side='right'
        )
    )
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON

@app.route('/get_dnsty_json', methods = ['GET', 'POST'])
def get_dnsty_json():
    print('press search')
    search_form = {
        "plant_ID" : request.args.get("plant_ID"),
        "start_date" : parse_date(request.args.get("start_date")) + '01',
        "end_date" : parse_date(request.args.get('end_date')) + '23',
        "matters" : request.args.get("matters").split(',')[:-1],
        "AI_option" : request.args.get("AI_option")
    }

    columns = [AisDataAir.data_knd_cd, AisDataAir.msrmt_ymdh, AisDataAir.msrstn_cd]
    columns_name = ['DATA_CD', 'MDATETIME', 'AREA_INDEX',]
    for matter in search_form['matters']:
        columns.append(dnsty_of(matter, AisDataAir))
        columns_name.append(matter)
        columns.append(dnsty_flag_of(matter, AisDataAir))
        columns_name.append(matter + '_FLAG')
    
    query =  db.session.query(AisDataAir).with_entities(*columns).filter(
                                                      AisDataAir.data_knd_cd == 'DATAR1',
                                                      search_form["start_date"]<=AisDataAir.msrmt_ymdh, 
                                                      AisDataAir.msrmt_ymdh<=search_form["end_date"], 
                                                      AisDataAir.msrstn_cd == search_form["plant_ID"])
    print(query)
    print('query start')
    df = pd.read_sql_query(query.statement, db.engine)
    df.columns = columns_name

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
    df = df.sort_index()

    print('query end')

    return draw_plot(df, columns_name, search_form['matters'])

def load_query(search_form, near_plants):
    global data
    global checked_plants_list
    st_date = search_form.start_date.replace('-', '').replace(' ', '')
    ed_date = search_form.end_date.replace('-', '').replace(' ', '')

    columns = [AisDataAir.data_knd_cd, AisDataAir.msrmt_ymdh, AisDataAir.msrstn_cd]
    columns_name = ['DATA_CD', 'MDATETIME', 'AREA_INDEX',]
    for matter in ['PM10', 'PM25', 'O3', 'SO2', 'CO', 'NO', 'NO2', 'NOX']:
        columns.append(dnsty_of(matter, AisDataAir))
        columns_name.append(matter)
        columns.append(dnsty_flag_of(matter, AisDataAir))
        columns_name.append(matter + '_FLAG')
    
    checked_plants_list = [int(search_form.plant_id)]
    plants_list = [search_form.plant_id] + near_plants
    query =  db.session.query(AisDataAir).with_entities(*columns).filter(
                                                      AisDataAir.data_knd_cd == 'DATAR1',
                                                      st_date<=AisDataAir.msrmt_ymdh, 
                                                      AisDataAir.msrmt_ymdh<=ed_date, 
                                                      AisDataAir.msrstn_cd.in_(plants_list))
    print(query)
    print('query start')
    df = pd.read_sql_query(query.statement, db.engine)
    df.columns = columns_name

    # wrong
    wrong_columns = [AisDataAbnrm.msrmt_ymdh, AisDataAbnrm.msrstn_cd, AisDataAbnrm.cntmn_dtl_cd, AisDataAbnrm.abnrm_data_se_cd]
    wrong_columns_name = ['MDATETIME', 'AREA_INDEX', 'DATA_CD', 'WRONG_CODE']
    
    query =  db.session.query(AisDataAbnrm).with_entities(*wrong_columns).filter(
                                                                    st_date<=AisDataAbnrm.msrmt_ymdh, 
                                                                    AisDataAbnrm.msrmt_ymdh<=ed_date, 
                                                                    AisDataAbnrm.msrstn_cd == search_form.plant_id)
    wrong = pd.read_sql_query(query.statement, db.engine)
    wrong.columns = wrong_columns_name

    wrong['MDATETIME'] = wrong['MDATETIME'].astype(str)
    date = []
    for d in wrong['MDATETIME'].to_numpy():
        try:
            converted_d = pd.to_datetime(d, format='%Y%m%d%H')
        except:
            d = d[:-2] + '00'
            converted_d = pd.to_datetime(d, format='%Y%m%d%H') + timedelta(days=1)
        date.append(converted_d)
    wrong['MDATETIME'] = date
    wrong.index = wrong['MDATETIME'].to_numpy(copy=True)
    wrong = wrong.sort_index()
    
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

    tmp = df[df['AREA_INDEX'] == int(search_form.plant_id)]
    org_index = tmp.index
    tmp.index = tmp['MDATETIME'].to_numpy(copy=True)
    for cd in range(1, 9):
        wrong_tmp = wrong[wrong['DATA_CD'] == cd]
        tmp.loc[wrong_tmp.index, [f'{item_cd[cd]}_LABEL']] = wrong_tmp['WRONG_CODE'].to_numpy(copy=True)
        df.loc[org_index, [f'{item_cd[cd]}_LABEL']] = tmp[f'{item_cd[cd]}_LABEL'].to_numpy(copy=True)

    for matter in ['PM10', 'PM25', 'O3', 'SO2', 'CO', 'NO', 'NO2', 'NOX']:
        print(matter, df[f'{matter}_LABEL'].unique())

    df.index = df['MDATETIME'].to_numpy(copy=True)
    print('query end')
    data = df.copy()

    return

@app.route('/', methods = ['GET', 'POST'])
def main():
    return render_template('main.html', graphJSON=draw_plot())

@app.route('/click_near_plant', methods = ['GET', 'POST'])
def click_near_plant():
    clicked_plant = request.args.get("plant").replace(' ', '').replace('\n', '')
    clicked_plant = int(clicked_plant)
    if clicked_plant in checked_plants_list:
        checked_plants_list.remove(clicked_plant)
    else:
        checked_plants_list.append(clicked_plant)
    return draw_plot()

@app.route('/check_rule', methods = ['GET', 'POST'])
def check_rule():
    checked_rule = request.args.get("checked")
    if checked_rule in checked_rules:
        checked_rules.remove(checked_rule)
    else:
        checked_rules.append(checked_rule)
    return ''

@app.get('/show_data')
def show_data():
    global data
    data = pd.read_csv('sample.csv')
    data['MDATETIME'] = pd.to_datetime(data['MDATETIME'].to_numpy(copy=True))
    data = data.loc[:4320]
    checked_plants_list = [111121]
    elems_left.clear()
    elems_right.clear()
    with open('./config/서울특별시.json', 'r') as f:
        ruleset = json.load(f)
        
    return render_template('show_data.html', graphJSON=draw_plot(),
                            big_religion=search_form_node.big_religion, middle_religion=search_form_node.middle_religion,
                            Same_value=ruleset['Same_value'], NO_rate=ruleset['NO_rate'], Near_station=ruleset['Near_station'], PM_reverse=ruleset['PM_Reverse'], Sudden_chg=ruleset['Sudden_chg'])

@app.route('/change_religion', methods = ['GET', 'POST'])
def change_religion():
    global search_form_node
    rel = request.args.get("big_religion")
    with open(f'./config/{rel}.json', 'r') as f:
        ruleset = json.load(f)
    
    print(ruleset['Same_value'])
    return render_template('show_data.html', graphJSON=draw_plot(),
                            big_religion=search_form_node.big_religion, middle_religion=search_form_node.middle_religion,)
    
    
@app.get("/get_same_value")
def get_same_value():
    rel = request.args.get("big_religion")
    with open(f'./config/{rel}.json', 'r') as f:
        ruleset = json.load(f)
    
    return jsonify(ruleset)


@app.post('/show_data')
def show_data_post():
    global search_form_node
    global data
    global checked_rules2
    search_form_node = search_form(request.form)
    near_plants = get_near_plants_of(search_form_node.plant_id)
    load_query(search_form_node, near_plants)
    graph_data = get_graph_data_of(search_form_node.plant_id)
    elems_left.clear()
    elems_right.clear()
    with open(f'./config/{search_form_node.big_religion}.json', 'r') as f:
        ruleset = json.load(f)
    
    data = detect(ruleset, data, checked_rules, target_key=search_form_node.plant_id, near_list = near_plants)
    checked_rules2 = checked_rules.copy()
    checked_rules.clear()

    date = {
        "start_year":search_form_node.start_year,
        "start_month":search_form_node.start_month,
        "end_year":search_form_node.end_year,
        "end_month":search_form_node.end_month
    }

    return render_template('show_data.html', date=date, this_plant = search_form_node.plant_id, near_plants = near_plants, graphJSON=draw_plot(),
                            big_religion=search_form_node.big_religion, middle_religion=search_form_node.middle_religion,
                            Same_value=ruleset['Same_value'], NO_rate=ruleset['NO_rate'], Near_station=ruleset['Near_station'], PM_reverse=ruleset['PM_Reverse'], Sudden_chg=ruleset['Sudden_chg'])

@app.route('/matter_click_left', methods = ['GET', 'POST'])
def matter_click_left():
    matter = request.args.get("matter")
    matter = matter.replace('\n', '').replace(' ', '')
    if matter == 'PM2.5':
        matter = 'PM25'
    if matter in elems_left:
        elems_left.remove(matter)
    else:
        elems_left.append(matter)
    return draw_plot()

@app.route('/matter_click_right', methods = ['GET', 'POST'])
def matter_click_right():
    matter = request.args.get("matter")
    matter = matter.replace('\n', '').replace(' ', '')
    if matter == 'PM2.5':
        matter = 'PM25'
    if matter in elems_right:
        elems_right.remove(matter)
    else:
        elems_right.append(matter)
    return draw_plot()

@app.route('/change_multiple_factor_of_matter', methods=["GET", "POST"])
def change_multiple_factor_of_matter():
    matter = request.get_json().get("matter")
    multiple_factor = request.get_json().get("multiple_factor")
    print(f'{matter} 성분을 {multiple_factor}배로 설정')
    return {'ok':"true"}

@app.get('/get_graph_data')
def get_graph_data():
    plants = request.args.get("plants")
    graph_data = get_graph_data_json(plants)
    return jsonify(graph_data)

@app.get('/set_rulebase')
def set_rulebase():
    rule_id = request.args.get("rule_id")
    standard = request.args.getlist("standards")
    religion_id = request.args.get("religion_id")

    print(f'rulebase를 변경할 지역: {religion_id}, 변경할 rulebase: {rule_id} 변경할 값: {standard}')

    return jsonify({"status":200})

@app.route('/result', methods = ['GET', 'POST'])
def set_result():
    tmp = data[data['AREA_INDEX'] == int(search_form.plant_id)]
    rule_code = [0, 1, 4, 2, 5, 7, 3]

    for i in range(1, 7):
        rule_node = Rules_table[f'{i}']
        for matter in ['PM10', 'PM25', 'O3', 'SO2', 'CO', 'NO', 'NO2', 'NOX']:
            rule_node.set_element_detact_result(matter, tmp[tmp[f'{matter}_CODE'] == rule_code[i]]['AREA_INDEX'].size)
            rule_node.set_element_label(matter, tmp[tmp[f'{matter}_LABEL'] == rule_code[i]]['AREA_INDEX'].size)
            size1 = tmp[tmp[f'{matter}_CODE'] == rule_code[i]]['AREA_INDEX'].size
            size2 = tmp[(tmp[f'{matter}_LABEL'] == rule_code[i]) & (tmp[f'{matter}_CODE'] == rule_code[i])]['AREA_INDEX'].size
            print(size1, size2)
            if size1 == 0:
                rule_node.set_element_detact_rate(matter, 0)
            else:
                rule_node.set_element_detact_rate(matter, size2 / size1)

    return render_template("show_match_rate.html", rules_dict = Rules_table)

if __name__ == '__main__':
    app.run(debug=True, host="165.246.44.130")