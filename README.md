
Critter Consumer
==========
This project contains the handler function for all critter events. It will listen to the Kinesis stream and parse each
event, storing them in the appropriate place.

This handler does three major tasks:

1. For MOTION_DETECTED events, it will store them in the critter_events table
2. For MOTION_DETECTED events, it will send them to SNS which will send an SMS to the subscribed phone number
3. For VOLTAGE events, it will update the critter_devices table with the latest reported battery voltage and timestamp
of when it was received.

### Deployment

This project uses [zappa](https://github.com/Miserlou/Zappa)to deploy. You will first need to change some basic config,
such as the Kinesis ARN in the zappa_settings.json file.

To deploy, make sure you have the correct aws credentials on your system and do the following (on mac or linux):

```
virtualenv env
source env/bin/activate
pip install -r requirements.txt
python create_dynamo_tables.py
zappa deploy prod
```

This will deploy the lambda function to your AWS account and create the two necessary DynamoDB tables.