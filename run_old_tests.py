#!/usr/bin/env python2
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

import sys

from framework_info import TestInfo
from test_exodus_purchase import ExodusPurchaseTest
from test_p2sh import P2SHTest
from test_property_creation import PropertyCreationTest
from test_simple_send import SimpleSendTest
from test_sto import SendToOwnersTest
from test_traditional_dex import TraditionalDexTest

all_tests = []
exit_status = 0

def enqueue_test(test):
    all_tests.append(test())

def start_tests():
    for test in all_tests:
        test.main()

def print_test_results():
    global exit_status
    errors = 0
    skipped = 0
    test_count = len(all_tests)
    TestInfo.log('\n-----------------------------------------------------')
    TestInfo.log('\nTest summary:\n')
    for test in all_tests:
        test_name = test.__class__.__name__
        if errors > 0 and TestInfo.FAIL_HARD:
            TestInfo.log(test_name + ' ... skipped')
            skipped += 1
            continue
        if test.success:
            TestInfo.log(test_name + ' ... successful')
        else:
            errors += 1
            TestInfo.log(test_name + ' ... failed')
    TestInfo.log('\n%d of %d tests successful (%s skipped)' % (test_count-errors, test_count, skipped,))
    exit_status = int(errors > 0)


if __name__ == '__main__':
    # TODO: create a test container

    enqueue_test (ExodusPurchaseTest)
    enqueue_test (SimpleSendTest)
    enqueue_test (PropertyCreationTest)
    enqueue_test (P2SHTest)
    enqueue_test (TraditionalDexTest)
    enqueue_test (SendToOwnersTest)

    start_tests()
    print_test_results()

    sys.exit(exit_status)
