from datetime import datetime, date, timedelta


def process_timestamp(timestamp):
    chop_timestamp = timestamp.split('_')
    list_ts = []
    for i in chop_timestamp[0].split('-'):
        list_ts.append(i)
    for i in chop_timestamp[1].split(':'):
        list_ts.append(i)
    list_ts = [int(y) for y in list_ts]
    return list_ts


list_ts = process_timestamp("2020-10-19_00:55:00")
start_dt = datetime(list_ts[0], list_ts[1],
                    list_ts[2], list_ts[3], list_ts[4], list_ts[5])
print(str(start_dt)+'hello')
