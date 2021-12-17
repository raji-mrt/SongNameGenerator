import json
import boto3
from botocore.exceptions import ClientError


def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('blacklisted_words')

    method = event['httpMethod']
    print('Request Type ' + method)

    if method == 'GET':
        entries = table.scan()
        output = []
        for each_entry in entries['Items']:
            print(each_entry)
            output.append(each_entry['word'])
        return {
            'statusCode': 200,
            'body': json.dumps(output)
        }
    if method == 'POST':
        if event["queryStringParameters"]['word']:
            response = table.put_item(Item={'word': event["queryStringParameters"]['word']})
            return {
                'statusCode': 201,
                'body': json.dumps(event["queryStringParameters"]['word'] + ' added to blacklisted words')
            }
    if method == 'DELETE':
        if event["queryStringParameters"]['word']:
            try:
                response = table.delete_item(Key={'word': event["queryStringParameters"]['word']},
                                             ConditionExpression="attribute_exists (word)")
            except ClientError as e:
                if e.response['Error']['Code'] == "ConditionalCheckFailedException":
                    return {
                        'statusCode': 204,
                        'body': json.dumps(event["queryStringParameters"]['word'] + ' is not found in blacklisted words')
                    }
                else:
                    raise
            else:
                return {
                    'statusCode': 200,
                    'body': json.dumps(event["queryStringParameters"]['word'] + ' removed from blacklisted words')
                }


