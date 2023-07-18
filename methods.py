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