import json

def lambda_handler(event, context):
    # Kiểm tra xem có trường "message" trong dữ liệu respone không
    if 'message' in event:
        # Trích xuất giá trị của trường "message"
        message = event['message']
        print("Received message from respone:", message)
        
        # Trả về kết quả thành công
        return {
            'statusCode': 200,
            'body': json.dumps('Message received successfully!')
        }
    else:
        # Trả về lỗi nếu không tìm thấy trường "message" trong dữ liệu respone
        return {
            'statusCode': 400,
            'body': json.dumps('No "message" field found in the response!')
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
    # Xoá các bản ghi trong bảng caro-user-online dựa trên giá trị của username và inviter
            delete_records(username, inviter)
            
            return {
                'statusCode': 200,
                'body': 'Invite sent successfully'
            }
