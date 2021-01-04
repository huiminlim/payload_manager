from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, date, timedelta
from time import sleep
import sys
import os


def mission_cmd():
    print("Mission")


def download_cmd():
    print("Download")


# Function processes the list of parsed timestamps to add job for
def create_list_ts(dt, num, interval):
    # Function to parse timestamp
    ls = [dt]
    curr_dt = dt
    for n in range(num-1):
        ls.append(curr_dt + timedelta(milliseconds=interval))
        curr_dt = curr_dt + timedelta(milliseconds=interval)
    return ls


def process_timestamp(timestamp):
    chop_timestamp = timestamp.split('_')
    list_ts = []
    for i in chop_timestamp[0].split('-'):
        list_ts.append(i)
    for i in chop_timestamp[1].split(':'):
        list_ts.append(i)
    list_ts = [int(y) for y in list_ts]
    return list_ts


# execute only if run as a script
if __name__ == "__main__":

    # Initialize Scheduler in background
    scheduler = BackgroundScheduler()

    cmd = sys.argv[1]
    arg = sys.argv[2:]
    timestamp_start = arg[0]  # Format: 2020-10-18_16:33:57
    num = int(arg[1])
    interval = int(arg[2])
    print("Timestamp: %s" % timestamp_start)
    print("Images to take: %s" % num)
    print("Interval (ms): %s" % interval)

    # Parse timestamp
    list_ts = process_timestamp(timestamp_start)
    start_dt = datetime(list_ts[0], list_ts[1],
                        list_ts[2], list_ts[3], list_ts[4], list_ts[5])
    list_ts_image = create_list_ts(start_dt, num, interval)

    if cmd == 'mission':
        for ts in list_ts_image:
            scheduler.add_job(mission_cmd, next_run_time=ts)
    if cmd == 'downlink':
        for ts in list_ts_image:
            scheduler.add_job(download_cmd, next_run_time=ts)

    # Start the scheduler
    scheduler.start()

    while True:
        try:
            pass
        except KeyboardInterrupt:
            print("End")
