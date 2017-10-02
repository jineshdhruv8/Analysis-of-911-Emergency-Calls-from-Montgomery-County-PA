from datetime import datetime
import math

__author__ = 'JINESH'

from geopy.geocoders import Nominatim
from googlemaps import Client
import csv
import time
import math
import datetime


twp_dict = {}

def read_csv(input_file):
    """
    This function will read the csv file
    :param input_file: Name of the file
    :return:
    """

    file = open(input_file, 'r', encoding='utf-8')
    reader = csv.reader(file)
    return reader


def write_csv_file(absolute_file_path, content_list, access_type):
    """
    This function will write post or campaign level metrics to the specified file

    Usage::

        >>> write_csv_file('Absolute_File_Path',['valid','list'],'a+')

    :param absolute_file_path:  The absolute path of output file
    :param content_list:        The metric list
    :param access_type:         It indicates type of access(write, append, etc.)
    :return:                    None

    """

    try:
        with open(absolute_file_path, access_type, encoding='utf-8', newline='') as file:
            wr = csv.writer(file)
            wr.writerow(content_list)

    except Exception as e:
        raise e


def custom_sleep(factor):
    """
    This function will sleep the current thread for exponential time

    :param factor: Number for sleep time
    :return:    Current Factor
    """
    print("Sleep : ", math.pow(2, factor), " seconds")
    time.sleep(math.pow(2, factor))
    factor += 1


def build_twp_dict(input_file):
    global twp_dict

    reader = read_csv(input_file)
    next(reader)  # Skip header

    for row in reader:
        twp = row[6]
        zipcode = row[3]

        if zipcode != "" and twp != "":
            if twp not in twp_dict:
                twp_dict[twp] = {zipcode: 1}
            else:
                zipcode_dict = twp_dict[twp]
                if zipcode not in zipcode_dict:
                    zipcode_dict[zipcode] = 1
                    twp_dict[twp] = zipcode_dict
                else:
                    zipcode_dict[zipcode] += 1
                    twp_dict[twp] = zipcode_dict

    print(twp_dict)



def clean(input_file, output_file):
    global twp_dict
    reader = read_csv(input_file)
    next(reader)  # skip header
    header = ['Latitude', 'Longitude', 'Description', 'Zip-Code', 'Title', 'Category', 'Reason', 'Time Stamp', 'Month_Num', 'Day_Num', 'Month', 'Day', 'Year', 'Hours', 'Minutes', 'TWP', 'ADDR' ]
    write_csv_file(output_file, header, 'w')
    c = 0
    for row in reader:
        new_row = []
        lat = row[0]
        long = row[1]
        desc = row[2]
        zipcode = row[3]
        title = row[4]
        timestamp = row[5]
        twp = row[6]
        addr = row[7]

        if zipcode == '' and twp != '':

            if twp in twp_dict:
                zipcode_dict = twp_dict[twp]
                zipcode = max(zipcode_dict, key=zipcode_dict.get)
            else:
                zipcode = get_zipcode(lat, long)

        # Extract time and date from timestamp
        date_list = timestamp.split(" ")[0].split("-")
        time_list = timestamp.split(" ")[1].split(":")
        year, month_num, day_num = date_list[0], date_list[1], date_list[2]
        day = datetime.date(int(year), int(month_num), int(day_num)).strftime("%a")
        month = datetime.date(int(year), int(month_num), int(day_num)).strftime("%b")
        hour, minutes = time_list[0], time_list[1]

        # Extract category & reason of emergency call
        category_list = title.split(":")
        reason = category_list[1][1:]
        category = category_list[0]

        if " -" in reason:
            reason = reason.replace(" -", "")

        # Modify Category
        if reason in ['ASSAULT VICTIM', 'SHOOTING', 'STABBING', 'HIT + RUN', 'ACTIVE SHOOTER', 'BOMB DEVICE FOUND', 'ARMED SUBJECT', 'PRISONER IN CUSTODY']:
            category = 'Crime'
        elif reason in ['VEHICLE ACCIDENT', 'INDUSTRIAL ACCIDENT', 'DISABLED VEHICLE']:
            category = 'Traffic'
        elif reason in ['CARDIAC EMERGENCY', 'FALL VICTIM', 'SYNCOPAL EPISODE', 'DIABETIC EMERGENCY', 'POLICE INFORMATION', 'UNCONSCIOUS SUBJECT',
                        'UNRESPONSIVE SUBJECT','ANIMAL COMPLAINT', 'STANDBY FOR ANOTHER CO', 'CARDIAC ARREST', 'RESCUE - WATER',
                        'UNKNOWN MEDICAL EMERGENCY', 'MEDICAL ALERT ALARM', 'TRANSFERRED CALL', 'RESCUE - GENERAL', 'RESCUE GENERAL',
                        'RESCUE ELEVATOR', 'RESCUE TECHNICAL', 'RESCUE WATER', 'EMS SPECIAL SERVICE']:
            category = 'EMS'
        elif reason in 'FIRE' in reason or reason in ['CARBON MONOXIDE DETECTOR', 'DEBRIS/FLUIDS ON HIGHWAY', 'TRAIN CRASH',
                                                      'S/B AT HELICOPTER LANDING','PUMP DETAIL', 'VEHICLE LEAKING FUEL',
                                                      'PLANE CRASH', 'GAS-ODOR/LEAK']:
            category = 'Fire'

        new_row = [lat, long, desc, zipcode, title, category, reason, timestamp, month_num, day_num, month, day, year, hour, minutes, twp, addr]
        write_csv_file(output_file, new_row, 'a+')


def get_zipcode(lat, long):
    api_key = "API_KEY"
    while True:
        try:
            gmaps = Client(key=api_key)
            destination = gmaps.reverse_geocode((lat, long))
            formatted_address = destination[0]['formatted_address'].split(",")
            zipcode = formatted_address[2].split(" ")[2]
            # geolocator = Nominatim()
            # loc = lat + "," + long
            # zipcode = geolocator.reverse(loc).raw['address']['postcode']
            return zipcode
        except Exception as e:
            custom_sleep(4)



def main():
    input_file = "911.csv"
    output_file = "cleaned_911.csv"

    build_twp_dict(input_file)
    clean(input_file,output_file)

if __name__ == "__main__":
    main()
