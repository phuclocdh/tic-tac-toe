import json
import boto3

dynamodb = boto3.client('dynamodb')

def lambda_handler(event, context):
    try:
        # Kiểm tra xem sự kiện có chứa 'body' không
        if 'body' not in event:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'No message body provided'})
            }

        # Giải mã JSON để lấy thông điệp từ sự kiện WebSocket
        message = json.loads(event['body']).get('message')

        # Kiểm tra xem thông điệp có tồn tại không
        if not message:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'No message provided'})
            }

        # Truy xuất connectionId từ sự kiện API Gateway WebSocket
        connection_id = event['requestContext'].get('connectionId')

        # Truy vấn bảng caro-connection để lấy username dựa vào connectionId
        response = dynamodb.query(
            TableName='caro-connection',
            KeyConditionExpression='connectionId = :c',
            ExpressionAttributeValues={
                ':c': {'S': connection_id}
            }
        )

        # Kiểm tra xem connectionId có tồn tại không
        if not response['Items']:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'ConnectionId not found'})
            }

        # Lấy username từ kết quả truy vấn
        username = response['Items'][0].get('username', {}).get('S')

        # Gửi tin nhắn kèm username đến từng connectionId
        send_message_to_connections(event, message, username)

        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Message sent successfully'})
        }

    except Exception as e:
        # Xử lý các lỗi có thể xảy ra và trả về thông báo lỗi cho client
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

def send_message_to_connections(event, message, username):
    # Truy vấn tất cả các connectionId từ bảng caro-connection
    paginator = dynamodb.get_paginator('scan')
    connection_ids = []

    for page in paginator.paginate(TableName='caro-connection'):
        connection_ids.extend(page['Items'])

    # Khởi tạo client API Gateway Management API
    apigatewaymanagementapi = boto3.client(
        'apigatewaymanagementapi', 
        endpoint_url = "https://" + event["requestContext"]["domainName"] + "/" + event["requestContext"]["stage"]
    )

    # Gửi tin nhắn kèm username đến từng connectionId
    for connection_id in connection_ids:
        try:
            apigatewaymanagementapi.post_to_connection(
                ConnectionId=connection_id['connectionId']['S'],
                Data=f"{username}: {message}"
            )
        except Exception as e:
            print(f"Error sending message to connection {connection_id['connectionId']['S']}: {e}")
