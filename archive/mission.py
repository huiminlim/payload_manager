from apscheduler.schedulers.background import BackgroundScheduler
from picamera import PiCamera
from datetime import datetime, date, timedelta
from time import sleep
import os
import sys


# Sample command: python3 mission.py mission 2020-10-19_00:55:00 5 1000

# Function takes a single image
# Saves the image with a given name
# To be used in the scheduled job
def take_image(mission_folder_path, timestamp, count, num):
    global flagDone
    name_image = mission_folder_path + '/' + str(timestamp) + "_" + str(count) + '.jpg'
    
    #placeholder name to allow windows to store
    #name_image = mission_folder_path + '/'+ str(count) +'.jpg'
    
    camera.capture(name_image)
    print(f'Image at {name_image} taken at {datetime.utcnow()}')

    if count == num:
        flagDone = True


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
    # Flag to end program after execution
    # Temporarily needed - not required in the actual program
    flagDone = False

    # Read command from system argument as list
    # Command: mission <timestamp_start> <images> <frequency>
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

    # Create Folder for mission
    storage_path = '/home/pi/Desktop'
    mission_folder_path = storage_path + '/' + timestamp_start
    os.mkdir(mission_folder_path)
    print("Mission directory created: %s" % mission_folder_path)

    # Initialize Camera
    camera = PiCamera()

    # Initialize Scheduler in background
    scheduler = BackgroundScheduler()

    # This code segment schedules all image taking (num per interval) as separate jobs
    # Timestamp list format: [2020, 10, 18, 16, 33, 57]
    count = 0
    for ts in list_ts_image:
        count = count + 1
        scheduler.add_job(take_image, 'date', run_date=ts,
                          args=[mission_folder_path, ts, count, num])

    scheduler.start()

    # Runs on to allow execution of job
    while flagDone == False:
        pass
