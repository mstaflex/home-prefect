import boto3
from botocore.client import Config

MINIO_ENDPOINT = "http://10.15.22.10:9000"  # Change to your MinIO URL
ACCESS_KEY = "9bdVvyi7FrqY7pgk8Xmx"
SECRET_KEY = "RU1qBWL1PRZ7DBnI5p8AI0RKwShilSeUAqYKpKGU"
BUCKET_NAME = "palantir"

s3 = boto3.client(
    "s3",
    endpoint_url=MINIO_ENDPOINT,
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
    config=Config(signature_version="s3v4"),
    region_name="us-east-1",  # MinIO ignores this but boto3 requires it
)

# Check bucket exists and list objects
try:
    response = s3.list_objects_v2(Bucket=BUCKET_NAME)
    count = response.get("KeyCount", 0)
    print(f"✅ Connected. Objects in '{BUCKET_NAME}': {count}")

    if count > 0:
        for obj in response.get("Contents", []):
            print(f"  - {obj['Key']} ({obj['Size']} bytes)")
    else:
        print("⚠️  Bucket is empty or prefix returned no results.")

    # Check if truncated (more than 1000 objects)
    if response.get("IsTruncated"):
        print("⚠️  Results truncated — bucket has 1000+ objects.")

except s3.exceptions.NoSuchBucket:
    print(f"❌ Bucket '{BUCKET_NAME}' does not exist.")
except Exception as e:
    print(f"❌ Error: {e}")
