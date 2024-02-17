from confluent_kafka import Consumer, KafkaError

# Configure the consumer
c = Consumer({
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'my-group',
    'auto.offset.reset': 'earliest'
})

c.subscribe(['my-topic'])

try:
    while True:
        msg = c.poll(timeout=1.0)  # Adjust poll timeout as needed
        if msg is None:
            continue
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                # End of partition event
                print(f'{msg.topic()} [{msg.partition()}] reached end at offset {msg.offset()}')
            elif msg.error():
                raise KafkaException(msg.error())
        else:
            # Message is a normal message
            print(f'Message: {msg.value().decode("utf-8")}')
finally:
    # Clean up on exit
    c.close()
