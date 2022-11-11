import queue
import socket
from threading import Thread
import os
import time

def server(host = "127.0.0.1", port=65432):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
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
    q,
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
            if m % update_interval == 0 and m > 0:
                percentage = m / update_interval
                print(f"client: {'█'*int(percentage)}{'░'*int(messages/update_interval-percentage)} {m} / {messages} messages", end="\r")
            message = os.urandom(message_size)
            s.sendall(message)
            data = s.recv(message_size)
            if data != message:
                errors += 1

        time_difference = (time.time() - start_time)
        print(f"client: {'█'*int(messages/update_interval)} {messages} / {messages} messages")
        print(f"client: message size: {message_size}")
        print(f"client: duration: {time_difference:.2f} seconds")
        print(f"client: errors: {errors}")
        q.put({
			"errors": errors,
			"time": time_difference,
			"messages": messages,
			"message_size": message_size,
		})

def run_server_client(server_args = None, client_args = None):
    q = queue.Queue()
    server_thread = Thread(target=server, kwargs=server_args)
    client_thread = Thread(target=client, args=(q,), kwargs=client_args)
    server_thread.start()
    client_thread.start()
    server_thread.join()
    client_thread.join()
    print("done")
    return q.get()

if __name__ == "__main__":
    run_server_client()
