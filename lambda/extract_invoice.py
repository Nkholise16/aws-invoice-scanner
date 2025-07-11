import json
import boto3
import re
import uuid

def extract_fields(text):
    lines = text.splitlines()
    full_text = ' '.join(lines)

    # Match Invoice or Quote ID
    invoice_id = re.search(r'(invoice|quote)[^\n:]*[:\s\-#]*([A-Z0-9\-\/]+)', full_text, re.IGNORECASE)

    # Match flexible date formats
    date = re.search(r'date[:\s\-]*([0-9]{2}[/-][0-9]{2}[/-][0-9]{4})', full_text, re.IGNORECASE)

    # Match total from variations (grand total, balance due, etc.)
    total_match = re.search(
        r'\b(grand\s+total|total\s+(to\s+be\s+paid)?|balance\s+due)\b[^\dR$]*[\s\n]*[R$]?\s*([0-9,]+\.\d{2})',
        full_text,
        re.IGNORECASE
    )

    # Vendor logic: basic match or fallback to N/A
    vendor = re.search(r'vendor[:\s]*([^\n]+)', text, re.IGNORECASE)
    vendor_value = vendor.group(1).strip() if vendor else 'N/A'

    return {
        'invoice_id': invoice_id.group(2) if invoice_id else str(uuid.uuid4()),
        'date': date.group(1) if date else 'N/A',
        'total': total_match.group(3) if total_match else 'N/A',
        'vendor': vendor_value
    }

def lambda_handler(event, context):
    textract = boto3.client('textract')
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Scanned_invoices')

    record = event['Records'][0]
    bucket = record['s3']['bucket']['name']
    key = record['s3']['object']['key']

    if not key.lower().endswith(('.pdf', '.jpg', '.jpeg')):
        print(f"Unsupported file type: {key}")
        return {'statusCode': 400, 'body': 'Unsupported file type'}

    try:
        response = textract.detect_document_text(
            Document={'S3Object': {'Bucket': bucket, 'Name': key}}
        )

        text = ' '.join([block['Text'] for block in response['Blocks'] if block['BlockType'] == 'LINE'])
        fields = extract_fields(text)
        print("Extracted Fields:", fields)

        table.put_item(Item=fields)

        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Invoice processed', 'data': fields})
        }

    except Exception as e:
        print("Error:", str(e))
        return {'statusCode': 500, 'body': json.dumps({'error': str(e)})}
