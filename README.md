Review Analyzer – Mini Serverless Pipeline (Week 6)

Simple AWS pipeline that ingests JSON “reviews” from S3, processes them with Lambda, and publishes custom CloudWatch metrics with a dashboard and alarm.

Services: S3 → Lambda (Python 3.12) → CloudWatch Logs & Metrics

Custom Metrics: AvgWordLen (Average) and ReviewCount (Sum)

Namespace: ReviewAnalyzer

Trigger: S3 object create for incoming/*.json

How it works

Upload a file such as

{"review": "These headphones are very comfortable"}


into s3://<bucket>/incoming/….

S3 triggers Lambda.

Lambda extracts review, calculates the average word length, and emits metrics.

CloudWatch dashboard visualizes AvgWordLen and ReviewCount.

An alarm monitors AvgWordLen and can notify via SNS.

Quick Start (CLI)
BUCKET=review-analyzer-briana-4nk3j3
FUNCTION=process-reviews
REGION=$(aws configure get region)

# Direct invoke
aws lambda invoke \
  --function-name $FUNCTION \
  --cli-binary-format raw-in-base64-out \
  --payload '{"review":"quick smoke test"}' \
  /dev/null >/dev/null

# Simulator
python3 tools/simulator.py --bucket $BUCKET --batch 6 --spike-every 3

Dashboard & Alarm

Dashboard: ReviewAnalyzer

AvgWordLen → Namespace ReviewAnalyzer, Stat Average (1 min)

ReviewCount → Namespace ReviewAnalyzer, Stat Sum (1 min)

Set time range to Last 1 hour and refresh.
Alarm: triggers if AvgWordLen > threshold for 1 datapoint.

Lambda Details

File: lambda/lambda_function.py

Handler: lambda_function.lambda_handler

Env var: METRIC_NS=ReviewAnalyzer

Modes:

Direct ({"review":"..."} or {"text":"..."})

Manual ({"bucket":"...","key":"..."})

S3 event trigger

Runbook (Ops)

Force a data point

aws lambda invoke \
  --function-name process-reviews \
  --cli-binary-format raw-in-base64-out \
  --payload '{"review":"ops smoke test"}' /dev/null


Tail logs

aws logs tail /aws/lambda/process-reviews --since 15m --follow


Teardown (optional)

# 1) Disable S3 trigger
aws s3api put-bucket-notification-configuration \
  --bucket <your-bucket> \
  --notification-configuration '{}'

# 2) Delete bucket contents
aws s3 rm s3://<your-bucket>/ --recursive
aws s3api delete-bucket --bucket <your-bucket>

# 3) Delete Lambda (optional)
aws lambda delete-function --function-name process-reviews

Project Structure
review-pipeline/
├─ lambda/
│  └─ lambda_function.py
├─ tools/
│  └─ simulator.py
├─ README.md
└─ .gitignore


Notes: Metrics take ~1–2 minutes to appear. Namespace is case-sensitive.
