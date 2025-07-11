# AWS Serverless Invoice Scanner 

This is a project I built using AWS Free Tier services to put my data analytics/science and aws cloud computing skills to practice.

## What It Does?

- You upload a PDF or JPEG of an invoice
- AWS automatically:
  - Extracts the text using Textract
  - Finds the invoice number, date, total, and vendor using Python + regex
  - Saves the result into DynamoDB (NoSQL Database)

## Technologies/AWS Services Used

- AWS Lambda
- Amazon Textract
- S3
- DynamoDB
- Python (for data extraction)
- IAM (for permissions)
- Amplify (for hosting the frontend)

## Limitations / Areas of Improvement

**"Total Amount" Extraction issue:** 
  - In some invoices, the total is part of a table or multi-line layout.
  - Amazon Textract’s `detect_document_text()` sometimes misses this due to layout formatting.
  - For better accuracy, I believe I could use:
    - Textract's `analyze_document()` feature with table detection
    - Amazon Bedrock (LLM) to extract structured fields using natural language

**"Vendor" Extraction:** 
  - The app assumes the vendor is labelled, which isn't always the case.

**Template Dependence:**  
  - This scanner works best when invoices follow a fairly consistent format/template (e.g. internal company use).
  - For scanning invoices from many vendors, additional AI or ML tools would be needed.
## Sample Output

```json
{
  "invoice_id": "QUO0005115",
  "date": "15/05/2025",
  "total": "520.00",
  "vendor": "N/A"
}
