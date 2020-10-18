from apscheduler.schedulers.background import BackgroundScheduler
from picamera import PiCamera
from datetime import datetime
from datetime import date
from time import sleep
import os
import sys


# Sample command: python3 mission.py mission 2020-10-19_00:55:00 5 1000


# Function to take image
def take_image(num, freq, mission_folder_path, timestamp_start):
    global flagDone
    for i in range(1, num+1):
        name_image = mission_folder_path + '/' + \
            timestamp_start + "_" + str(i) + '.jpg'
        camera.capture(name_image)
        print(f'Image at {name_image} taken at {datetime.utcnow()}')
        sleep(freq/1000)  # Not precise, cannot use for mission!
    flagDone = True


# Function to parse timestamp
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
    #print(arg)
    timestamp_start = arg[0]  # Format: 2020-10-18_16:33:57
    num = int(arg[1])
    freq = int(arg[2])
    print("Timestamp: %s" % timestamp_start)
    print("Images to take: %s" % num)
    print("Frequency (ms): %s" % freq)

    # Parse timestamp
    list_ts = process_timestamp(timestamp_start)

    # Timestamp of mission
    # Mock timestamp data to create mission
    # To be removed and time will be received from mission command
    # time_utc = str(datetime.utcnow()).replace(" ", "_")
    # print("UTC time: %s" % time_utc)

    # Create Folder for mission
    storage_path = '/home/pi/Desktop'
    #print ("The current working directory is %s" % storage_path)
    # mission_folder_path = storage_path + '/' + time_utc
    mission_folder_path = storage_path + '/' + timestamp_start
    os.mkdir(mission_folder_path)
    print("Mission directory created: %s" % mission_folder_path)

    # Initialize Camera
    camera = PiCamera()

    # Initialize Scheduler in background
    scheduler = BackgroundScheduler()
    scheduler.add_job(take_image, 'date', run_date=datetime(
        list_ts[0], list_ts[1], list_ts[2], list_ts[3], list_ts[4], list_ts[5]), args=[num, freq, mission_folder_path, timestamp_start])
    scheduler.start()

    #take_image(num, freq, mission_folder_path, time_utc)

    # Runs on to allow execution of job
    while flagDone == False:
        pass


# ------- End --------- #
#from time import sleep
# camera.start_preview()
# sleep(5)
#
# camera.stop_preview()
# camera.capture('/home/pi/Desktop/image.jpg')
#path = os.getcwd()
