import os
import pandas as pd
import numpy as np
import unicodecsv
import datetime as dt
from azure.storage.blob import BlockBlobService
from azure.storage.blob import ContentSettings
from azure.storage.table import TableService, Entity
from azure.common import AzureHttpError, AzureConflictHttpError, AzureMissingResourceHttpError

# ##########################
account = os.environ.get('ACCOUNT')
account_key = os.environ.get('ACCOUNT_KEY')
block_blob_service = BlockBlobService(account_name=account, account_key=account_key)
azure_container = 'rides'
azure_path = 'data/'
azure_saved_path = azure_path + 'saved/'
temp_path = ''
# ##########################

def get_rides():
    file = 'table_rides.csv'
    try:
        rides = open_local_file(file) 
    except FileNotFoundError:
        block_blob_service.get_blob_to_path(azure_container, azure_path + file, temp_path + file)
        rides = open_local_file(file)
    
    return rides


def open_local_file(file):
    ''' Using this to save traffic and speed everythign up '''
    with open(temp_path + file, 'rb') as f:
        reader = unicodecsv.DictReader(f)
        rides = list(reader)
    return rides


def get_ride_and_json(id):

    ride_metadata = get_ride_metadata(id)

    file = 'id_' + str(id) + '_only_changing_mph.json'

    try:
        # ride data # json_path = 'trails/data/id_' + str(id) + '_only_changing_mph.json'
        with open (temp_path + file, "r") as ride_file:
            data = ride_file.read()    
    except FileNotFoundError:
        # get file from azure blob
        block_blob_service.get_blob_to_path(azure_container, azure_path + file, temp_path + file)
        # ride data # json_path = 'trails/data/id_' + str(id) + '_only_changing_mph.json'
        with open (temp_path + file, "r") as ride_file:
            data = ride_file.read()    

    return [ride_metadata, data]


    
def get_ride_metadata(id):
    ''' Gets the ride metadata '''
    rides = get_rides()
    ride = [ride for ride in rides if int(ride['id']) is id]

    return ride[0]


def get_ride_as_dataframe(ride_id):
    '''load calibrated data and return is as a dataframe'''
    
    file = 'id_' + str(ride_id) + '_calibrated.csv'

    try:
        ride = pd.read_csv(temp_path + file)
    except FileNotFoundError:
        # get file from azure blob
        block_blob_service.get_blob_to_path(azure_container, azure_path + file, temp_path + file)
        ride = pd.read_csv(temp_path + file)
    
    return ride


def get_calibrated_subset(trail_id, org_start_point, org_end_point):
    ''' takes a start and end point from the MPH data and 
        returns a subset of the calibrated data -/+100 rows '''

    # load calibrated
    file = 'id_' + str(trail_id) + '_calibrated.csv'

    try:
        ride = pd.read_csv(temp_path + file)
    except FileNotFoundError:
        # get file from azure blob
        block_blob_service.get_blob_to_path(azure_container, azure_path + file, temp_path + file)
        ride = pd.read_csv(temp_path + file)

    deviation = 100

    # make subset 
    raw = ride.iloc[org_start_point-deviation:org_end_point+deviation, :]
    trail = raw.copy()

    trail.drop(['AccelX','AccelY','AccelZ','GyroX','GyroY','GyroZ', 'MagX','MagY','MagZ','Speed'],1, inplace=True)
    trail['RowNum'] = trail.index

    # center the map 
    midpoint = int(len(trail)/2)
    trail_start_lat = trail.iloc[midpoint]['Latitude']
    trail_start_long = trail.iloc[midpoint]['Longitude']

    return deviation, trail_start_lat, trail_start_long, trail.to_json(orient='records')



def save_trail(ride_id, trail_name, start_point, end_point):
    ''' Saves the full calibrated csv for a given trail '''

    # TODO
    # update another file and associate the trail with the ride
    # insert it and get the new ID. 
    # ride_id + trail_id

    # TODO
    # Test if the file is already in the tmp folder.

    # Get full ride as dataframe
    ride_df = get_ride_as_dataframe(ride_id)

    # make a subset based on start and end_point
    trail = ride_df.iloc[start_point:end_point, :]
    
    # create a path based on ride id, trail name, and duration. That combo should be unique.
    start_time_raw = ride_df.iloc[start_point]['Time']
    end_time_raw = ride_df.iloc[end_point]['Time']
    
    duration = get_duration(start_time_raw, end_time_raw)

    file = trail_name + '_' + duration +  '_' + 'rideid_' + str(ride_id) + '.csv'

    # save the trail instance
    trail.to_csv(temp_path + file, index=False)
    block_blob_service.create_blob_from_path(
        azure_container,
        azure_saved_path + file,
        temp_path + file,
        content_settings = ContentSettings(content_type='text/csv'))

    # Associate Run with Ride
    table_service = TableService(account_name=account_name, account_key=account_key)
    run = {'PartitionKey': file, 'RowKey': str(ride_id), 'name': trail_name, 'duration': duration}
    table_service.insert_entity('runs', run)

    return True



# ##################################
# HELPER FUNCTIONS 
def get_duration(start_time_raw, end_time_raw):
    # A time comes in this format: '2016/11/24 12:04:00.2910'
    # start by generating datetimes
    start_time = dt.datetime.strptime(start_time_raw, "%Y/%m/%d %H:%M:%S.%f")
    end_time = dt.datetime.strptime(end_time_raw, "%Y/%m/%d %H:%M:%S.%f") 

    # td is a timedelta
    td = end_time - start_time

    # just the minutes without the seconds
    minutes = int(td.seconds / 60)

    # take just the seconds. modulo
    seconds = td.seconds % 60 

    # microseconds in just two decimals. 
    miliseconds = int(td.microseconds /10000)

    # return format: 3:23:82
    return str(minutes) + '.' + str(seconds) + '.' + str(miliseconds)




