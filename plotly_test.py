import json

for reg in ["서울특별시", "세종특별자치시", "제주특별자치도","부산광역시", "대구광역시", "인천광역시", "광주광역시",
                            "대전광역시", "울산광역시", "강원도", "경기도", "충청북도", "충청남도", "전라남도", "전라북도", "경상북도", "경상남도"]:
    ruleset = {}
    ruleset['PM_Reverse'] = { 'x1' : 35, 'x2' : 5, 'x3' : 10 }
    ruleset['Same_value'] = { 'x' : 10 }
    ruleset['Sudden_chg'] = { 'k' : 7, 'Threshold' : 0 }
    ruleset['Near_station'] = { 'distance' : 0.5, 'x' : 37 }
    ruleset['NO_rate'] = { 'x' : 0.005 }

    with open(f'./config/{reg}.json', 'w') as f:
        json.dump(ruleset, f)
