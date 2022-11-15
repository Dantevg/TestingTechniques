import os
import sys
import server_client
import tests

ANSI_RESET = "\x1b[0m"
ANSI_RED = "\x1b[31m"
ANSI_GREEN = "\x1b[32m"
ANSI_BLUE = "\x1b[34m"

def exec_command(command):
	print(f"test: running command '{command}'")
	return os.system(command)


def run_test(desc, commands):
	(test_commands, reset_command) = commands
	print(f"\n━━━━━ test '{desc}'")
	if exec_command(test_commands[desc]) != 0:
		print("Failed to execute network tampering command")
		exec_command(reset_command)
		return
	if tests.is_slow(desc):
		test_results = server_client.run_server_client(client_args={"messages": 10, "update_interval": 1})
	else:
		test_results = server_client.run_server_client()
	exec_command(reset_command)
	return test_results

def print_results(statuses):
	print()
	print("TEST REPORT")
	print("┏━━━━━━━━━━")
	for desc in statuses:
		results = statuses[desc]
		if results != None and results["errors"] == 0:
			print(f"┃ {ANSI_GREEN}✓ {desc}{ANSI_RESET} in {ANSI_BLUE}{results['time']:.2f}s{ANSI_RESET}")
		elif results != None:
			print(f"┃ {ANSI_RED}✘ {desc} {ANSI_BLUE}{results['errors']}{ANSI_RESET} errors in {ANSI_BLUE}{results['time']:.2f}s{ANSI_RESET}")
		else:
			print(f"┃ {ANSI_RED}✘ {desc}{ANSI_RESET} errored")
	
	n_passed = len([desc for desc in statuses if statuses[desc] != None and statuses[desc]["errors"] == 0])
	print(f"┃ {str(n_passed)} tests passed, {len(statuses) - n_passed} failed.")
	if n_passed == len(statuses):
		print(f"┃ Final verdict: {ANSI_GREEN}PASSED{ANSI_RESET}")
	else:
		print(f"┃ Final verdict: {ANSI_RED}FAILED{ANSI_RESET}")

def main():
	if len(sys.argv) != 2:
		print("Expecting network device as argument, probably 'lo' (find using 'ip address')")
		return

	(test_commands, reset_command) = tests.get_commands(sys.argv[1])

	if os.geteuid() != 0:
		print("tc command needs root, run again with sudo")
		return

	test_statuses = {}
	try:
		exec_command(reset_command)
		for desc in test_commands:
			test_statuses[desc] = run_test(desc, (test_commands, reset_command))
	except KeyboardInterrupt:
		exec_command(reset_command)
		sys.exit(0)

	print_results(test_statuses)


if __name__ == "__main__":
	main()
