from confluent_kafka import Producer
import json


def delivery_report(err, msg):
    if err is not None:
        print('Message delivery failed: {}'.format(err))
    else:
        print('Message delivered to {} [{}]'.format(msg.topic(), msg.partition()))


def create_producer():
    conf = {'bootstrap.servers': "my-django-release-kafka:9092"}
    producer = Producer(conf)
    return producer


def send_to_kafka(topic, data):
    producer = create_producer()
    producer.produce(topic, json.dumps(data).encode('utf-8'), callback=delivery_report)
    producer.poll(0)
    producer.flush()
