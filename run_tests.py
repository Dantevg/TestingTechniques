import os
import sys
import time
import server_client

def get_commands(device):
	test_commands = {
		"baseline": [],
		"delay": [f"sudo tc qdisc add dev {device} root netem delay 200ms"],
		"jittered delay": [f"sudo tc qdisc add dev {device} root netem delay 200ms 75ms"],
		"packet drops": [f"sudo tc qdisc add dev {device} root netem loss 20%"],
		"low throughput": [f"sudo tc qdisc add dev {device} root tbf rate 256kbit burst 16kbit latency 400ms"],
		"packet reordering": [f"sudo tc qdisc add dev {device} root netem delay 10ms reorder 25% 50%"],
		"packet duplication": [f"sudo tc qdisc add dev {device} root netem duplicate 5%"],
		"bitflips": [f"sudo tc qdisc add dev {device} root netem corrupt 10%"],
		"packet reordering & packet duplication": [f"sudo tc qdisc add dev {device} root netem delay 10ms reorder 25% 50% duplicate 5%"],
		# TODO: fix the second command, which now errors with "Error: Invalid qdisc name."
		"packet drops & low throughput": [f"sudo tc qdisc add dev {device} root netem loss 20%", f"sudo tc qdisc change dev {device} root tbf rate 256kbit burst 16kbit latency 400ms"],
		"packet duplication & bitflips": [f"sudo tc qdisc add dev {device} root netem duplicate 5% corrupt 10%"],
	}
	
	reset_command = f"sudo tc qdisc del dev {device} root"
	return (test_commands, reset_command)

def exec_command(command):
	print(f"test: running command '{command}'")
	return os.system(command)

def exec_commands(commands):
	return all([exec_command(c) == 0 for c in commands])

def run_test(desc, commands):
	(test_commands, reset_command) = commands
	print(f"\n===== test '{desc}'")
	if not exec_commands(test_commands[desc]):
		print("Failed to execute network tampering command")
		exec_command(reset_command)
		return
	if desc == "delay" or desc == "jittered delay":
		server_client.run_server_client(client_args={"messages": 10, "update_interval": 1})
	else:
		server_client.run_server_client()
	exec_command(reset_command)

def main():
	if len(sys.argv) != 2:
		print("Expecting network device as argument, probably 'lo' (find using 'ip address')")
		return
	
	(test_commands, reset_command) = get_commands(sys.argv[1])
	
	if os.geteuid() != 0:
		print("tc command needs root, run again with sudo")
		return
	
	try:
		exec_command(reset_command)
		for desc in test_commands:
			run_test(desc, (test_commands, reset_command))
			time.sleep(1)
	except KeyboardInterrupt:
		exec_command(reset_command)
		sys.exit(0)

if __name__ == "__main__":
	main()