from apscheduler.schedulers.background import BackgroundScheduler
from payload_manager_helper import *
from picamera import PiCamera
import serial
import os

data_read = ""
no_exception = True
ser_cmd_input = serial.Serial('/dev/serial0')
test_run = False


def main():

    global data_read
    global no_exception
    global ser_cmd_input
    global test_run

    # Initialize Scheduler in background
    scheduler = BackgroundScheduler()

    # Start the scheduler
    scheduler.start()

    # Initialize Camera
    camera = PiCamera()
    camera.resolution = (640, 480)

    # Open Serial port to receive commands
    # Blocking to wait forever for input
    ser_cmd_input = serial.Serial('/dev/serial0', baudrate=9600, timeout=None)

    # Open Serial port to downlink images
    ser_downlink = serial.Serial("/dev/ttyUSB0", baudrate=115200, timeout=10)

    while True:
        try:

            if test_run:
                print("Unicode decode error test")
                raise UnicodeDecodeError(
                    'funnycodec', b'\x00\x00', 1, 2, 'This is just a fake reason!')

            if test_run == False and no_exception:
                print("Read data from serial input")
                data_read = ser_cmd_input.readline().decode("utf-8").replace("\r\n", "")

            if data_read:
                list_data_read = data_read.split(" ")

                print(list_data_read)

                cmd = list_data_read[0]

                # Technically redundant since merged mission and downlink command
                if cmd == 'md':

                    mission_list = list_data_read[1:4]
                    downlink_start_ts = list_data_read[4]

                    # Mission
                    datetime_obj, num, list_ts_image = process_mission_command(
                        mission_list)

                    # Create folder path part applicable for mission only
                    # Create Folder for mission
                    storage_path = MISSION_ROOT_FILEPATH

                    mission_folder_path = storage_path + '/' + \
                        datetime_obj.strftime("%Y-%m-%d_%H:%M:%S")
                    os.mkdir(mission_folder_path)
                    print("Mission directory created: %s" %
                          mission_folder_path)

                    count = 0
                    for ts in list_ts_image:
                        count = count + 1
                        scheduler.add_job(mission_cmd, run_date=ts, args=[
                            camera, mission_folder_path, ts, count, num])

                    # Downlink
                    # Process all 3 timestamps
                    timestamp_start_downlink = process_timestamp(
                        downlink_start_ts)
                    # timestamp_query_start = process_timestamp(downlink_list[2])
                    # timestamp_query_end = process_timestamp(downlink_list[3])

                    # Obtain list of filepaths to images to downlink
                    # filepath_list = process_downlink_filepaths(
                    #     timestamp_query_start, timestamp_query_end)

                    scheduler.add_job(download_cmd, next_run_time=timestamp_start_downlink, args=[
                        ser_downlink, mission_folder_path])

                    no_exception = True

        except KeyboardInterrupt:
            print("End, exiting")
            scheduler.shutdown()
            camera.close()
            exit()

        except UnicodeDecodeError:
            print()
            print("Error -- unicode decode error")
            print("Request cmd again...")

            if test_run:
                test_run = False

            ser_cmd_input.write(b"bcc\r\n")
            data_read = ser_cmd_input.readline().decode("utf-8").replace("\r\n", "")
            no_exception = False

        # Fall through exception -- just in case
        except Exception as ex:
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            print(message)


if __name__ == "__main__":
    main()
