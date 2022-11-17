# Testing Techniques test tool
This test tool automatically runs all tests defined in [`src/tests.py`](src/tests.py).
It gathers the information about test pass/fail status and how long each test
took, and displays it in a summary.
The test cases also contain randomised tests, where the arguments to the network
tampering vary between a some lower and upper bound. They change every time the
tests are run.

Note that for some tests the number of messages sent is reduced from 100 to 10.
This is done for those tests that take a much longer time, i.e. with delay or
packet drops.

## Usage
1. **Clone this repository.**  
    `git clone git@github.com:Dantevg/TestingTechniques.git`
2. **Run the tests.** Make sure nothing else is using the localhost network.
    Sudo is required for the network tampering. The test runner expects one
    argument, the network interface to tamper with (usually `lo`, loopback).  
    `sudo python3 ./run_tests.py lo`
3. **Wait for test results.**
4. ???
5. **Profit!**
    ![test report / summary](./img/screenshot.png)
