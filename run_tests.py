import os
import sys
import server_client
import random

ANSI_RESET = "\x1b[0m"
ANSI_RED = "\x1b[31m"
ANSI_GREEN = "\x1b[32m"

slow_tests = ["delay", "jittered delay", "packet drops & low throughput", "jittered delay & low throughput"]


def get_commands(device):
    delay = random.randint(50, 500)
    delay_lower = int(random.uniform(0.2, 0.8) * delay)
    percentage_mid = random.randint(35, 65)
    percentage_low = random.randint(5, 30)
    throughput = random.randint(1, 10) * 128
    test_commands = {
        "baseline": "",
        "delay": f"sudo tc qdisc add dev {device} root netem delay {delay}ms",
        "jittered delay": f"sudo tc qdisc add dev {device} root netem delay {delay}ms {delay_lower}ms",
        "packet drops": f"sudo tc qdisc add dev {device} root netem loss {percentage_low}%",
        "low throughput": f"sudo tc qdisc add dev {device} root tbf rate {throughput}kbit burst 16kbit latency {delay}ms",
        "packet reordering": f"sudo tc qdisc add dev {device} root netem delay 10ms reorder {percentage_low}% {percentage_mid}%",
        "packet duplication": f"sudo tc qdisc add dev {device} root netem duplicate {percentage_low}%",
        "bitflips": f"sudo tc qdisc add dev {device} root netem corrupt {percentage_low}%",
        "jittered delay & low throughput": f"sudo tc qdisc add dev {device} root netem delay {delay}ms {delay_lower}ms rate {throughput}kbit latency {2 * delay}ms",
        "packet reordering & packet duplication": f"sudo tc qdisc add dev {device} root netem delay 10ms reorder {percentage_low}% {percentage_mid}% duplicate {percentage_low}%",
        "packet drops & low throughput": f"sudo tc qdisc add dev {device} root netem loss {percentage_low}% rate {throughput}kbit latency {delay}ms",
        "packet duplication & bitflips": f"sudo tc qdisc add dev {device} root netem duplicate {percentage_low}% corrupt {int(random.uniform(1, 2) * percentage_low)}%",
    }

    reset_command = f"sudo tc qdisc del dev {device} root"
    return (test_commands, reset_command)


def exec_command(command):
    print(f"test: running command '{command}'")
    return os.system(command)


def run_test(desc, commands):
    (test_commands, reset_command) = commands
    print(f"\n===== test '{desc}'")
    if exec_command(test_commands[desc]) != 0:
        print("Failed to execute network tampering command")
        exec_command(reset_command)
        return
    if desc in slow_tests:
        n_errors = server_client.run_server_client(client_args={"messages": 10, "update_interval": 1})
    else:
        n_errors = server_client.run_server_client()
    exec_command(reset_command)
    return n_errors == 0


def print_results(statuses):
    print()
    print("Test report")
    print("===========")
    for desc in statuses:
        if statuses[desc]:
            print(f"{ANSI_GREEN}✓ {desc}{ANSI_RESET}")
        else:
            print(f"{ANSI_RED}✘ {desc}{ANSI_RESET}")

    n_passed = len([x for x in statuses if statuses[x]])
    print(f"{str(n_passed)} tests passed, {len(statuses) - n_passed} failed.")


def main():
    if len(sys.argv) != 2:
        print("Expecting network device as argument, probably 'lo' (find using 'ip address')")
        return

    (test_commands, reset_command) = get_commands(sys.argv[1])

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
