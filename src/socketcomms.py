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


def get_command(tamp1, args1, tamp2, args2):
    command = "sudo tc qdisc add dev lo root netem"
    if tamp1 == "Delay":
        command = f"{command} delay {args1[0]}ms"
    if tamp2 == "Delay":
        command = f"{command} delay {args2[0]}ms"
    if tamp1 == "JitteredDelay":
        command = f"{command} delay {args1[0]}ms {args1[1]}ms"
    if tamp2 == "JitteredDelay":
        command = f"{command} delay {args2[0]}ms {args2[1]}ms"
    if tamp1 == "Reordering":
        command = f"{command} delay 10ms reorder {args1[0]}% {args1[1]}%"
    if tamp2 == "Reordering":
        command = f"{command} delay 10ms reorder {args2[0]}% {args2[1]}%"
    if tamp1 == "PacketDrops":
        command = f"{command} loss {args1[0]}%"
    if tamp2 == "PacketDrops":
        command = f"{command} loss {args2[0]}%"
    if tamp1 == "Duplication":
        command = f"{command} duplicate {args1[0]}%"
    if tamp2 == "Duplication":
        command = f"{command} duplicate {args2[0]}%"
    if tamp1 == "Bitflips":
        command = f"{command} corrupt {args1[0]}%"
    if tamp2 == "Bitflips":
        command = f"{command} corrupt {args2[0]}%"
    if tamp1 == "LowThroughput":
        command = f"{command} rate {args1[0]}kbit burst {args1[1]}kbit latency {args1[2]}ms"
    if tamp2 == "LowThroughput":
        command = f"{command} rate {args2[0]}kbit burst {args2[1]}kbit latency {args2[2]}ms"
    return command


def parse_tampering(tamp):
    tamp_spl = tamp.split('(')
    args_ind = list(find_all(tamp_spl[1], ','))
    if not args_ind:
        args = [int(tamp_spl[1][:-1])]
    else:
        args = [int(tamp_spl[1][:args_ind[0]])]
        for i in range(len(args_ind)):
            if i+1 == len(args_ind):
                args.append(int(tamp_spl[1][args_ind[i]+1:-1]))
            else:
                args.append(int(tamp_spl[1][args_ind[i]+1:args_ind[i+1]]))
    return (tamp_spl[0], args)

def process_input(data):
    tamp_ind = data.find("))")+1
    tamp_input = data[37:tamp_ind]
    sep = tamp_input.find(')')
    tamp1 = tamp_input[:sep+1]
    tamp2 = tamp_input[sep+2:]
    tamp1_parsed = parse_tampering(tamp1)
    tamp2_parsed = parse_tampering(tamp2)
    packet_ind1 = list(find_all(data, '(\"'))
    packet_ind2 = list(find_all(data, '\",Packet'))
    packet_data_list = []
    for i in range(len(packet_ind1)):
        packet_data = data[packet_ind1[i]+2:packet_ind2[i]]
        packet_data_list.append(packet_data)
    return tamp1_parsed, tamp2_parsed, packet_data_list

def send_packages(tampering_cmd, packet_data):
    # TODO
    return packet_data

def build_return_string(data):
    return_string = "Packet_nil"
    for x in reversed(data):
        return_string = f"Packet_cons(\"{x}\",{return_string})"
    return return_string + "\n"


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
                (tamp1, args1), (tamp2, args2), packet_data = process_input(data)
                tampering_cmd = get_command(tamp1, args1, tamp2, args2)
                return_data = send_packages(tampering_cmd, packet_data)
                return_string = build_return_string(return_data)
                conn.send(return_string.encode())


if __name__ == "__main__":
    main()
