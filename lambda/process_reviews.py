import json
import boto3
import statistics

cloudwatch = boto3.client('cloudwatch')

def lambda_handler(event, context):
    # Logs the event
    print("Event:", json.dumps(event))

    # 1️⃣ Parse S3 event
    record = event['Records'][0]
    bucket = record['s3']['bucket']['name']
    key = record['s3']['object']['key']

    # 2️⃣ Download file from S3
    s3 = boto3.client('s3')
    obj = s3.get_object(Bucket=bucket, Key=key)
    data = obj['Body'].read().decode('utf-8')

    try:
        review_data = json.loads(data)
        review = review_data.get("review", "")
    except Exception:
        review = data.strip()

    # 3️⃣ Compute metrics
    char_len = len(review)
    words = review.split()
    word_len = len(words)
    avg_word_len = statistics.mean([len(w) for w in words]) if words else 0

    print(f"Chars: {char_len}, Words: {word_len}, AvgWordLen: {avg_word_len}")

    # 4️⃣ Publish custom metrics
    cloudwatch.put_metric_data(
        Namespace='ReviewAnalyzer',
        MetricData=[
            {'MetricName': 'ReviewCount', 'Value': 1, 'Unit': 'Count'},
            {'MetricName': 'AvgCharLen', 'Value': char_len, 'Unit': 'Count'},
            {'MetricName': 'AvgWordLen', 'Value': avg_word_len, 'Unit': 'Count'}
        ]
    )

    return {
        'statusCode': 200,
        'body': json.dumps('Metrics sent successfully!')
    }

