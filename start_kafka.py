import subprocess
import os
import signal
import sys
import time

kafka_dir = "/Users/coulson/j2kexp/kafka_2.13-3.6.1"
zookeeper_start_script = f"{kafka_dir}/bin/zookeeper-server-start.sh"
kafka_start_script = f"{kafka_dir}/bin/kafka-server-start.sh"
kafka_topic_script = f"{kafka_dir}/bin/kafka-topics.sh"

def change_dir(func):
    def wrapper(*args, **kwargs):
        os.chdir(kafka_dir)  # Change working directory to Kafka directory
        return func(*args, **kwargs)
    return wrapper

@change_dir
def start_zookeeper():
    print("Starting Zookeeper...")
    return subprocess.Popen(["bin/zookeeper-server-start.sh", "config/zookeeper.properties"], cwd=kafka_dir)

@change_dir
def start_kafka():
    print("Starting Kafka...")
    return subprocess.Popen(["bin/kafka-server-start.sh", "config/server.properties"], cwd=kafka_dir)

@change_dir
def create_kafka_topic():
    print("Creating Kafka topic...")
    subprocess.run(["bin/kafka-topics.sh", "--create", "--topic", "quickstart-events", "--bootstrap-server", "localhost:9092"])

# Signal handler for graceful shutdown
def signal_handler(sig, frame):
    print('Interrupt received, shutting down...')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# Check if Kafka directory exists
# if not os.path.isdir(kafka_dir):  # Adjusted to account for "./" in kafka_dir
#     print(f"Directory {kafka_dir} does not exist in the current working directory. Aborting.")
#     sys.exit(1)

processes = []

try:
    # Start Zookeeper and Kafka
    zookeeper_proc = start_zookeeper()
    processes.append(zookeeper_proc)
    time.sleep(10)  # Wait for Zookeeper to start

    kafka_proc = start_kafka()
    processes.append(kafka_proc)
    time.sleep(10)  # Wait for Kafka to start

    # Create Kafka Topic
    create_kafka_topic()

    print("Servers are running. Press Control-C to terminate.")
    while True:
        time.sleep(10)
except Exception as e:
    print(f"An error occurred: {e}")
    sys.exit(1)
finally:
    for proc in processes:
        proc.terminate()
