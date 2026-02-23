import logging
import io
from django.conf import settings

logger = logging.getLogger("analytics")


def get_s3_client():
    try:
        import boto3
        client = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION,
        )
        return client
    except Exception as e:
        logger.warning(f"S3 client unavailable: {e}")
        return None


def upload_report(report_id, content, file_format="pdf"):
    s3 = get_s3_client()
    if not s3:
        logger.warning("S3 unavailable, skipping report upload")
        return None

    try:
        key = f"reports/{report_id}.{file_format}"
        content_type_map = {
            "pdf": "application/pdf",
            "csv": "text/csv",
            "json": "application/json",
        }

        if isinstance(content, str):
            content = content.encode("utf-8")

        s3.put_object(
            Bucket=settings.AWS_S3_BUCKET,
            Key=key,
            Body=content,
            ContentType=content_type_map.get(file_format, "application/octet-stream"),
            ServerSideEncryption="AES256",
        )

        url = f"https://{settings.AWS_S3_BUCKET}.s3.{settings.AWS_REGION}.amazonaws.com/{key}"
        logger.info(f"Report {report_id} uploaded to S3: {url}")
        return url
    except Exception as e:
        logger.error(f"Failed to upload report {report_id} to S3: {e}")
        return None


def upload_data_export(export_id, data_bytes, filename):
    s3 = get_s3_client()
    if not s3:
        return None

    try:
        key = f"exports/{export_id}/{filename}"
        s3.put_object(
            Bucket=settings.AWS_S3_BUCKET,
            Key=key,
            Body=data_bytes,
            ServerSideEncryption="AES256",
        )

        url = s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": settings.AWS_S3_BUCKET, "Key": key},
            ExpiresIn=3600,
        )
        logger.info(f"Data export uploaded: {key}")
        return url
    except Exception as e:
        logger.error(f"Failed to upload data export: {e}")
        return None


def list_reports(prefix="reports/"):
    s3 = get_s3_client()
    if not s3:
        return []

    try:
        response = s3.list_objects_v2(
            Bucket=settings.AWS_S3_BUCKET,
            Prefix=prefix,
        )
        return [
            {
                "key": obj["Key"],
                "size": obj["Size"],
                "last_modified": obj["LastModified"].isoformat(),
            }
            for obj in response.get("Contents", [])
        ]
    except Exception as e:
        logger.error(f"Failed to list reports from S3: {e}")
        return []
