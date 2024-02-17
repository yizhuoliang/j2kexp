import socket

def start_pinger():
    # Define host and port to connect to (same as the ponger)
    host = '127.0.0.1'
    port = 65432

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        s.sendall(b'Ping!')
        print("Message sent: Ping!")

if __name__ == "__main__":
    start_pinger()
