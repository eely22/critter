import boto3
import json
import base64
import logging
from dateutil import parser

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

        # create the item to store
        try:
            item = {}
            item['event_type'] = data['event_type']
            item['device_id'] = data['device_id']
            item['timestamp'] = str(data['timestamp'])
            item['timestamp_int'] = int(parser.parse(data['timestamp']).strftime("%s")) * 1000
            if 'event_value' in data:
                item['event_type'] = int(data['event_value'])
        except Exception as ex:
            logging.warn("improper event")

        # store it in the table
        dynamodb = boto3.resource('dynamodb')
        events_table = dynamodb.Table("critter_events")
        events_table.put_item(Item=item)

        if 'event_type' in data and data['event_type'] == "TRAP_TRIGGERED":
            #TODO Look up phone number and send SMS
            device_name_table = dynamodb.Table("critter_device_names")
            device_name = device_name_table.get_item(Key={"device_id": item['device_id']})

            name = None
            if "Item" in device_name and "name" in device_name["Item"]:
                name = device_name["Item"]["name"]


            sns = SMSAutomation()
            sns.send_critter_alert("+13023775569", trap_name=name)
