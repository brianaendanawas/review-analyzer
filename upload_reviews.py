# upload_reviews.py
import boto3
import pathlib
import sys

def main():
    if len(sys.argv) != 3:
        print("Usage: python upload_reviews.py <bucket> <local_json_path>")
        sys.exit(1)

    bucket = sys.argv[1]
    src = pathlib.Path(sys.argv[2]).expanduser().resolve()
    if not src.exists():
        print(f"File not found: {src}")
        sys.exit(1)

    s3 = boto3.client("s3")
    key = "incoming/sample_reviews.json"
    s3.upload_file(str(src), bucket, key)
    print(f"Uploaded {src.name} to s3://{bucket}/{key}")

if __name__ == "__main__":
    main()

