import json
import boto3

# Khởi tạo client DynamoDB
dynamodb = boto3.client('dynamodb')

def lambda_handler(event, context):
    try:
        # Truy xuất connectionId từ sự kiện API Gateway WebSocket
        connection_id = event['requestContext'].get('connectionId')
        print(connection_id)
        
        # Truy vấn tất cả các bản ghi trong bảng caro-user-online
        response = dynamodb.scan(
            TableName='caro-user-online'
        )

        # Lấy danh sách các bản ghi từ kết quả truy vấn
        items = response.get('Items', [])

        # Chuyển đổi dữ liệu thành định dạng JSON
        data = [{'username': item['username']['S']} for item in items]

        # Trả về dữ liệu cho client thông qua connectionId
        send_response(connection_id, data, event)

        # Trả về phản hồi cho Lambda
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Data sent successfully to connectionId'})
        }
    except Exception as e:
        # Xử lý các lỗi có thể xảy ra và trả về thông báo lỗi cho client
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

def send_response(connection_id, data, event):
    try:
        # Khởi tạo client API Gateway Management API
        apigatewaymanagementapi = boto3.client(
            'apigatewaymanagementapi', 
            endpoint_url = "https://" + event["requestContext"]["domainName"] + "/" + event["requestContext"]["stage"]
        )

        # Gửi dữ liệu đến connectionId thông qua API Gateway Management API
        apigatewaymanagementapi.post_to_connection(
            ConnectionId=connection_id,
            Data=json.dumps(data)
        )
    except Exception as e:
        print("Error sending response to client:", e)

