import socket

def start_ponger():
    # Define host and port for the ponger to listen on
    host = '127.0.0.1'
    port = 65432  # Port to listen on (non-privileged ports are > 1023)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen()
        print("Ponger listening on", host, port)
        conn, addr = s.accept()
        with conn:
            print('Connected by', addr)
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                print(f'Received message: {data.decode()}')
                # Close the connection after receiving the message
                break  # Exit the loop after processing the message

            # It's a good practice to close the connection outside the loop after all processing is done
            conn.close()

start_ponger()
