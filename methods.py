from pandas import to_datetime
import pickle
import datetime
import ast

def parse_date(date_to_parse):
    parsed_list = date_to_parse.split('-')
    result = parsed_list[0]+parsed_list[1]+parsed_list[2]
    return result

def dnsty_of(matter, item):
    if matter == "CO":
        return item.co_dnsty
    elif matter == "O3":
        return item.oz_dnsty
    elif matter == "SO2":
        return item.so2_dnsty
    elif matter == "NOX":
        return item.nox_dnsty
    elif matter == "NO2":
        return item.no2_dnsty
    elif matter == "NO":
        return item.nmo_dnsty
    elif matter == "PM10":
        return item.pm_dnsty
    elif matter == "PM25":
        return item.pm25_dnsty

def dnsty_flag_of(matter, item):
    if matter == "CO":
        return item.co_dtl_flag
    elif matter == "O3":
        return item.oz_dtl_flag
    elif matter == "SO2":
        return item.so2_dtl_flag
    elif matter == "NOX":
        return item.nox_dtl_flag
    elif matter == "NO2":
        return item.no2_dtl_flag
    elif matter == "NO":
        return item.nmo_dtl_flag
    elif matter == "PM10":
        return item.pm_dtl_flag
    elif matter == "PM25":
        return item.pm25_dtl_flag

class search_form:
    start_year = 0
    start_month = 0
    end_year = 0
    end_month = 0
    rule_bases = []
    plant_id = "000000"
    big_religion = '서울특별시'
    middle_religion = '서울특별시'
    small_religion = ""
    plant_id = 111121

    def __init__(self, request_form=None):
        if request_form is not None:
            self.start_year= request_form.get("start_date").split("-")[0]
            self.start_month= request_form.get("start_date").split("-")[1]
            self.start_date = request_form.get("start_date") + '-01 00'
            self.end_year = request_form.get("end_date").split("-")[0]
            self.end_month = request_form.get("end_date").split("-")[1]
            test_date = to_datetime(request_form.get("end_date") + '-01 23')
            nxt_mnth = test_date.replace(day=28) + datetime.timedelta(days=4)
            self.end_date = str(nxt_mnth - datetime.timedelta(days=nxt_mnth.day))
            self.rule_bases = request_form.getlist("rule")
            self.small_religion = request_form.get("small_religion")
            self.plant_id = request_form.get("small_religion").split('(')[1].split(')')[0]
            self.big_religion = request_form.get("big_religion")
            self.middle_religion = request_form.get("middle_religion")
            print(request_form.get("rule_priority"))
            self.priority_arr = ast.literal_eval(request_form.get("rule_priority"))

def get_graph_data_json(plant_id_list):
    final_json = []
    for plant in plant_id_list:
        graph_data = get_graph_data_of(plant)
        final_json.push(graph_data)
    return final_json

def get_graph_data_of(plant_id):
    data = [{"index1":"data1"}, {"index2":"data2"}]
    return data

def get_near_plants_of(plant_id):
    with open('Specifications.pkl', 'rb') as f:
        near = pickle.load(f)
    ###plant의 주변에 있는 관측소들의 id를 list형식으로 return"
    near_list = near[int(plant_id)]['CO']
    near_list = [str(x) for x in near_list]
    
    return near_list


##일치율 parameter로 받게 만들기
class Rule:
    class Element:
        match_rate = 0
        detact_result = 0
        label = 0
        is_set = False

        def __init__(self, name, detact_result = 0, label = 0):
            self.name = name
            self.detact_result = detact_result
            self.label = label
        
        # def calc_match_rate(self):
        #     if(self.label ==0 or self.label == None):
        #         return -1
        #     return abs(int(self.detact_result)-int(self.label))/(abs(int(self.detact_result))+abs(int(self.label)))*100
        
        def set_my_detact_result(self, detact_result):
            self.detact_result = detact_result
            self.im_set()
        
        def set_my_detact_match_rate(self, detact_rate):
            self.match_rate = detact_rate
            self.im_set()

        def set_my_label(self, label):
            self.label = label
            self.im_set()

        def im_set(self):
            self.is_set = True
    
    code = -1
    title = ""
    elements = {
        "CO":Element(name = "CO"),
        "O3":Element(name = "O3"),
        "NOX":Element(name = "NOX"),
        "SO2":Element(name = "SO2"),
        "NO2":Element(name = "NO2"),
        "NO":Element(name = "NO"),
        "PM10":Element(name = "PM10"),
        "PM25":Element(name = "PM25"),
    }
    def __init__(self, title):
        self.title = title

    def push_element(self, element_name, detact_result, label, detact_rate):
        self.elements.append(self.Element(element_name, detact_result, label))

    def get_element(self, element_name):
        return self.elements.get(element_name)
    
    def set_element_detact_result(self, element_name, detact_result):
        self.elements[element_name].set_my_detact_result(detact_result)

    def set_element_detact_rate(self, element_name, detact_result):
        self.elements[element_name].set_my_detact_match_rate(detact_result)

    def set_element_label(self, element_name, label):
        self.elements[element_name].set_my_label(label)
    

Rules_table = {
    "1":Rule("동일값 n시간 이상 지속"),
    "2":Rule("pm 역전"),
    "3":Rule("급격한 변화"),
    "4":Rule("주변측정소 대비 이상"),
    "5":Rule("NO비율 이상"),
    "6":Rule("베이스라인 이상")
}