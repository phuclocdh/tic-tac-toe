import json
import boto3

dynamodb = boto3.client('dynamodb')

def lambda_handler(event, context):
    connectionId = event['requestContext']['connectionId']
    username = json.loads(event['body']).get('username', None)

    if username is None:
        return {
            'statusCode': 400,
            'body': json.dumps('Missing username in request.')
        }

    # Kiểm tra xem username đã tồn tại trong bảng caro-user chưa
    user_exists = check_user_existence(username)

    if user_exists:
        send_response(event, connectionId, 'Username already exists.')
        return {
            'statusCode': 400,
            'body': json.dumps('Username already exists.')
        }

    # Ghi username vào bảng caro-user và caro-user-online
    write_username_to_tables(username, connectionId)
    # Ghi username vào connectionId tương ứng trong bảng caro-connection
    update_connectionId(event, username, connectionId)
    return {
        'statusCode': 200,
        'body': json.dumps('All operations completed successfully.')
    }

def check_user_existence(username):
    try:
        response = dynamodb.get_item(
            TableName='caro-user',
            Key={'username': {'S': username}}
        )
        return 'Item' in response
    except Exception as e:
        print("Error checking user existence:", e)
        return False

def write_username_to_tables(username, connectionId):
    try:
        # Thêm username vào bảng caro-user
        dynamodb.put_item(
            TableName='caro-user',
            Item={'username': {'S': username}}
        )

        # Thêm dữ liệu connectionId vào bảng caro-user-online
        dynamodb.put_item(
            TableName='caro-user-online',
            Item={'username': {'S': username}, 'connectionId': {'S': connectionId}}
        )
    except Exception as e:
        print("Error writing username to tables:", e)

def update_connectionId(event, username, connectionId):
    try:
        dynamodb.update_item(
            TableName='caro-connection',
            Key={'connectionId': {'S': connectionId}},
            UpdateExpression='SET username = :user',
            ExpressionAttributeValues={':user': {'S': username}}
        )
    except Exception as e:
        print("Error updating connectionId:", e)
