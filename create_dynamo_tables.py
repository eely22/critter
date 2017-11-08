import boto3

region = 'us-west-2'

dynamodb = boto3.resource('dynamodb', region_name=region)
critter_devices_table = dynamodb.create_table(
            AttributeDefinitions=[
                {
                    'AttributeName': 'device_id',
                    'AttributeType': 'S'
                },
            ],
            TableName='critter_devices2',
            KeySchema=[
                {
                    'AttributeName': 'device_id',
                    'KeyType': 'HASH'
                },
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 3,
                'WriteCapacityUnits': 3
            }
        )
critter_devices_table.wait_until_exists()

critter_events_table = dynamodb.create_table(
            AttributeDefinitions=[
                {
                    'AttributeName': 'device_id',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'timestamp_int',
                    'AttributeType': 'S'
                },
            ],
            TableName='critter_events2',
            KeySchema=[
                {
                    'AttributeName': 'device_id',
                    'KeyType': 'HASH'
                },
                {
                    'AttributeName': 'timestamp_int',
                    'KeyType': 'RANGE'
                },
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 3,
                'WriteCapacityUnits': 3
            }
        )
critter_events_table.wait_until_exists()