import socket
from threading import Thread
import os
import time

def server(host = "127.0.0.1", port=65432):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen()
        conn, addr = s.accept()
        print(f"server: started on {host}:{port}")
        with conn:
            print(f"server: connected by {addr}")
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                conn.sendall(data)

def client(
    host = "127.0.0.1", 
    port=65432, 
    messages=100, 
    message_size=1024,
    update_interval=10):

    errors = 0
    start_time = time.time()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        print(f"client: connected to {host}:{port}")

        for m in range(messages):
            if m % update_interval == 0:
                print(f"client: {m} messages sent")
            message = os.urandom(message_size)
            s.sendall(message)
            data = s.recv(message_size)
            if data != message:
                errors += 1

        print(f"client: messages sent: {messages}")
        print(f"client: message size: {message_size}")
        time_difference = (time.time() - start_time)
        print(f"client: duration: {time_difference:.2f} seconds")
        print(f"client: errors: {errors}")

def run_server_client(server_args = None, client_args = None):
    server_thread = Thread(target=server, kwargs=server_args)
    client_thread = Thread(target=client, kwargs=client_args)
    server_thread.start()
    client_thread.start()
    server_thread.join()
    client_thread.join()
    print("done")

if __name__ == "__main__":
    run_server_client()