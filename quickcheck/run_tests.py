import pytest
from pytest import list_of, Generator

N_PACKETS = 100
PACKET_LENGTH = 1024

# Delay { delay :: Int }
# JitteredDelay { jitterDelay :: Int ; jitter :: Int }
# PacketDrops { loss :: Int }
# LowThroughput { rate :: Int ; burst :: Int ; latency :: Int }
# Reordering { reorder :: Int ; correlation :: Int }
# Duplication { duplicate :: Int } 
# Bitflips { corrupt :: Int }

tamperings = {
	"Delay": {
		"delay": lambda x: x.generate_data(int, min_num = 0, max_num=400),
	},
	"JitteredDelay": {
		"delay": lambda x: x.generate_data(int, min_num = 0, max_num=400),
		"jitter": lambda x: x.generate_data(int, min_num = 0, max_num=320),
	},
	"PacketDrops": {},
	"LowThroughput": {},
	"Reordering": {},
	"Duplication": {},
	"Bitflips": {},
}

class Tampering(Generator):
	def generate(self):
		tampering = tamperings[self.generate_data(str, choices=list(tamperings.keys()))]
		values = {}
		for k in tampering.keys(): values[k] = tampering[k](self)
		return values

@pytest.mark.randomize(tamperings=list_of(Tampering(), min_items=1, max_items=2))
def test_generate_tampering(tamperings):
	# TODO: really do something, this is just here to see the output of Tampering()
	assert tamperings == "Delay"

@pytest.mark.randomize(
	packets=list_of(str, min_items=N_PACKETS, max_items=N_PACKETS),
	fixed_length=PACKET_LENGTH)
def test_generate_packets(packets):
	pass
