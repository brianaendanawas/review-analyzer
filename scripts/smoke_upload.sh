#!/usr/bin/env bash
set -euo pipefail
BUCKET="review-analyzer-briana-4nk3j3"   # << replace if your bucket differs
cat > sample.json <<'J'
[
  {"reviewId": "1", "text": "Quick smoke test upload."}
]
J
aws s3 cp sample.json s3://$BUCKET/incoming/sample-$(date +%s).json
echo "Uploaded to s3://$BUCKET/incoming/"
