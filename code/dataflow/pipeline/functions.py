import json
import time
from datetime import datetime    
from functools import reduce
from google.cloud import bigquery, storage, pubsub_v1

def get_data(data, columns):
    columns = columns.split(".")
    value = reduce(lambda row, column: row.get(column) if row else None, columns, data)
    if value is None and "fields" in data:
        value = reduce(lambda row, column: row.get(column) if row else None, columns, data["fields"])
    return value
    
def parse_data(line):

    mapping = {
        "expand": "expand",
        "id": "id",
        "self": "self",
        "project_name": "project.name",
        "issue_type_name": "issuetype.name",
        "resolution_name": "resolution.name",
        "created_date": "created",
        "resolved_date": "resolutiondate",
        "severity": "customfield_11169.value",
        "team": "customfield_11067.value",
        "global_release": "customfield_11089.value",
        "story_points": "customfield_10026",
        "priority": "priority.name",
        "bug_type": "customfield_11191.value",
        "summary": "summary",
        "testing_scope": "customfield_11137",
        "engineering_area": "customfield_11130.value",
        "automation_test_name": "customfield_11132",
        "status": "status.name",
        "reporter": "reporter.displayName",
        "assignee_name": "assignee.displayName",
        "total_acv": "customfield_10948",
        "program": "customfield_11087.value",
        "execution_comments": "customfield_11104",
        "display_in_big_picture": "customfield_11079.value",
        "updated": "updated",
        "engineering_feedback": "customfield_11099.value",
        "proposed_text_for_limitation_or_resolved_issue": "customfield_11118",
        "customer_request_type": "customfield_10002.requestType.name",
        "project_type": "project.projectTypeKey",
        "channel": "creator.displayName"
    }
    
    record = json.loads(line)
    row = {
        key: get_data(record,src_column) for key, src_column in mapping.items()
    }
    row["date"] = datetime.today().strftime('%Y-%m-%d')
    row["project"] = record.get("key").split("-")[0]
    if "id" in row:
        row["id"] = int(record["id"])

    return row

def get_table_schema(table):
    client = bigquery.Client()
    table = client.get_table(table)
    schema_fields = [{'name': field.name, 'type': field.field_type, 'mode': field.mode} for field in table.schema]
    return {'fields': schema_fields}

def confirm_data_upload(bq_result):
    allowed_retries = 10
    retries = 0

    client = bigquery.Client()
    job_id = bq_result[1].jobId

    while retries <= allowed_retries:
        job = client.get_job(job_id)
        print(f"BIGQUERY JOB STATE: {job.state}")
        if job.state == "DONE" and job.error_result is None:
            return f"SUCCESS"
        
        retries += 1
        time.sleep(30)
    
    return str(job.state)
        
def create_archive_pubsub_message(job_status, src_bucket, dest_bucket):
    return {
        "status": job_status,
        "request": "archive_data",
        "src_bucket": src_bucket,
        "dest_bucket": dest_bucket
    }
    
def notify_pubsub(message, topic):
    publisher = pubsub_v1.PublisherClient()
    message = str(message).encode("utf-8")
    publisher.publish(topic, message)
    print(f"Message {message} published to topic {topic}!")