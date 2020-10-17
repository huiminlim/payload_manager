from picamera import PiCamera
from datetime import datetime
from time import sleep
import os, sys

def take_image(num, freq, mission_folder_path, timestamp_start):
    for i in range(1, num+1):
        name_image = mission_folder_path +'/' + timestamp_start + "_" + str(i) + '.jpg'
        camera.capture(name_image)
        print(f'Image at {name_image} taken at {datetime.utcnow()}')
        sleep(freq/1000) # Not precise, cannot use for mission!

# execute only if run as a script
if __name__ == "__main__":
    # Read command from system argument as list
    # Command: mission <timestamp_start> <images> <frequency>
    arg = sys.argv[1:]
    #timestamp_start = int(arg[1])
    num = int(arg[1])
    freq = int(arg[2])
    print("Images to take: %s" % num)
    print("Frequency (ms): %s" % freq)
        
    # Timestamp of mission
    # Mock timestamp data to create mission
    # To be removed and time will be received from mission command
    time_utc = str(datetime.utcnow()).replace(" ", "_")
    print ("UTC time: %s" % time_utc)
    
    # Create Folder for mission
    storage_path = '/home/pi/Desktop'
    #print ("The current working directory is %s" % storage_path)
    mission_folder_path = storage_path + '/' + time_utc
    os.mkdir(mission_folder_path)
    print ("Mission directory created: %s" % mission_folder_path)
    
    # Initialize Camera
    camera = PiCamera()
    
    take_image(num, freq, mission_folder_path, time_utc)
    





# ------- End --------- #
#from time import sleep
# camera.start_preview()
# sleep(5)
#
# camera.stop_preview()
#camera.capture('/home/pi/Desktop/image.jpg')
#path = os.getcwd()
