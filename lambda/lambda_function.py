import json, os, boto3, urllib.parse

cw = boto3.client("cloudwatch")
s3 = boto3.client("s3")
METRIC_NS = os.getenv("METRIC_NS", "ReviewAnalyzer")

def _emit_metrics(avg_word_len=None, count=None):
    data = []
    if avg_word_len is not None:
        data.append({
            "MetricName": "AvgWordLen",
            "Value": float(avg_word_len),
            "Unit": "None"
        })
    if count is not None:
        data.append({
            "MetricName": "ReviewCount",
            "Value": int(count),
            "Unit": "Count"
        })
    if not data:
        return
    cw.put_metric_data(Namespace=METRIC_NS, MetricData=data)

def _avg_word_len(text: str) -> float:
    words = [w for w in text.strip().split() if w]
    if not words:
        return 0.0
    lengths = [len(w) for w in words]
    return sum(lengths) / len(lengths)

def _process_review(text: str):
    avg = _avg_word_len(text)
    _emit_metrics(avg_word_len=avg, count=1)
    print(f"[OK] Emitted metrics: AvgWordLen={avg:.2f}, ReviewCount=1, NS={METRIC_NS}")

def _from_s3(bucket: str, key: str):
    key = urllib.parse.unquote_plus(key)
    obj = s3.get_object(Bucket=bucket, Key=key)
    body = obj["Body"].read().decode("utf-8", errors="replace")
    try:
        payload = json.loads(body)
        text = payload.get("review") or payload.get("text") or body
    except Exception:
        text = body
    _process_review(text)

def lambda_handler(event, context):
    print(f"[EVENT] {json.dumps(event)[:500]}")

    # Mode 1: Direct text { "review": "..."} or {"text":"..."}
    if isinstance(event, dict) and (event.get("review") or event.get("text")):
        text = event.get("review") or event.get("text")
        _process_review(text)
        return {"statusCode": 200, "body": json.dumps("Metrics sent (direct)")}
    
    # Mode 2: Manual S3 { "bucket":"...", "key":"..." }
    if isinstance(event, dict) and event.get("bucket") and event.get("key"):
        _from_s3(event["bucket"], event["key"])
        return {"statusCode": 200, "body": json.dumps("Metrics sent (manual s3)")}

    # Mode 3: S3 event trigger
    if isinstance(event, dict) and event.get("Records"):
        for rec in event["Records"]:
            if rec.get("eventSource") == "aws:s3":
                b = rec["s3"]["bucket"]["name"]
                k = rec["s3"]["object"]["key"]
                _from_s3(b, k)
        return {"statusCode": 200, "body": json.dumps("Metrics sent (s3 trigger)")}

    print("[WARN] Unrecognized event shape; no metrics emitted.")
    return {"statusCode": 400, "body": json.dumps("Unrecognized event")}
