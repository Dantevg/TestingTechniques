import queue
import socket
from threading import Thread

def server(host = "127.0.0.1", port=8002):
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
    port=8002, 
    messages = []):

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        print(f"client: connected to {host}:{port}")

        for m in range(len(messages)):
            percentage = m / len(messages) * 10
            print(f"client: ┃{'█'*int(percentage)}{' '*int(10-percentage)}┃ {m} / {len(messages)} messages", end="\r")
            s.sendall(messages[m].encode())
            data = s.recv(1024).decode()
            q.put(data)

def run_server_client(server_args = None, client_args = None):
    q = queue.Queue()
    server_thread = Thread(target=server, kwargs=server_args)
    client_thread = Thread(target=client, args=(q,), kwargs=client_args)
    server_thread.start()
    client_thread.start()
    server_thread.join()
    client_thread.join()
    return q

if __name__ == "__main__":
    run_server_client()