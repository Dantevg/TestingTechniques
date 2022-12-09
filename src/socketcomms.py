import sys
import socket

def main():
    if len(sys.argv) != 1:
        print("Port number required")
        return
    host = socket.gethostname()
    portnr = sys.argv[0]

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, portnr))
        print("waiting for Tester")
        s.listen()
        conn, address = s.accept()
        with conn:
            while True:
                data = conn.recv(1024)


if __name__ == "__main__":
    main()
