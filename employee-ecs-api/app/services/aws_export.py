"""Upload JSON to S3 and notify SNS. Configure env vars for production."""

import json
from datetime import datetime, timezone

import boto3

from app.config import settings


def export_employees_json_to_s3_and_notify(
    employees_payload: list[dict],
) -> tuple[str | None, str | None]:
    """
    Writes JSON to s3://{bucket}/{prefix}employees-{timestamp}.json
    and publishes to SNS if ARNs are set. Returns (s3_uri, sns_message_id).
    """
    if not settings.s3_export_bucket:
        return None, None

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    key = f"{settings.s3_export_prefix}employees-{ts}.json"
    body = json.dumps(employees_payload, default=str, indent=2)

    client = boto3.client("s3", region_name=settings.aws_region)
    client.put_object(
        Bucket=settings.s3_export_bucket,
        Key=key,
        Body=body.encode("utf-8"),
        ContentType="application/json",
    )
    s3_uri = f"s3://{settings.s3_export_bucket}/{key}"

    sns_id = None
    if settings.sns_topic_arn:
        sns = boto3.client("sns", region_name=settings.aws_region)
        msg = json.dumps(
            {
                "message": "Employee export JSON is available in S3",
                "s3_uri": s3_uri,
                "bucket": settings.s3_export_bucket,
                "key": key,
            }
        )
        resp = sns.publish(
            TopicArn=settings.sns_topic_arn,
            Subject="Employee data export ready",
            Message=msg,
        )
        sns_id = resp.get("MessageId")

    return s3_uri, sns_id
