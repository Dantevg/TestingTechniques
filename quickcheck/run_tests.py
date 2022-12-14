import os
import pytest
from pytest import list_of, Generator
import server_client2

N_PACKETS = 5
PACKET_LENGTH = 1024

def gen_int(x, min, max):
	return x.generate_data(int, min_num=min, max_num=max)

tamperings = {
	"Delay": lambda x: f"delay {gen_int(x, 0, 400)}ms",
	"JitteredDelay": lambda x: f"delay {gen_int(x, 0, 400)}ms {gen_int(x, 0, 320)}ms",
	"PacketDrops": lambda x: f"loss {gen_int(x, 0, 55)}%",
	"LowThroughput": lambda x: f"rate {gen_int(x, 0, 512)}kbit burst {gen_int(x, 0, 1024)}kbit latency {gen_int(x, 0, 500)}ms",
	"Reordering": lambda x: f"delay 10ms reorder {gen_int(x, 0, 55)}% {gen_int(x, 0, 70)}%",
	"Duplication": lambda x: f"duplicate {gen_int(x, 0, 55)}%",
	"Bitflips": lambda x: f"corrupt {gen_int(x, 0, 55)}%",
}

# TODO: check that commands and combinations actually work
# Probably there can be more combinations with LowThroughput
combinations = [
	("Delay",),
	("JitteredDelay",),
	("PacketDrops",),
	("LowThroughput",),
	("Reordering",),
	("Duplication",),
	("Bitflips",),
	("Delay", "PacketDrops"),
	# ("Delay", "JitteredDelay"),
	# ("Delay", "LowThroughput"),
	("Delay", "Reordering"),
	("Delay", "Duplication"),
	("Delay", "Bitflips"),
	("JitteredDelay", "PacketDrops"),
	# ("JitteredDelay", "LowThroughput"),
	("JitteredDelay", "Reordering"),
	("JitteredDelay", "Duplication"),
	("JitteredDelay", "Bitflips"),
	# ("PacketDrops", "LowThroughput"),
	("PacketDrops", "Reordering"),
	("PacketDrops", "Duplication"),
	("PacketDrops", "Bitflips"),
	# ("LowThroughput", "Reordering"),
	# ("LowThroughput", "Duplication"),
	# ("LowThroughput", "Bitflips"),
	("Reordering", "Duplication"),
	("Reordering", "Bitflips"),
	("Duplication", "Bitflips"),
]

def get_command(tamperings, device):
	return f"sudo tc qdisc add dev {device} root netem {' '.join(tamperings)}"

class Tamperings(Generator):
	def generate(self, **kwargs):
		tamperingNames = self.generate_data(str, choices=combinations)
		tamperingCommands = [tamperings[tamperingNames[0]](self)]
		if len(tamperingNames) == 2:
			tamperingCommands.append(tamperings[tamperingNames[1]](self))
		return tamperingCommands

@pytest.mark.randomize(
	tamperings=Tamperings(),
	packets=list_of(str, min_items=N_PACKETS, max_items=N_PACKETS),
	fixed_length=PACKET_LENGTH,
	ncalls=10
)
def test(tamperings, packets):
	command = get_command(tamperings, "lo")
	print(f"test: running command '{command}'")
	os.system("sudo tc qdisc del dev lo root")
	assert os.system(command) == 0
	q = server_client2.run_server_client(client_args={"messages": packets})
	for p1 in packets:
		p2 = q.get()
		assert p1 == p2
