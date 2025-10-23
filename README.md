# Review Analyzer Mini Pipeline

A small AWS serverless data-pipeline that processes incoming product reviews.

## 🧠 Overview
When a new review JSON file is uploaded to the S3 bucket’s **incoming/** folder,  
a Lambda function processes the review, computes average character and word length,  
and sends custom CloudWatch metrics for monitoring.

## ⚙️ Architecture
- **S3 Bucket** – stores incoming JSON review files  
- **Lambda (process-reviews)** – triggered manually or via EventBridge/S3; parses reviews and publishes metrics  
- **CloudWatch Logs & Metrics** –  
  - Namespace: `ReviewAnalyzer`  
  - Metrics: `ReviewCount`, `AvgCharLen`, `AvgWordLen`  
- **CloudWatch Alarm** – triggers SNS email if `AvgWordLen > 80`  
- **SNS Topic (review-analyzer-alerts)** – sends email notifications

## 📊 Observability
- Alarm tested successfully ✅ (SNS email received)  
- Dashboard: `CloudWatch → Dashboards → ReviewAnalyzer`  
  - Line: **AvgWordLen**  
  - Number: **ReviewCount**  
- Tested: **Oct 23, 2025**

## 🧰 Tools Used
- AWS Lambda (Python 3.12)  
- Amazon S3  
- Amazon CloudWatch (Metrics, Alarms, Dashboard)  
- AWS SNS  
- AWS CloudShell + GitHub

## 🚀 Next Steps
- Add a small Python simulator that uploads random reviews every few seconds  
- Include screenshots of the CloudWatch dashboard and alarm states
