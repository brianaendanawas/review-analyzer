import argparse, json, time, random, string, sys
import boto3

def random_review(short=False, long=False):
    short_pool = [
        "Great sound and comfy.", "Battery lasts all day.",
        "Works fine for Zoom calls.", "Solid build quality."
    ]
    normal_pool = [
        "These headphones sound great and are comfortable to wear for hours.",
        "The microphone is acceptable but could be clearer in noisy rooms.",
        "Setup was easy and Bluetooth connection is stable across my apartment.",
        "Bass is strong without drowning the mids; treble is not harsh."
    ]
    if short:
        return random.choice(short_pool)
    if long:
        big = "supercalifragilisticexpialidocioussupercalifragilisticexpialidocious"
        return " ".join([big] * random.randint(40, 120))
    words = " ".join(random.choice(random.choice(normal_pool).split()) for _ in range(random.randint(15,35)))
    return words

def put_json(s3, bucket, key, payload):
    s3.put_object(Bucket=bucket, Key=key, Body=json.dumps(payload).encode("utf-8"))

def run_batch(s3, bucket, prefix, count, spike_every):
    for i in range(1, count+1):
        is_spike = (spike_every and i % spike_every == 0)
        review = random_review(long=is_spike)
        key = f"{prefix.rstrip('/')}/sim-{int(time.time())}-{i}.json"
        put_json(s3, bucket, key, {"review": review})
        print(("SPIKE  " if is_spike else "normal ") + key)
    print(f"Uploaded {count} objects.")

def run_stream(s3, bucket, prefix, rate, spike_every):
    i = 0
    try:
        while True:
            i += 1
            is_spike = (spike_every and i % spike_every == 0)
            review = random_review(long=is_spike)
            key = f"{prefix.rstrip('/')}/stream-{int(time.time())}-{i}.json"
            put_json(s3, bucket, key, {"review": review})
            print(("SPIKE  " if is_spike else "normal ") + key)
            time.sleep(rate)
    except KeyboardInterrupt:
        print("\nStopped.")

if __name__ == "__main__":
    p = argparse.ArgumentParser(description="S3 review uploader")
    p.add_argument("--bucket", required=True)
    p.add_argument("--prefix", default="incoming/")
    mode = p.add_mutually_exclusive_group()
    mode.add_argument("--batch", type=int, help="upload N reviews and exit")
    mode.add_argument("--stream", type=int, help="upload forever every N seconds")
    p.add_argument("--spike-every", type=int, default=0, help="every Nth item is a long-word spike (0=never)")
    args = p.parse_args()

    s3 = boto3.client("s3")
    if args.batch:
        run_batch(s3, args.bucket, args.prefix, args.batch, args.spike_every)
    else:
        rate = args.stream or 5
        run_stream(s3, args.bucket, args.prefix, rate, args.spike_every)
