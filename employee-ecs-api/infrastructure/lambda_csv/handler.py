"""
Lambda subscribed to SNS: reads JSON export path from message, loads JSON from S3,
writes CSV to another prefix. Wire this in AWS Console or Terraform (not run locally).

Expected SNS message body (JSON string) from the API publish step includes:
  s3_uri, bucket, key

Output: s3://{bucket}/exports/csv/{basename}.csv
"""

import csv
import io
import json
import os
import urllib.parse

import boto3

s3 = boto3.client("s3")
OUT_PREFIX = os.environ.get("CSV_PREFIX", "exports/csv/")


def _parse_sns_record(record: dict) -> dict:
    body = record.get("Sns", {}).get("Message", "{}")
    if isinstance(body, str):
        try:
            return json.loads(body)
        except json.JSONDecodeError:
            return {}
    return {}


def handler(event, context):
    for record in event.get("Records", []):
        if record.get("EventSource") or record.get("eventSource") == "aws:sns":
            msg = _parse_sns_record(record)
        else:
            msg = record if isinstance(record, dict) else {}

        bucket = msg.get("bucket")
        key = msg.get("key")
        if not bucket or not key:
            continue

        obj = s3.get_object(Bucket=bucket, Key=key)
        raw = obj["Body"].read().decode("utf-8")
        data = json.loads(raw)
        if not isinstance(data, list):
            data = [data]

        buf = io.StringIO()
        if data:
            w = csv.DictWriter(buf, fieldnames=list(data[0].keys()))
            w.writeheader()
            for row in data:
                w.writerow({k: row.get(k) for k in data[0].keys()})
        csv_body = buf.getvalue()

        base = key.rsplit("/", 1)[-1].replace(".json", "")
        out_key = f"{OUT_PREFIX}{base}.csv"
        s3.put_object(
            Bucket=bucket,
            Key=out_key,
            Body=csv_body.encode("utf-8"),
            ContentType="text/csv",
        )

    return {"statusCode": 200, "body": json.dumps({"ok": True})}
