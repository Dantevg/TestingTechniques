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

def get_command(tamp, args):
    args_len = len(args)
    if args_len == 1:
        if tamp == "Delay":
            return f"sudo tc qdisc add dev lo root netem delay {args[0]}ms"
        elif tamp == "PacketDrops":
            return f"sudo tc qdisc add dev lo root netem loss {args[0]}%"
        elif tamp == "Duplication":
            return f"sudo tc qdisc add dev lo root netem duplicate {args[0]}%"
        else:
            return f"sudo tc qdisc add dev lo root netem corrupt {args[0]}%"
    elif args_len == 2:
        if tamp == "JitteredDelay":
            return f"sudo tc qdisc add dev lo root netem delay {args[0]}ms {args[1]}ms"
        else:
            return f"sudo tc qdisc add dev lo root netem delay 10ms reorder {args[0]}% {args[1]}%"
    else:
        return f"sudo tc qdisc add dev lo root tbf rate {args[0]}kbit burst {args[1]}kbit latency {args[2]}ms"


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
                tampering_cmd = get_command(tamp1, args1)



if __name__ == "__main__":
    main()
