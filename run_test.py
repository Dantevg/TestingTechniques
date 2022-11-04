import os
import sys
import run_tests

def main():
	if len(sys.argv) != 3:
		print("Usage: run_test <network device> <test>")
		return
	
	device = sys.argv[1]
	test = sys.argv[2]
	
	(test_commands, reset_command) = run_tests.get_commands(device)
	
	if not test in test_commands:
		print(f"No such test '{test}'. Possible tests: {list(test_commands.keys())}")
		return
		
	if os.geteuid() != 0:
		print("tc command needs root, run again with sudo")
		return
		
	run_tests.exec_command(reset_command)
	run_tests.run_test(test, (test_commands, reset_command))

if __name__ == "__main__":
	main()
