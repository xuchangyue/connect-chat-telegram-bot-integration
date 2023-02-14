import json
import os
import sys
import boto3
from pprint import pprint
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "./vendored"))
from boto3.dynamodb.conditions import Key


connect = boto3.client('connect')
participant = boto3.client('connectparticipant')
dynamodb = boto3.resource('dynamodb')

# instance_id = '39bcdf01-1b4a-4c8f-8fb6-330e2f9960b7'
# contact_flow_id = 'f13177bf-bc01-4eb9-9104-864623cf3c2a'
# streaming_sns_arn = 'arn:aws:sns:ap-northeast-1:746872035549:chat-streaming'
# table_name = 'ConnectChat-TelegramBot'
table_name = os.environ['TABLE_NAME']
instance_id = os.environ['INSTANCE_ID']
streaming_sns_arn = os.environ['STREAMING_SNS_ARN']
contact_flow_id = os.environ['CONTACT_FLOW_ID']

table = dynamodb.Table(table_name)


def start_chat(first_message, username, chat_id):

    connect_response = connect.start_chat_contact(
        InstanceId=instance_id,
        ContactFlowId=contact_flow_id,
        Attributes={
            'string': 'string'
        },
        ParticipantDetails={
            'DisplayName': username
        },
        InitialMessage={
            'ContentType': 'text/plain',
            'Content': first_message
        }
    )

    participant_id = connect_response['ParticipantId']
    participant_token = connect_response['ParticipantToken']
    contact_id = connect_response['ContactId']
    pprint(connect_response)

    streaming_response = connect.start_contact_streaming(
        InstanceId=instance_id,
        ContactId=contact_id,
        ChatStreamingConfiguration={
        'StreamingEndpointArn': streaming_sns_arn
        }
    )
    participant_connection_response = participant.create_participant_connection(
        Type=[
            'WEBSOCKET', 'CONNECTION_CREDENTIALS'
            ],
        ParticipantToken=participant_token,
        ConnectParticipant=True
    )
    connection_token = participant_connection_response['ConnectionCredentials']['ConnectionToken']
    connection_expriy = participant_connection_response['ConnectionCredentials']['Expiry']
    table.put_item(
        Item={
            'ContactId': contact_id,
            'ChatId': chat_id,
            'ConnectionToken': connection_token,
            'ConenctionExpiry': connection_expriy,
            'Username': username
        }
    )
    
    
    return participant_connection_response


    
def lambda_handler(event, context):
    try:
        #pprint(event)
        
        data = json.loads(event["body"])
        message = str(data["message"]["text"])
        pprint(message)
        
        chat_id = str(data["message"]["chat"]["id"])
        first_name = data["message"]["chat"]["first_name"]
        ddb_response = table.query(
            IndexName='ChatId-index',
            Limit=1,
            ConsistentRead=False,
            KeyConditionExpression=Key('ChatId').eq(chat_id),
            )

        items = ddb_response['Items']
        pprint(items)

        if items == []:
            start_chat(message, first_name, chat_id)
            
        else:
            connection_token = items[0]['ConnectionToken']
            participant.send_message(
                ContentType='text/plain',
                Content=message,
                ConnectionToken=connection_token
                )

    except Exception as e:
        print(e)

    return {"statusCode": 200}
