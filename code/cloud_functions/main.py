import base64
import json
import functions_framework
from datetime import datetime
from google.cloud import storage

def archive_json_files(src_bucket, dest_bucket):

    gcs_client = storage.Client()
    src_bucket = gcs_client.bucket(src_bucket.replace("gs://",""))
    dest_bucket = gcs_client.bucket(dest_bucket.replace("gs://",""))
    input_files = [blob.name for blob in src_bucket.list_blobs() if blob.name.lower().endswith(".json")]
    
    for filename in input_files:
        src_blob = src_bucket.blob(filename)
        dest_filename = f"{filename.replace('.json','')}_{datetime.today().strftime('%Y-%m-%d_%H%M%S')}.json"
        dest_blob = src_bucket.copy_blob(src_blob, dest_bucket, dest_filename)
        src_blob.delete()
        
    # confirm no .json files remain unarchived
    input_bucket_files = [blob.name for blob in src_bucket.list_blobs() if blob.name.lower().endswith(".json")]
    if len(input_bucket_files) == 0:
        return
    else:
        raise Exception(f"Dataflow pipeline needs attention: \
        Cloud Storage Bucket {src_bucket} needs check, JSON data remained unarchived!")

# @notify_error - slack notifiactions decorator potentially, depends on team setup
# Triggered from a message on a Cloud Pub/Sub topic.
@functions_framework.cloud_event
def run(cloud_event):

    message = base64.b64decode(cloud_event.data["message"]["data"]).decode("utf-8")
    message = message.replace("'",'"')
    message = json.loads(message)
    
    if message["status"] == "SUCCESS":
        archive_json_files(src_bucket=message["src_bucket"], dest_bucket=message["dest_bucket"])
    else:
        raise Exception(f"Files not archived! Dataflow job returned status {message['status']}")



