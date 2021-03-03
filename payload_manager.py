from apscheduler.schedulers.background import BackgroundScheduler
from payload_manager_helper import *
from picamera import PiCamera
import serial
import os


def main():

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
            data_read = ser_cmd_input.readline().decode("utf-8").replace("\r\n", "")

            list_data_read = data_read.split(" ")

            print(list_data_read)

            cmd = list_data_read[0]

            # Technically redundant since merged mission and downlink command
            if cmd == 'md':

                mission_list = list_data_read[1:4]
                downlink_list = list_data_read[4:]

                # Mission
                datetime_obj, num, list_ts_image = process_mission_command(
                    mission_list)

                # Create folder path part applicable for mission only
                # Create Folder for mission
                storage_path = MISSION_ROOT_FILEPATH

                mission_folder_path = storage_path + '/' + \
                    datetime_obj.strftime("%Y-%m-%d_%H:%M:%S")
                os.mkdir(mission_folder_path)
                print("Mission directory created: %s" % mission_folder_path)

                count = 0
                for ts in list_ts_image:
                    count = count + 1
                    scheduler.add_job(mission_cmd, run_date=ts, args=[
                        camera, mission_folder_path, ts, count, num])

                # Downlink
                # Process all 3 timestamps
                timestamp_start_downlink = process_timestamp(downlink_list[1])
                timestamp_query_start = process_timestamp(downlink_list[2])
                timestamp_query_end = process_timestamp(downlink_list[3])

                # Obtain list of filepaths to images to downlink
                filepath_list = process_downlink_filepaths(
                    timestamp_query_start, timestamp_query_end)

                scheduler.add_job(download_cmd, next_run_time=timestamp_start_downlink, args=[
                    ser_downlink, filepath_list])

        except KeyboardInterrupt:
            print("End, exiting")
            scheduler.shutdown()
            camera.close()
            exit()

        except UnicodeDecodeError:
            print()
            print("Error -- unicode decode error")
            print("Did not manage to read command")
            print()

        # Fall through exception -- just in case
#         except Exception as ex:
#             print(ex)


if __name__ == "__main__":
    main()
