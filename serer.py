from flask import Flask, jsonify, render_template, url_for, request, json
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
from model import AisDataAir
from methods import parse_date, dnsty_of
from config import db_src

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = db_src
db = SQLAlchemy()
Base = db.Model

db.init_app(app)
db.app=app

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
    print(date)
    try:
        return render_template("show_db.html", item = gogo)
    except:
        return (f'<script>alert("데이터가 없습니다."); location.href="/";</script>')

@app.route('/get_dnsty_json', methods = ['GET', 'POST'])
def get_dnsty_json():
    print(request.args)
    search_form = {
            "plant_ID" : request.args.get("plant_ID"),
            "start_date" : parse_date(request.args.get("start_date"))+"01",
            "end_date" : parse_date(request.args.get('end_date'))+"23",
            "matters" : request.args.get("matters").split(','),
            "AI_option" : request.args.get("AI_option")
        }
    print(search_form)
    db_to_show =  db.session.query(AisDataAir).filter(search_form["start_date"]<=AisDataAir.msrmt_ymdh, AisDataAir.msrmt_ymdh<=search_form["end_date"], AisDataAir.msrstn_cd == search_form["plant_ID"]).limit(50)
    print("GOGO")
    print(db_to_show)
    result = []

    for matter in search_form["matters"]:
        everyday_dnsties_of_matter = []
        for item in db_to_show:
            print("GO")
            today = str(item.msrmt_ymdh)
            if(dnsty_of(matter, item) != None):
                dnsty = float(str(dnsty_of(matter, item)))
                today_data = {today:dnsty}
                everyday_dnsties_of_matter.append(today_data)
        result.append({str(matter):everyday_dnsties_of_matter})
    
    print(result)
    return jsonify(result)


@app.route('/', methods = ['GET', 'POST'])
def main():
    if request.method == 'GET':
        return render_template("main.html")
    
    # elif request.method == 'POST':
    #     search_form = {
    #         "plant_ID" : request.form.get("plant_ID"),
    #         "start_date" : parse_date(request.form.get("start_date"))+"01",
    #         "end_date" : parse_date(request.form.get('end_date'))+"23",
    #         "matters" : request.form.getlist("matters"),
    #         "AI_option" : request.form.get("AI_option")
    #     }
    #     db_to_show =  db.session.query(AisDataAir).filter(search_form["start_date"]<=AisDataAir.msrmt_ymdh, AisDataAir.msrmt_ymdh<=search_form["end_date"], AisDataAir.msrstn_cd == search_form["plant_ID"]).limit(50)

    #     result = []

    #     for matter in search_form["matters"]:
    #         everyday_dnsties_of_matter = []
    #         for item in db_to_show:
    #             print("GO")
    #             today = str(item.msrmt_ymdh)
    #             dnsty = float(str(dnsty_of(matter, item)))
    #             today_data = {today:dnsty}
    #             everyday_dnsties_of_matter.append(today_data)
    #         result.append({str(matter):everyday_dnsties_of_matter})
            
    #     return jsonify(result)



@app.route('/gogo', methods = ['GET', 'POST'])
def gogo():
    return jsonify({
                "2021121401": "0.02100000000000"
            },
            {
                "2021121402": "0.01900000000000"
            },
            {
                "2021121403": "0.01800000000000"
            },
            {
                "2021121404": "0.02000000000000"
            },
            {
                "2021121405": "0.01100000000000"
            },
            {
                "2021121406": "0.00800000000000"
            },
            {
                "2021121407": "0.00300000000000"
            },
            {
                "2021121408": "0.00200000000000"
            },
            {
                "2021121409": "0.00400000000000"
            },
            {
                "2021121410": "0.00300000000000"
            },
            {
                "2021121411": "0.00900000000000"
            },
            {
                "2021121412": "0.02500000000000"
            },
            {
                "2021121413": "0.03200000000000"
            },
            {
                "2021121414": "0.03400000000000"
            },
            {
                "2021121415": "0.03200000000000"
            },
            {
                "2021121416": "0.03200000000000"
            },
            {
                "2021121417": "0.03200000000000"
            },
            {
                "2021121418": "0.02500000000000"
            },
            {
                "2021121419": "0.01500000000000"
            },
            {
                "2021121420": "0.00200000000000"
            })

if __name__ == '__main__':
    app.run(debug=True, host="127.0.0.1")