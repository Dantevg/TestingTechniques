import sys
import socket

# krijgt een packetlijst en een lijst van tamperings en moet als output de packetlijst van torxakis teruggeven.

def find_all(i_str, substr):
    start = 0
    while True:
        start = i_str.find(substr, start)
        if start == -1: return
        yield start
        start += len(substr)

def process_input(data):
    tamp_ind = data.find("))")+1
    tamp_input = data[37:tamp_ind]
    sep = tamp_input.find(')')
    tamp1 = tamp_input[:sep+1]
    tamp2 = tamp_input[sep+2:]
    packet_ind1 = list(find_all(data, '(\"'))
    packet_ind2 = list(find_all(data, '\",Packet'))
    packet_data_list = []
    for i in range(len(packet_ind1)):
        packet_data = data[packet_ind1[i]+2:packet_ind2[i]]
        packet_data_list.append(packet_data)
    return tamp1, tamp2, packet_data_list

def main():
    if len(sys.argv) != 2:
        print("Port number required")
        return
    portnr = int(sys.argv[1])

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("localhost", portnr))
        print("waiting for Tester")
        s.listen()
        conn, address = s.accept()
        print("Tester connected")
        with conn:
            while True:
                data = conn.recv(1024).decode()
                tamp1, tamp2, packet_data = process_input(data)
                



if __name__ == "__main__":
    main()
