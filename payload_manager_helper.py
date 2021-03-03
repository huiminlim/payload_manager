from datetime import datetime, timedelta
import subprocess
import time
import os

MISSION_ROOT_FILEPATH = '/home/pi/Desktop/Mission'

#### DOWNLINK CONSTANTS ####
CHUNK_SIZE = 179
BATCH_SIZE = 200
TIME_SLEEP_AFTER_START = 1
TIME_SLEEP_AFTER_END = 1.5
TIME_LONG_DELAY = 0.16
TIME_SHORT_DELAY = 0.098

TELEMETRY_PACKET_TYPE_DOWNLINK_START = 30
TELEMETRY_PACKET_TYPE_DOWNLINK_PACKET = 31

packet_count = 0
#### ------------------ ####


def process_mission_command(data_read_list):

    # Function processes the list of parsed timestamps to add job for
    def create_list_ts(dt, num, interval):
        # Function to parse timestamp
        ls = [dt]
        curr_dt = dt
        # Repeat creation of incremental dt
        for num_dt in range(num-1):
            ls.append(curr_dt + timedelta(milliseconds=interval))
            curr_dt = curr_dt + timedelta(milliseconds=interval)
        return ls

    timestamp_start = data_read_list[0]
    num = int(data_read_list[1])
    interval = int(data_read_list[2])

    # print("Command: %s" % cmd)
    print("Timestamp: %s" % timestamp_start)
    print("Images to take: %s" % num)
    print("Interval (ms): %s" % interval)

    # Parse timestamp into datetime format
    start_dt = process_timestamp(timestamp_start)

    list_ts_image = create_list_ts(start_dt, num, interval)

    return start_dt, num, list_ts_image


def mission_cmd(cam, mission_folder_path, timestamp, count, num):
    name_image = mission_folder_path + '/' + \
        str(timestamp).replace(" ", "_") + "_" + str(count) + '.jpg'
    cam.capture(name_image, resize=(640, 480))
    print(f'Image at {name_image} taken at {datetime.utcnow()}')
    print()


def process_timestamp(timestamp):
    chop_timestamp = timestamp.split('_')
    list_ts = []
    for i in chop_timestamp[0].split('-'):
        list_ts.append(i)
    for i in chop_timestamp[1].split(':'):
        list_ts.append(i)
    list_ts = [int(y) for y in list_ts]

    start_dt = datetime(list_ts[0], list_ts[1],
                        list_ts[2], list_ts[3], list_ts[4], list_ts[5])

    return start_dt


#### DOWNLINK FUNCTIONS ####

def process_downlink_command(data_read_list):
    timestamp_downlink = process_timestamp(data_read_list[1])
    timestamp_query_start = process_timestamp(data_read_list[2])
    timestamp_query_end = process_timestamp(data_read_list[3])
    return [timestamp_downlink, timestamp_query_start, timestamp_query_end]


# Receive timestamp in plaintext
# def process_downlink_filepaths(start_timestamp, end_timestamp):
#     list_filepaths = []

#     list_dir_mission = os.listdir(MISSION_ROOT_FILEPATH)

#     for mission_timestamp in list_dir_mission:
#         processed_timestamp = process_timestamp(mission_timestamp)
#         if start_timestamp < processed_timestamp and processed_timestamp < end_timestamp:
#             for file in os.listdir(MISSION_ROOT_FILEPATH + '/' + mission_timestamp):
#                 list_filepaths.append(
#                     MISSION_ROOT_FILEPATH + '/' + mission_timestamp + '/' + file)

#     print(list_filepaths)

#     return list_filepaths

# Given mission folder path, obtain list of images path
def obtain_downlink_images_filepaths(mission_folder_path):
    list_filepaths = []
    for file in os.listdir(mission_folder_path):
        list_filepaths.append(mission_folder_path + '/' + file)
    return list_filepaths


def download_cmd(ser_obj, mission_folder):
    curr_img_count = 0

    filepath_list = obtain_downlink_images_filepaths(
        mission_folder)

    print(f"List of images: {filepath_list}")

    total_img = len(filepath_list)
    for file in filepath_list:
        curr_img_count = curr_img_count + 1

        print(f"Current image count: {curr_img_count} of {total_img}")

        # Call bash script to execute prep script
        # base64 + gzip
        prep_filepath = './prep_test.sh ' + file
        subprocess.call(prep_filepath, stdout=subprocess.DEVNULL, shell=True)

        # Open and read in the image
        with open('base_enc.gz', 'rb') as file:
            compressed_enc = file.read()
            file.close()
        total_bytes_retrieved = len(compressed_enc)

        # Call bash script to remove currently created compressed files
        subprocess.call('./cleanup.sh base_enc.gz',
                        stdout=subprocess.DEVNULL, shell=True)

        # Process the bytes into batches of chunks to be sent out
        chunk_list = chop_bytes(compressed_enc, CHUNK_SIZE)

        # Split chunks into batch according to a batch size
        batch_list = split_batch(chunk_list, BATCH_SIZE)
        total_batch = len(batch_list)

        # Send start packet
        start_packet = ccsds_create_downlink_start_packet(
            TELEMETRY_PACKET_TYPE_DOWNLINK_START, total_bytes_retrieved, total_batch)
        ser_obj.write(start_packet)
        time.sleep(TIME_SLEEP_AFTER_START)

        # Begin Batch send of chunk
        current_batch = 1
        for batch in batch_list:
            print(f"BEGIN SEND: BATCH {current_batch}")
            current_batch = current_batch + 1

            # Begin batch send
            batch_send(ser_obj, batch, TIME_SHORT_DELAY,
                       TIME_LONG_DELAY, current_batch)

            print()

        # Pause before next image send
        time.sleep(10)

#####


# Create a CCSDS Packet Header
# Given source data length
def ccsds_create_packet_header(source_data_len):
    # Contains the Version number, Packet identification,
    # Packet Sequence Control and Packet data length

    global packet_count

    # Abstract header as 6 bytes
    header = bytearray(0)  # octet 1, 2, ..., 6

    octet = 0b0

    # Version number
    octet = octet << 3 | 0b000

    # # Packet identification
    # # @Type indicator -- Set to 0 to indicate telemetry packet
    octet = octet << 1 | 0b0

    # # @Packet Secondary Header Flag -- Set to 0 to indicate that secondary header not present
    octet = octet << 1 | 0b0

    # # @Application Process ID
    # # Defines the process onboard that is sending the packet --> TBC
    octet = octet << 11 | 0b10

    header = header + octet.to_bytes(2, 'big')

    octet = 0b0

    # # Packet Sequence Control
    # # @Grouping packets -- No grouping so set to 0
    octet = octet << 2 | 0b11

    # # @Source Sequence Count
    # # Sequence number of packet modulo 16384
    octet = octet << 14 | packet_count
    packet_count = packet_count + 1

    header = header + octet.to_bytes(2, 'big')

    octet = 0b0

    # # Packet Data Length
    # In terms of octets
    # Total number of octets in packet data field - 1
    octet = octet << 16 | (source_data_len - 1)

    header = header + octet.to_bytes(2, 'big')

    return header


# Function to create a start packet for downlink
# Format: | CCSDS Primary header | Telemetry Packet Type | Total Bytes | Total Chunks to send |
def ccsds_create_downlink_start_packet(telemetry_packet_type, total_bytes, total_batch):

    TOTAL_BYTES_LENGTH = 3  # Bytes
    TOTAL_BATCH_LENGTH = 3
    TELEMETRY_TYPE_LENGTH = 1

    # Packet
    packet = bytearray(0)

    # Compute Source data length and create header
    source_data_len = TOTAL_BYTES_LENGTH + \
        TOTAL_BYTES_LENGTH + TELEMETRY_TYPE_LENGTH
    ccsds_header = ccsds_create_packet_header(source_data_len)

    packet = packet + ccsds_header

    # Append bytes to packet
    packet = packet + \
        telemetry_packet_type.to_bytes(TELEMETRY_TYPE_LENGTH, 'big')
    packet = packet + total_bytes.to_bytes(TOTAL_BYTES_LENGTH, 'big')
    packet = packet + total_batch.to_bytes(TOTAL_BATCH_LENGTH, 'big')
    return packet


# Function to create a chunk packet for downlink
# NOTE: Payload length should be a fixed constant (refer to top constants declared)
def ccsds_create_downlink_chunk_packet(telemetry_packet_type, current_batch, current_chunk, payload):

    CURRENT_CHUNKS_LENGTH = 3
    CURRENT_BATCH_LENGTH = 3
    TELEMETRY_TYPE_LENGTH = 1

    # Packet
    packet = bytearray(0)

    # Compute Source data length and create header
    source_data_len = TELEMETRY_TYPE_LENGTH + \
        CURRENT_CHUNKS_LENGTH + CURRENT_BATCH_LENGTH + len(payload)
    ccsds_header = ccsds_create_packet_header(source_data_len)

    packet = packet + ccsds_header

    # Append bytes to packet
    packet = packet + \
        telemetry_packet_type.to_bytes(TELEMETRY_TYPE_LENGTH, 'big')
    packet = packet + current_batch.to_bytes(CURRENT_BATCH_LENGTH, 'big')
    packet = packet + current_chunk.to_bytes(CURRENT_CHUNKS_LENGTH, 'big')

    # Append payload bytes into packet
    packet = packet + payload

    return packet


# Function to initiate a batch tx
def batch_send(serial_obj, batch_arr, short_delay, long_delay, current_batch):

    # Initiate downlink of chunk packets in the batch
    chunk_counter = 0
    while chunk_counter < len(batch_arr):

        # Create CCSDS packet
        packet = ccsds_create_downlink_chunk_packet(
            TELEMETRY_PACKET_TYPE_DOWNLINK_PACKET, current_batch, chunk_counter, batch_arr[chunk_counter])

        print(
            f"Sending {chunk_counter+1} out of {BATCH_SIZE} of length {len(packet)}")
        serial_obj.write(packet)

        if chunk_counter % 100 == 0:
            time.sleep(long_delay)
        else:
            time.sleep(short_delay)
        chunk_counter = chunk_counter + 1

    time.sleep(TIME_SLEEP_AFTER_END)


# Returns an array of chunks of bytes, given chunk size and bytes array
def chop_bytes(bytes_arr, chunk_size):
    chunk_arr = []
    idx = 0

    while idx + chunk_size < len(bytes_arr):
        chunk_arr.append(bytes_arr[idx:idx + chunk_size])
        idx = idx + chunk_size

    # Remaining odd sized chunk
    chunk_arr.append(bytes_arr[idx:])

    return chunk_arr


# Given an array of chunks, split them into array of batches given a batch size
def split_batch(chunks_arr, batch_size):
    batch_arr = []
    idx = 0

    while idx + batch_size <= len(chunks_arr):
        batch_arr.append(chunks_arr[idx:idx + batch_size])
        idx = idx + batch_size

    # Remaining odd sized chunk
    batch_arr.append(chunks_arr[idx:])

    return batch_arr
