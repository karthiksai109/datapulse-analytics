import logging
from celery import shared_task
from django.utils import timezone

logger = logging.getLogger("analytics")


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def process_analytics_event(self, event_id):
    from .models import AnalyticsEvent, Alert
    from .services.elasticsearch_service import index_event
    from .services.mongodb_service import store_raw_event
    from .services.kafka_producer import publish_alert_trigger

    try:
        event = AnalyticsEvent.objects.get(id=event_id)

        # Index in Elasticsearch for search
        index_event(event)

        # Store raw data in MongoDB
        raw_data = {
            "event_id": str(event.id),
            "event_type": event.event_type,
            "payload": event.payload,
            "metadata": event.metadata,
            "timestamp": event.timestamp,
            "source_id": str(event.source_id) if event.source else None,
        }
        store_raw_event(raw_data)

        # Check alert conditions
        active_alerts = Alert.objects.filter(is_active=True)
        for alert in active_alerts:
            if _check_alert_condition(alert, event):
                alert.last_triggered = timezone.now()
                alert.trigger_count += 1
                alert.save(update_fields=["last_triggered", "trigger_count"])
                publish_alert_trigger(alert, event)
                logger.info(f"Alert {alert.id} triggered by event {event.id}")

        event.processed = True
        event.save(update_fields=["processed"])
        logger.info(f"Event {event_id} processed successfully")

    except AnalyticsEvent.DoesNotExist:
        logger.error(f"Event {event_id} not found")
    except Exception as e:
        logger.error(f"Failed to process event {event_id}: {e}")
        self.retry(exc=e)


def _check_alert_condition(alert, event):
    config = alert.condition_config
    if not config:
        return False

    event_type_match = config.get("event_type")
    if event_type_match and event.event_type != event_type_match:
        return False

    threshold = config.get("threshold")
    field = config.get("field", "value")
    operator = config.get("operator", "gt")

    value = event.payload.get(field)
    if value is None or threshold is None:
        return False

    try:
        value = float(value)
        threshold = float(threshold)
    except (ValueError, TypeError):
        return False

    operators = {
        "gt": lambda v, t: v > t,
        "gte": lambda v, t: v >= t,
        "lt": lambda v, t: v < t,
        "lte": lambda v, t: v <= t,
        "eq": lambda v, t: v == t,
    }

    check_fn = operators.get(operator)
    if check_fn:
        return check_fn(value, threshold)
    return False


@shared_task(bind=True, max_retries=2, default_retry_delay=120)
def generate_report_task(self, report_id):
    from .models import Report
    from .services.s3_service import upload_report

    try:
        report = Report.objects.select_related("dashboard").get(id=report_id)
        dashboard = report.dashboard

        # Gather dashboard data
        from .models import AnalyticsEvent
        events = AnalyticsEvent.objects.filter(
            source__in=dashboard.data_sources.all()
        ).order_by("-timestamp")[:1000]

        # Generate report content based on format
        if report.format == "csv":
            content = _generate_csv_report(events)
        elif report.format == "json":
            content = _generate_json_report(events)
        else:
            content = _generate_pdf_report(events, dashboard)

        # Upload to S3
        file_url = upload_report(str(report.id), content, report.format)
        if file_url:
            report.file_url = file_url

        # Generate AI summary placeholder
        report.ai_summary = _generate_ai_summary(events, dashboard)
        report.save(update_fields=["file_url", "ai_summary"])

        logger.info(f"Report {report_id} generated successfully")

    except Report.DoesNotExist:
        logger.error(f"Report {report_id} not found")
    except Exception as e:
        logger.error(f"Failed to generate report {report_id}: {e}")
        self.retry(exc=e)


def _generate_csv_report(events):
    import csv
    import io

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Event ID", "Type", "Timestamp", "Payload"])
    for event in events:
        writer.writerow([str(event.id), event.event_type, event.timestamp, str(event.payload)])
    return output.getvalue()


def _generate_json_report(events):
    import json
    data = [
        {
            "event_id": str(e.id),
            "event_type": e.event_type,
            "timestamp": e.timestamp.isoformat(),
            "payload": e.payload,
        }
        for e in events
    ]
    return json.dumps(data, indent=2)


def _generate_pdf_report(events, dashboard):
    # Simplified PDF content generation
    content = f"DataPulse Analytics Report\nDashboard: {dashboard.title}\n"
    content += f"Total Events: {events.count()}\n"
    content += f"Generated at: {timezone.now().isoformat()}\n"
    return content.encode("utf-8")


def _generate_ai_summary(events, dashboard):
    event_count = events.count() if hasattr(events, 'count') else len(events)
    return (
        f"Dashboard '{dashboard.title}' analysis: {event_count} events processed. "
        f"Data collected from {dashboard.data_sources.count()} active sources. "
        f"Report generated automatically by DataPulse Analytics engine."
    )


@shared_task
def cleanup_old_events(days=90):
    from .models import AnalyticsEvent
    cutoff = timezone.now() - timezone.timedelta(days=days)
    deleted_count, _ = AnalyticsEvent.objects.filter(
        timestamp__lt=cutoff, processed=True
    ).delete()
    logger.info(f"Cleaned up {deleted_count} events older than {days} days")
