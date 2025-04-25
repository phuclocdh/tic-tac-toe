import boto3
import json
import uuid  # Import thư viện để tạo UUID

# Khởi tạo client DynamoDB
dynamodb = boto3.client('dynamodb')
# Khởi tạo client API Gateway

def lambda_handler(event, context):
    # Lấy thông điệp từ sự kiện WebSocket
    message = event['body']
    try:
        # Giải mã JSON
        message_json = json.loads(message)
        # Lấy username từ thông điệp
        username = message_json.get('username')
        # Kiểm tra nếu không có username
        if not username:
            return {
                'statusCode': 400,
                'body': 'Missing username in the request'
            }
        
        # Truy vấn bảng caro-user-online để tìm connectionId tương ứng với username
        response = dynamodb.query(
            TableName='caro-user-online',
            KeyConditionExpression='username = :u',
            ExpressionAttributeValues={
                ':u': {'S': username}
            }
        )

        # Kiểm tra nếu không tìm thấy username trong bảng caro-user-online
        if not response['Items']:
            return {
                'statusCode': 404,
                'body': 'Username not found in caro-user-online'
            }

        # Lấy connectionId từ kết quả truy vấn
        connection_id = response['Items'][0]['connectionId']['S']
        
        # Lấy connectionId của client truyền event và lưu vào biến idInviter
        id_inviter = event['requestContext'].get('connectionId')
        
        # Truy vấn bảng caro-connection để tìm username tương ứng với connectionId
        response_inviter = dynamodb.query(
            TableName='caro-connection',
            KeyConditionExpression='connectionId = :c',
            ExpressionAttributeValues={
                ':c': {'S': id_inviter}
            }
        )

        # Kiểm tra nếu không tìm thấy connectionId trong bảng caro-connection
        if not response_inviter['Items']:
            return {
                'statusCode': 404,
                'body': 'ConnectionId not found in caro-connection'
            }

        # Lấy username của inviter từ kết quả truy vấn
        inviter = response_inviter['Items'][0]['username']['S']

        # Tạo requestId ngẫu nhiên
        request_id = str(uuid.uuid4())

        # Ghi giá trị vào bảng caro-request
        try:
            dynamodb.put_item(
                TableName='caro-request',
                Item={
                    'requestId': {'S': request_id},  # Sử dụng requestId làm khóa chính
                    'invite': {'S': username},
                    'idInvite': {'S': connection_id},
                    'idInviter': {'S': id_inviter},  # Thêm idInviter vào bảng
                    'inviter': {'S': inviter}  # Thêm inviter vào bảng
                }
            )
            delete_records(username, inviter)
            
            return {
                'statusCode': 200,
                'body': 'Invite sent successfully'
            }
        except Exception as e:
            return {
                'statusCode': 500,
                'body': f'Error: {str(e)}'
            }
    except Exception as e:
        return {
            'statusCode': 400,
            'body': f'Invalid message format: {str(e)}'
        }

def delete_records(username, inviter):
    try:
        # Xoá các bản ghi trong bảng caro-user-online dựa trên giá trị của username và inviter
        dynamodb.delete_item(
            TableName='caro-user-online',
            Key={'username': {'S': username}}
        )
        dynamodb.delete_item(
            TableName='caro-user-online',
            Key={'username': {'S': inviter}}
        )
    except Exception as e:
        print("Error deleting records:", e)
