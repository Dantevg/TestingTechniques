import random

def is_slow(test_name):
	return ("delay" in test_name) or ("packet drops" in test_name)

def get_commands(device):
	delay = random.randint(50, 300)
	delay_lower = int(random.uniform(0.2, 0.8) * delay)
	percentage_mid = random.randint(35, 65)
	percentage_low = random.randint(5, 30)
	throughput = random.randint(1, 10) * 128
	packet_duplication_bitflips = int(random.uniform(1, 2) * percentage_low)
	test_commands = {
		"baseline": "",
		
		# Normal tests, taken from exercise 1
		"delay":
			f"sudo tc qdisc add dev {device} root netem delay 200ms",
		"jittered delay":
			f"sudo tc qdisc add dev {device} root netem delay 200ms 75ms",
		"packet drops":
			f"sudo tc qdisc add dev {device} root netem loss 20%",
		"low throughput":
			f"sudo tc qdisc add dev {device} root tbf rate 256kbit burst 16kbit latency 400ms",
		"packet reordering":
			f"sudo tc qdisc add dev {device} root netem delay 10ms reorder 25% 50%",
		"packet duplication":
			f"sudo tc qdisc add dev {device} root netem duplicate 5%",
		"bitflips":
			f"sudo tc qdisc add dev {device} root netem corrupt 10%",
		"jittered delay & low throughput":
			f"sudo tc qdisc add dev {device} root netem delay 200ms 75ms rate 256kbit latency 400ms",
		"packet reordering & packet duplication":
			f"sudo tc qdisc add dev {device} root netem delay 10ms reorder 25% 50% duplicate 5%",
		"packet drops & low throughput":
			f"sudo tc qdisc add dev {device} root netem loss 10% rate 1mbit latency 200ms",
		"packet duplication & bitflips":
			f"sudo tc qdisc add dev {device} root netem duplicate 5% corrupt 10%",
		
		# Random tests
		f"random delay ({delay}ms)":
			f"sudo tc qdisc add dev {device} root netem delay {delay}ms",
		f"random jittered delay ({delay}ms {delay_lower}ms)":
			f"sudo tc qdisc add dev {device} root netem delay {delay}ms {delay_lower}ms",
		f"random packet drops ({percentage_low}%)":
			f"sudo tc qdisc add dev {device} root netem loss {percentage_low}%",
		f"random low throughput ({throughput}kbps {delay}ms)":
			f"sudo tc qdisc add dev {device} root tbf rate {throughput}kbit burst 16kbit latency {delay}ms",
		f"random packet reordering ({percentage_low}% {percentage_mid}%)":
			f"sudo tc qdisc add dev {device} root netem delay 10ms reorder {percentage_low}% {percentage_mid}%",
		f"random packet duplication ({percentage_low}%)":
			f"sudo tc qdisc add dev {device} root netem duplicate {percentage_low}%",
		f"random bitflips ({percentage_low}%)":
			f"sudo tc qdisc add dev {device} root netem corrupt {percentage_low}%",
		f"random jittered delay ({delay}ms {delay_lower}ms) & low throughput ({throughput}kbps {2*delay}ms)":
			f"sudo tc qdisc add dev {device} root netem delay {delay}ms {delay_lower}ms rate {throughput}kbit latency {2 * delay}ms",
		f"random packet reordering ({percentage_low}% {percentage_mid}%) & packet duplication ({percentage_low}%)":
			f"sudo tc qdisc add dev {device} root netem delay 10ms reorder {percentage_low}% {percentage_mid}% duplicate {percentage_low}%",
		f"random packet drops ({percentage_low}%) & low throughput ({throughput}kbps {delay}ms)":
			f"sudo tc qdisc add dev {device} root netem loss {percentage_low}% rate {throughput}kbit latency {delay}ms",
		f"random packet duplication ({percentage_low}%) & bitflips ({packet_duplication_bitflips}%)":
			f"sudo tc qdisc add dev {device} root netem duplicate {percentage_low}% corrupt {packet_duplication_bitflips}%",
	}

	reset_command = f"sudo tc qdisc del dev {device} root"
	return (test_commands, reset_command)
