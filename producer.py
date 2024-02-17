from confluent_kafka import Producer
import json

def delivery_report(err, msg):
    """ Called once for each message produced to indicate delivery result.
        Triggered by poll() or flush(). """
    if err is not None:
        print(f'Message delivery failed: {err}')
    else:
        print(f'Message delivered to {msg.topic()} [{msg.partition()}]')

# Configure the producer
p = Producer({'bootstrap.servers': 'localhost:9092'})

topic = 'my-topic'

for i in range(10):
    data = {'number': i}
    # Trigger any available delivery report callbacks from previous produce() calls
    p.poll(0)

    # Asynchronously produce a message, the delivery report callback will be triggered from poll() above, or flush() below, when the message has been successfully delivered or failed permanently.
    p.produce(topic, json.dumps(data).encode('utf-8'), callback=delivery_report)

# Wait for any outstanding messages to be delivered and delivery report callbacks to be triggered.
p.flush()
