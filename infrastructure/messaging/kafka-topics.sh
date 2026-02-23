#!/bin/bash
# Create Kafka topics for DataPulse Analytics

KAFKA_BROKER=${KAFKA_BROKER:-"localhost:9092"}

echo "Creating Kafka topics..."

kafka-topics.sh --create --bootstrap-server $KAFKA_BROKER \
  --topic datapulse-events \
  --partitions 6 \
  --replication-factor 1 \
  --config retention.ms=604800000 \
  --config cleanup.policy=delete

kafka-topics.sh --create --bootstrap-server $KAFKA_BROKER \
  --topic datapulse-analytics \
  --partitions 3 \
  --replication-factor 1 \
  --config retention.ms=604800000

kafka-topics.sh --create --bootstrap-server $KAFKA_BROKER \
  --topic datapulse-alerts \
  --partitions 3 \
  --replication-factor 1 \
  --config retention.ms=2592000000

kafka-topics.sh --create --bootstrap-server $KAFKA_BROKER \
  --topic datapulse-dead-letter \
  --partitions 1 \
  --replication-factor 1 \
  --config retention.ms=-1

echo "Kafka topics created successfully."
kafka-topics.sh --list --bootstrap-server $KAFKA_BROKER
