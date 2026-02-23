import json
import os
import logging
import boto3
from datetime import datetime

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3_client = boto3.client("s3")
dynamodb = boto3.resource("dynamodb")
S3_BUCKET = os.environ.get("S3_BUCKET", "datapulse-storage")
TABLE_NAME = os.environ.get("DYNAMODB_TABLE", "datapulse-event-summaries")


def lambda_handler(event, context):
    """
    AWS Lambda function triggered by Kafka/SQS events.
    Processes analytics events, generates summaries, and stores in S3/DynamoDB.
    """
    logger.info(f"Received {len(event.get('Records', []))} records")

    processed = 0
    errors = 0

    for record in event.get("Records", []):
        try:
            body = json.loads(record.get("body", "{}"))
            event_type = body.get("event_type", "unknown")
            payload = body.get("payload", {})
            timestamp = body.get("timestamp", datetime.utcnow().isoformat())

            # Process event
            enriched = _enrich_event(body)

            # Store processed event in S3
            s3_key = f"processed/{datetime.utcnow().strftime('%Y/%m/%d')}/{event_type}/{context.aws_request_id}.json"
            s3_client.put_object(
                Bucket=S3_BUCKET,
                Key=s3_key,
                Body=json.dumps(enriched),
                ContentType="application/json",
            )

            # Update summary in DynamoDB
            _update_summary(event_type, payload)

            processed += 1
            logger.info(f"Processed event: {event_type}")

        except Exception as e:
            errors += 1
            logger.error(f"Error processing record: {e}")

    result = {
        "statusCode": 200,
        "body": json.dumps({
            "processed": processed,
            "errors": errors,
            "request_id": context.aws_request_id,
        }),
    }

    logger.info(f"Lambda complete: {processed} processed, {errors} errors")
    return result


def _enrich_event(event_data):
    enriched = event_data.copy()
    enriched["processed_at"] = datetime.utcnow().isoformat()
    enriched["lambda_processed"] = True

    payload = event_data.get("payload", {})
    if "value" in payload:
        try:
            value = float(payload["value"])
            enriched["payload"]["value_category"] = (
                "high" if value > 100 else "medium" if value > 50 else "low"
            )
        except (ValueError, TypeError):
            pass

    return enriched


def _update_summary(event_type, payload):
    try:
        table = dynamodb.Table(TABLE_NAME)
        today = datetime.utcnow().strftime("%Y-%m-%d")

        table.update_item(
            Key={"event_type": event_type, "date": today},
            UpdateExpression="SET event_count = if_not_exists(event_count, :zero) + :inc, last_updated = :ts",
            ExpressionAttributeValues={
                ":inc": 1,
                ":zero": 0,
                ":ts": datetime.utcnow().isoformat(),
            },
        )
    except Exception as e:
        logger.error(f"DynamoDB update failed: {e}")
