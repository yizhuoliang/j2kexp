import os
import requests
import shutil
from subprocess import call

# Kafka download URL and filenames
kafka_tgz_url = 'https://downloads.apache.org/kafka/3.6.1/kafka_2.13-3.6.1.tgz'
kafka_tgz_filename = kafka_tgz_url.split('/')[-1]  # Extracts 'kafka_2.13-3.6.1.tgz'
kafka_dir_name = kafka_tgz_filename.rsplit('.', 2)[0]  # Extracts 'kafka_2.13-3.6.1'

def download_file(url, filename):
    """Download a file from a URL to a given filename"""
    response = requests.get(url, stream=True)
    with open(filename, 'wb') as file:
        shutil.copyfileobj(response.raw, file)
    return filename

def delete_if_exists(path):
    """Delete file or directory if it exists"""
    if os.path.isdir(path):
        shutil.rmtree(path)
    elif os.path.isfile(path):
        os.remove(path)

def main():
    # Step 1: Delete existing files/directories
    delete_if_exists(kafka_dir_name)
    delete_if_exists(kafka_tgz_filename)

    # Step 2: Download Kafka binary
    print(f"Downloading Kafka from {kafka_tgz_url}...")
    download_file(kafka_tgz_url, kafka_tgz_filename)
    print("Download completed.")

    # Step 3: Extract the downloaded tarball
    print("Extracting Kafka...")
    call(['tar', '-xzf', kafka_tgz_filename])
    print("Extraction completed.")

if __name__ == "__main__":
    main()
