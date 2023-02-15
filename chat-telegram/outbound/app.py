import json
import os
import sys
import boto3
from pprint import pprint
import requests
from boto3.dynamodb.conditions import Key


TOKEN = os.environ['TELEGRAM_TOKEN']
BASE_URL = "https://api.telegram.org/bot{}".format(TOKEN)
dynamodb = boto3.resource('dynamodb')
table_name = os.environ['TABLE_NAME']
table = dynamodb.Table(table_name)


def lambda_handler(event, context):
    try:
        agent_message = json.loads(event['Records'][0]['Sns']['Message'])
        pprint(agent_message)
        contact_id = agent_message['ContactId']
        content = agent_message['Content']
        ddb_response = table.get_item(
            Key={'ContactId': contact_id}
            )
        pprint(ddb_response)

        chat_id = ddb_response['Item']['ChatId']

        response = content

        data = {"text": response.encode("utf8"), "chat_id": chat_id}
        url = BASE_URL + "/sendMessage"
        requests.post(url, data)

    except Exception as e:
        print(e)

    return {"statusCode": 200}
