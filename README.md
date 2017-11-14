
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

This project uses [zappa](https://github.com/Miserlou/Zappa) to deploy. This project will build all necessary components
needed for critter to run, including the DynamoDB tables and Kinesis streams. All components will be built in us-west-2,
but you can change that in the scripts if you prefer, simply change the create_kinesis_stream.py and create_dynamo_tables.py
files.

To deploy, make sure you have python 2.7 installed and the correct aws credentials on your system and do the following
(on mac or linux):

```
virtualenv env
source env/bin/activate
pip install -r requirements.txt
python create_kinesis_stream.py
python create_dynamo_tables.py
zappa deploy prod
```

This will deploy the lambda function to your AWS account, create the Kinesis stream and update the Zappa settings file
 with the correct ARN, and create the two necessary DynamoDB tables.


#### IAM Permissions

The zappa deploy command requires special user privelages to be configured in IAM. This is due to how Zappa
assigns permissions. Normally, it assigns SNS permissions as follows:

```
{
    "Effect": "Allow",
        "Action": [
            "sns:*"
        ],
        "Resource": "arn:aws:sns:*:*:*"
},
```

However, this must ba changed to:

```
{
    "Effect": "Allow",
        "Action": [
            "sns:*"
        ],
        "Resource": "*"
},
```

So after the scripts are run, you will see a new IAM user added with the name critter-consume-prod-ZappaLambdaExecutionRole,
the permissions for the user must be changed as noted above or the consumer will not be able to sent SMS messages.