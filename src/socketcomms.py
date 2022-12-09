import sys
import socket

# krijgt een packetlijst en een lijst van tamperings en moet als output de packetlijst van torxakis teruggeven.

def main():
    if len(sys.argv) != 2:
        print("Port number required")
        return
    host = socket.gethostname()
    portnr = int(sys.argv[1])

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, portnr))
        print("waiting for Tester")
        s.listen()
        conn, address = s.accept()
        print("Tester connected")
        with conn:
            while True:
                data = conn.recv(1024).decode()
                print(data)



if __name__ == "__main__":
    main()
