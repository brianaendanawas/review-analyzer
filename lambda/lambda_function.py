import json
import boto3
import statistics

cloudwatch = boto3.client('cloudwatch')

def extract_reviews(raw_text: str):
    try:
        data = json.loads(raw_text)
    except Exception:
        return [raw_text.strip()] if raw_text.strip() else []

    if isinstance(data, dict):
        if "review" in data:
            return [str(data["review"])]
        if "reviews" in data:
            seq = data["reviews"]
        else:
            return [json.dumps(data)]
    else:
        seq = data

    out = []
    if isinstance(seq, (list, tuple)):
        for item in seq:
            if isinstance(item, dict) and "review" in item:
                out.append(str(item["review"]))
            else:
                out.append(str(item))
    else:
        out.append(str(seq))
    return [r for r in out if str(r).strip()]

def publish_metrics(review_texts):
    char_lens = [len(r) for r in review_texts]
    word_lens = [len(str(r).split()) for r in review_texts]
    avg_char_len = statistics.mean(char_lens) if char_lens else 0.0
    avg_word_len = statistics.mean(word_lens) if word_lens else 0.0
    review_count = len(review_texts)

    print(f"Processed {review_count} reviews | avg_char_len={avg_char_len:.2f} | avg_word_len={avg_word_len:.2f}")

    cloudwatch.put_metric_data(
        Namespace="ReviewAnalyzer",
        MetricData=[
            {"MetricName": "ReviewCount", "Value": float(review_count), "Unit": "Count"},
            {"MetricName": "AvgCharLen",  "Value": float(avg_char_len),  "Unit": "Count"},
            {"MetricName": "AvgWordLen",  "Value": float(avg_word_len),  "Unit": "Count"},
        ],
    )

def lambda_handler(event, context):
    print("Event:", json.dumps(event))
    record = event["Records"][0]
    bucket = record["s3"]["bucket"]["name"]
    key    = record["s3"]["object"]["key"]

    s3 = boto3.client("s3")
    obj = s3.get_object(Bucket=bucket, Key=key)
    body = obj["Body"].read().decode("utf-8")

    reviews = extract_reviews(body)
    publish_metrics(reviews)

    return {"statusCode": 200, "body": json.dumps("Metrics sent")}

