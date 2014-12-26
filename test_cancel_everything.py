#!/usr/bin/env python2
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

from framework_extension import MasterTestFramework
from framework_entity import TestEntity
from framework_info import TestInfo

# Helper

BTC = 0
MSC = 1
TMSC = 2
MIndiv1 = 3
MDiv1 = 4
TIndiv1 = 2147483651
TIndiv2 = 2147483652
TIndiv3 = 2147483653
TIndivMax = 2147483654
TDiv1 = 2147483655
TDiv2 = 2147483656
TDiv3 = 2147483657
TDivMax = 2147483658
TNotCreated = 2147483659


ADD_1 = 1
CANCEL_2 = 2
CANCEL_3 = 3
CANCEL_4 = 4


class MetaDexCancelEverythingInSameEcosystemTest(MasterTestFramework):

    def run_test(self):
        """Tests expected effects of valid CANCEL-EVERYTHING commands in the same ecosystem."""
        self.entities = [TestEntity(node) for node in self.nodes]

        self.prepare_funding()
        self.prepare_properties()
        self.initial_distribution()

        self.test_cancel_everything_with_sane_values()
        self.test_cancel_everything_with_zero_amounts()
        self.test_cancel_everything_mixed_amounts()


    def prepare_funding(self):
        """The miner (node 1) furthermore purchases 50000.0 MSC and 50000.0 TMSC."""
        entity_miner = self.entities[0]

        entity_miner.send_bitcoins(entity_miner.address)
        entity_miner.purchase_mastercoins(500.0)

        self.generate_block()
        self.check_balance(entity_miner.address, MSC,  '50000.00000000', '0.00000000')
        self.check_balance(entity_miner.address, TMSC, '50000.00000000', '0.00000000')


    def prepare_properties(self):
        """The miner (node 1) creates 8 new properties with the maximum amounts possible.

        4 with divisible units: TDiv1, TDiv2, TDiv3, TDivMax
        4 with indivisible units: TIndiv1, TIndiv2, TIndiv3, TIndivMax

        The tokens are going to be distributed as needed.

        Final balances of miner (node 1) are tested to confirm correct property creation."""
        node = self.entities[0].node
        addr = self.entities[0].address

        if len(node.listproperties_MP()) > 2:
            AssertionError('There should not be more than two properties, MSC and TMSC, after a clean start')

        # tx: 50, ecosystem: 2, 9223372036854775807 indivisible tokens, "TIndiv1"
        node.sendrawtx_MP(addr, '0000003202000100000000000054496e646976310000007fffffffffffffff')
        # tx: 50, ecosystem: 2, 9223372036854775807 indivisible tokens, "TIndiv2"
        node.sendrawtx_MP(addr, '0000003202000100000000000054496e646976320000007fffffffffffffff')
        # tx: 50, ecosystem: 2, 9223372036854775807 indivisible tokens, "TIndiv3"
        node.sendrawtx_MP(addr, '0000003202000100000000000054496e646976330000007fffffffffffffff')
        # tx: 50, ecosystem: 2, 9223372036854775807 indivisible tokens, "TIndivMax"
        node.sendrawtx_MP(addr, '0000003202000100000000000054496e6469764d61780000007fffffffffffffff')
        # tx: 50, ecosystem: 2, 92233720368.54770000 divisible tokens, "TDiv1"
        node.sendrawtx_MP(addr, '0000003202000200000000000054446976310000007fffffffffffffff')
        # tx: 50, ecosystem: 2, 92233720368.54770000 divisible tokens, "TDiv2"
        node.sendrawtx_MP(addr, '0000003202000200000000000054446976320000007fffffffffffffff')
        # tx: 50, ecosystem: 2, 92233720368.54770000 divisible tokens, "TDiv3"
        node.sendrawtx_MP(addr, '0000003202000200000000000054446976330000007fffffffffffffff')
        # tx: 50, ecosystem: 2, 92233720368.54770000 divisible tokens, "TDivMax"
        node.sendrawtx_MP(addr, '00000032020002000000000000544469764d61780000007fffffffffffffff')
        # tx: 50, ecosystem: 1, 9223372036854775807 indivisible tokens, "MIndiv1"
        node.sendrawtx_MP(addr, '000000320100010000000000004d496e646976310000007fffffffffffffff')
        # tx: 50, ecosystem: 1, 92233720368.54770000 divisible tokens, "MDiv1"
        node.sendrawtx_MP(addr, '000000320100020000000000004d446976310000007fffffffffffffff')

        self.generate_block()
        self.check_balance(addr, TIndiv1,   '9223372036854775807',  '0')
        self.check_balance(addr, TIndiv2,   '9223372036854775807',  '0')
        self.check_balance(addr, TIndiv3,   '9223372036854775807',  '0')
        self.check_balance(addr, TIndivMax, '9223372036854775807',  '0')
        self.check_balance(addr, TDiv1,     '92233720368.54775807', '0.00000000')
        self.check_balance(addr, TDiv2,     '92233720368.54775807', '0.00000000')
        self.check_balance(addr, TDiv3,     '92233720368.54775807', '0.00000000')
        self.check_balance(addr, TDivMax,   '92233720368.54775807', '0.00000000')
        self.check_balance(addr, MIndiv1,   '9223372036854775807',  '0')
        self.check_balance(addr, MDiv1,     '92233720368.54775807', '0.00000000')


    def initial_distribution(self):
        """Tokens and bitcoins are sent from the miner (node 1) to A1 (node 2).

        A1 (node 2) gets 50.0 BTC, 50.0 MSC, 50.0 TMSC, 50.0 TDiv1 and 50 MIndiv1.

        Final balances are tested."""
        entity_miner = self.entities[0]
        entity_a1 = self.entities[1]

        entity_miner.send_bitcoins(entity_a1.address, 50.0)
        entity_miner.send(entity_a1.address, MSC,     '50.00000000')
        entity_miner.send(entity_a1.address, TMSC,    '50.00000000')
        entity_miner.send(entity_a1.address, MIndiv1, '50')
        # A1 does not receive any MDiv1
        # A1 does not receive any TIndiv1
        entity_miner.send(entity_a1.address, TDiv1,   '50.00000000')

        self.generate_block()
        self.check_balance(entity_a1.address, MSC,     '50.00000000', '0.00000000')  # SP 1
        self.check_balance(entity_a1.address, TMSC,    '50.00000000', '0.00000000')  # SP 2
        self.check_balance(entity_a1.address, MIndiv1, '50',          '0')           # SP 3
        self.check_balance(entity_a1.address, MDiv1,    '0.00000000', '0.00000000')  # SP 4
        self.check_balance(entity_a1.address, TIndiv1,  '0',          '0')           # SP 2147483651
        self.check_balance(entity_a1.address, TDiv1,   '50.00000000', '0.00000000')  # SP 2147483655


    def test_cancel_everything_with_sane_values(self):
        """Tests CANCEL-EVERYTHING command with sane values.

        It is NOT tested:
        - if the offer to cancel has a different price level than provided
        - if amount values are ignored
        - if property values are ignored (as long as they are in the same ecosystem)
        - if cancellation of offers is limited to the targeted ecosystem
        - if cancellation of offers is limited to meta DEx offers

        1. A1 starts with 50.0 MSC, 50 MIndiv1 and 0.0 MDiv1
        2. A1 offers 50.0 MSC for 600.0 MDiv1
        3. A1 cancels everything in the main ecosystem (50.0 TMSC, 600.0 MDiv1)

        After this test A1 should have the same balance as at the beginning."""
        entity_a1 = self.entities[1]

        # 1. A1 starts with 50.0 MSC, 50 MIndiv1 and 0.0 MDiv1
        self.check_balance(entity_a1.address, MSC,     '50.00000000',  '0.00000000')  # SP 1
        self.check_balance(entity_a1.address, MIndiv1, '50',           '0')           # SP 3
        self.check_balance(entity_a1.address, MDiv1,    '0.00000000',  '0.00000000')  # SP 4

        # 2. A1 offers 50.0 MSC for 600.0 MDiv1
        entity_a1.trade('50.00000000', MSC, '600.00000000', MDiv1, ADD_1)
        self.generate_block()
        self.check_balance(entity_a1.address, MSC,      '0.00000000', '50.00000000')  # SP 1
        self.check_balance(entity_a1.address, MIndiv1, '50',           '0')           # SP 3
        self.check_balance(entity_a1.address, MDiv1,    '0.00000000',  '0.00000000')  # SP 4

        # 3. A1 cancels everything in the main ecosystem (50.0 TMSC, 600.0 MDiv1)
        entity_a1.trade('50.00000000', MSC, '600.00000000', MDiv1, CANCEL_4)
        self.generate_block()
        self.check_balance(entity_a1.address, MSC,     '50.00000000',  '0.00000000')  # SP 1
        self.check_balance(entity_a1.address, MIndiv1, '50',           '0')           # SP 3
        self.check_balance(entity_a1.address, MDiv1,    '0.00000000',  '0.00000000')  # SP 4


    def test_cancel_everything_with_zero_amounts(self):
        """Tests CANCEL-EVERYTHING command and if amount values are ignored.

        The offers to cancel should not be matched by a price ratio and usually invalid
        amounts, such as zero, should be accepted.

        It is NOT tested:
        - if property values are ignored (as long as they are in the same ecosystem)
        - if cancellation of offers is limited to the targeted ecosystem
        - if cancellation of offers is limited to meta DEx offers

        1. A1 starts with 50.0 MSC, 50 MIndiv1 and 0.0 MDiv1
        2. A1 offers 50 MIndiv1 for 0.6 MSC in two trades
        3. A1 cancels everything in the main ecosystem (0.0 MSC, 0.0 MDiv1)

        After this test A1 should have the same balance as at the beginning."""
        entity_a1 = self.entities[1]

        # 1. A1 starts with 50.0 MSC, 50 MIndiv1 and 0.0 MDiv1
        self.check_balance(entity_a1.address, MSC,     '50.00000000',  '0.00000000')  # SP 1
        self.check_balance(entity_a1.address, MIndiv1, '50',           '0')           # SP 3
        self.check_balance(entity_a1.address, MDiv1,    '0.00000000',  '0.00000000')  # SP 4

        # 2. A1 offers 50 MIndiv1 for 0.6 MSC in two trades
        entity_a1.trade('40', MIndiv1, '0.1', MSC, ADD_1)
        entity_a1.trade('10', MIndiv1, '0.5', MSC, ADD_1)
        self.generate_block()
        self.check_balance(entity_a1.address, MSC,     '50.00000000',  '0.00000000')  # SP 1
        self.check_balance(entity_a1.address, MIndiv1,  '0',          '50')           # SP 3
        self.check_balance(entity_a1.address, MDiv1,    '0.00000000',  '0.00000000')  # SP 4

        # 3. A1 cancels everything in the main ecosystem (0.0 MSC, 0.0 MDiv1)
        entity_a1.trade('0.00000000', MSC, '0.00000000', MDiv1, CANCEL_4)
        self.generate_block()
        self.check_balance(entity_a1.address, MSC,     '50.00000000',  '0.00000000')  # SP 1
        self.check_balance(entity_a1.address, MIndiv1, '50',           '0')           # SP 3
        self.check_balance(entity_a1.address, MDiv1,    '0.00000000',  '0.00000000')  # SP 4


    def test_cancel_everything_mixed_amounts(self):
        """Tests cancellation of offers via CANCEL-EVERYTHING command.

        It is NOT tested:
        - if property values are ignored (as long as they are in the same ecosystem)
        - if cancellation of offers is limited to the targeted ecosystem
        - if cancellation of offers is limited to meta DEx offers

        1. A1 starts with 50.0 MSC, 50 MIndiv1 and 0.0 MDiv1
        2. A1 offers 4.8 MSC for 15.16 MDiv1
        3. A1 offers 23 MIndiv1 for 42.0 MSC
        4. A1 cancels everything in the main ecosystem (0.0 MDiv1, 92233720368.54775807 MSC)

        After this test A1 should have the same balance as at the beginning."""
        entity_a1 = self.entities[1]

        # 1. A1 starts with 50.0 MSC, 50 MIndiv1 and 0.0 MDiv1
        self.check_balance(entity_a1.address, MSC,     '50.00000000',  '0.00000000')  # SP 1
        self.check_balance(entity_a1.address, MIndiv1, '50',           '0')           # SP 3
        self.check_balance(entity_a1.address, MDiv1,    '0.00000000',  '0.00000000')  # SP 4

        # 2. A1 offers 4.8 MSC for 15.16 MDiv1
        entity_a1.trade('4.80000000', MSC, '15.16000000', MDiv1, ADD_1)
        self.generate_block()
        self.check_balance(entity_a1.address, MSC,     '45.20000000',  '4.80000000')  # SP 1
        self.check_balance(entity_a1.address, MIndiv1, '50',           '0')           # SP 3
        self.check_balance(entity_a1.address, MDiv1,    '0.00000000',  '0.00000000')  # SP 4

        # 3. A1 offers 23 MIndiv1 for 42.0 MSC
        entity_a1.trade('23', MIndiv1, '42.00000000', MSC, ADD_1)
        self.generate_block()
        self.check_balance(entity_a1.address, MSC,     '45.20000000',  '4.80000000')  # SP 1
        self.check_balance(entity_a1.address, MIndiv1, '27',          '23')           # SP 3
        self.check_balance(entity_a1.address, MDiv1,    '0.00000000',  '0.00000000')  # SP 4

        # 4. A1 cancels everything in the main ecosystem (0.0 MDiv1, 92233720368.54775807 MSC)
        entity_a1.trade('0.00000000', MDiv1, '92233720368.54775807', MSC, CANCEL_4)
        self.generate_block()
        self.check_balance(entity_a1.address, MSC,     '50.00000000',  '0.00000000')  # SP 1
        self.check_balance(entity_a1.address, MIndiv1, '50',           '0')           # SP 3
        self.check_balance(entity_a1.address, MDiv1,    '0.00000000',  '0.00000000')  # SP 4


if __name__ == '__main__':
    MetaDexCancelEverythingInSameEcosystemTest().main()
