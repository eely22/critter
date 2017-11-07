import boto3
import json
import base64
import logging
from dateutil import parser
from decimal import *

# -----------------------------------------------------------------------------------------------
class SMSAutomation:
    def __init__(self, region='us-west-2'):
        self.__client = boto3.client('sns', region_name=region)

    def send_critter_alert(self, phone_number, trap_name=None):
        self.__client.publish(
            PhoneNumber = phone_number,
            Message="Trap sprung!" + ("" if trap_name is None else " Check trap %s" % trap_name)
        )

def critter_handler(event, context):
    for record in event['Records']:
        data = json.loads(base64.b64decode(record['kinesis']['data']))
        logging.debug(data)

        # process event based on type
        if data['event_type'] in ['MOTION_DETECTED', 'TRAP_TRIGGERED']:
            process_critter_action_event(data)
        elif data['event_type'] in ['VOLTAGE']:
            process_critter_battery_event(data)

def process_critter_battery_event(data):
    dynamodb = boto3.resource('dynamodb')
    devices_table = dynamodb.Table("critter_devices")

    # save the last reported voltage to the devices table
    device = devices_table.get_item(Key={"device_id": data['device_id']})
    if "Item" in device:
        item = device["Item"]
        item["last_reported_timestamp"] = str(data['timestamp'])
        item["last_reported_voltage"] = Decimal(str(round(int(data['event_value']) / 1024.0 * 3.6 * 1000) / 1000))
        devices_table.put_item(Item=item)

def process_critter_action_event(data):
    # create the item to store
    try:
        item = {}
        item['event_type'] = data['event_type']
        item['device_id'] = data['device_id']
        item['timestamp'] = str(data['timestamp'])
        item['timestamp_int'] = int(parser.parse(data['timestamp']).strftime("%s")) * 1000
    except Exception as ex:
        logging.warn("improper event")

    # store it in the table
    dynamodb = boto3.resource('dynamodb')
    events_table = dynamodb.Table("critter_events")
    events_table.put_item(Item=item)

    if 'event_type' in data and data['event_type'] == "TRAP_TRIGGERED":
        #TODO Look up phone number and send SMS
        devices_table = dynamodb.Table("critter_devices")
        device_name = devices_table.get_item(Key={"device_id": item['device_id']})

        name = None
        if "Item" in device_name and "name" in device_name["Item"]:
            name = device_name["Item"]["name"]


        sns = SMSAutomation()
        sns.send_critter_alert("+13023775569", trap_name=name)
