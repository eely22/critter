import boto3, time, json

region = 'us-west-2'
stream_to_create = 'critter'

def wait_until_exists(kinesis, stream_name):
    response = kinesis.describe_stream(StreamName=stream_name)
    while response['StreamDescription']['StreamStatus'] == 'CREATING':
        time.sleep(3)
        response = kinesis.describe_stream(StreamName=stream_name)

    return response['StreamDescription']['StreamARN']

# create the stream
kinesis = boto3.client('kinesis', region_name=region)
response = kinesis.create_stream(
    StreamName=stream_to_create,
    ShardCount=1
)

# wait for it to exist, and then get the ARN back
stream_arn = wait_until_exists(kinesis, stream_to_create)

# update zappa_settings.json file with the Kinesis ARN
with open('zappa_settings.json') as f:
    settings = json.loads(f.read())

# write the zappa settings back to the file
settings['prod']['events'][0]['event_source']['arn'] = stream_arn
with open('zappa_settings.json', 'w') as f:
    f.write(json.dumps(settings, indent=4))
