import json
import boto3
import os


table_name = os.environ['TABLE_NAME']
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(table_name)


def lambda_handler(event, context):
    
    
    agent_message = json.loads(event['Records'][0]['Sns']['Message'])
    contact_id = agent_message['ContactId']
    ddb_response = table.delete_item(Key={'ContactId': contact_id})
    
        
    return {
        'statusCode': 200,
        'body': json.dumps('deleted successfully')
    }
