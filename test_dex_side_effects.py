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

ADD_1 = 1
CANCEL_2 = 2
CANCEL_3 = 3
CANCEL_4 = 4


class DexCrossEcosystemSideEffectsTest(MasterTestFramework):

    def run_test(self):
        """Tests side effects and interferences of the traditional and token exchange."""
        self.entities = [TestEntity(node) for node in self.nodes]

        self.prepare_funding()
        self.prepare_properties()
        self.initial_distribution()

        self.test_dex_side_effects_on_other_ecosystem()
        self.test_dex_side_effects_on_same_ecosystem()

        self.success = TestInfo.Status()


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

        if len(node.omni_listproperties()) > 2:
            AssertionError('There should not be more than two properties, MSC and TMSC, after a clean start')

        # tx: 50, ecosystem: 2, 9223372036854775807 indivisible tokens, "TIndiv1"
        node.omni_sendrawtx(addr, '0000003202000100000000000054496e646976310000007fffffffffffffff')
        # tx: 50, ecosystem: 2, 9223372036854775807 indivisible tokens, "TIndiv2"
        node.omni_sendrawtx(addr, '0000003202000100000000000054496e646976320000007fffffffffffffff')
        # tx: 50, ecosystem: 2, 9223372036854775807 indivisible tokens, "TIndiv3"
        node.omni_sendrawtx(addr, '0000003202000100000000000054496e646976330000007fffffffffffffff')
        # tx: 50, ecosystem: 2, 9223372036854775807 indivisible tokens, "TIndivMax"
        node.omni_sendrawtx(addr, '0000003202000100000000000054496e6469764d61780000007fffffffffffffff')
        # tx: 50, ecosystem: 2, 92233720368.54770000 divisible tokens, "TDiv1"
        node.omni_sendrawtx(addr, '0000003202000200000000000054446976310000007fffffffffffffff')
        # tx: 50, ecosystem: 2, 92233720368.54770000 divisible tokens, "TDiv2"
        node.omni_sendrawtx(addr, '0000003202000200000000000054446976320000007fffffffffffffff')
        # tx: 50, ecosystem: 2, 92233720368.54770000 divisible tokens, "TDiv3"
        node.omni_sendrawtx(addr, '0000003202000200000000000054446976330000007fffffffffffffff')
        # tx: 50, ecosystem: 2, 92233720368.54770000 divisible tokens, "TDivMax"
        node.omni_sendrawtx(addr, '00000032020002000000000000544469764d61780000007fffffffffffffff')
        # tx: 50, ecosystem: 1, 9223372036854775807 indivisible tokens, "MIndiv1"
        node.omni_sendrawtx(addr, '000000320100010000000000004d496e646976310000007fffffffffffffff')
        # tx: 50, ecosystem: 1, 92233720368.54770000 divisible tokens, "MDiv1"
        node.omni_sendrawtx(addr, '000000320100020000000000004d446976310000007fffffffffffffff')

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

        A1 (node 2) gets 50.0 BTC, 63.5 MSC and 63.5 TMSC.

        Final balances are tested."""
        entity_miner = self.entities[0]
        entity_a1 = self.entities[1]

        entity_miner.send_bitcoins(entity_a1.address, 50.0)
        entity_miner.send(entity_a1.address, MSC,  '63.50000000')
        entity_miner.send(entity_a1.address, TMSC, '63.50000000')

        self.generate_block()
        self.check_balance(entity_a1.address, MSC,    '63.50000000', '0.00000000')
        self.check_balance(entity_a1.address, TMSC,   '63.50000000', '0.00000000')
        self.check_balance(entity_a1.address, TDiv1,   '0.00000000', '0.00000000')
        self.check_balance(entity_a1.address, TIndiv1, '0',          '0')


    def test_dex_side_effects_on_other_ecosystem(self):
        """
        1. A1 starts with 63.5 MSC, 63.5 TMSC, 0 TIndiv1 and 0.0 TDiv1
        2. A1 offers 10.0 MSC for 2.0 BTC (traditional)
        3. A1 offers 10.0 TMSC for 25 TIndiv1
        4. A1 offers 11.5 TMSC for 0.75 TDiv1
        5. A1 cancels 10.0 MSC for 2.0 BTC (traditional)
        6, A1 cancels 11.5 TMSC for 0.75 TDiv1
        7. A1 cancels 10.0 TMSC for 25 TIndiv1

        After this test A1 should have the same balance as at the beginning."""
        entity_a1 = self.entities[1]

        # 1. A1 starts with 63.5 MSC, 63.5 TMSC, 0 TIndiv1 and 0.0 TDiv1
        self.check_balance(entity_a1.address, MSC,    '63.50000000',  '0.00000000')  # SP 1
        self.check_balance(entity_a1.address, TMSC,   '63.50000000',  '0.00000000')  # SP 2
        self.check_balance(entity_a1.address, TIndiv1, '0',           '0')           # SP 2147483651
        self.check_balance(entity_a1.address, TDiv1,   '0.00000000',  '0.00000000')  # SP 2147483655

        self.check_active_dex_offers_count(0)
        self.check_orderbook_count(0, MSC)
        self.check_orderbook_count(0, TMSC)
        self.check_orderbook_count(0, TIndiv1)
        self.check_orderbook_count(0, TDiv1)

        # 2. A1 offers 10.0 MSC for 2.0 BTC (traditional)
        TestInfo.log(entity_a1.address + ' offers 10.00000000 MSC for 2.0 BTC')
        entity_a1.node.omni_sendrawtx(entity_a1.address,
                                    '0001001400000001000000003b9aca00000000000bebc2000a000000000000271001')

        self.generate_block()
        self.check_balance(entity_a1.address, MSC,    '53.50000000', '10.00000000')  # SP 1
        self.check_balance(entity_a1.address, TMSC,   '63.50000000',  '0.00000000')  # SP 2
        self.check_balance(entity_a1.address, TIndiv1, '0',           '0')           # SP 2147483651
        self.check_balance(entity_a1.address, TDiv1,   '0.00000000',  '0.00000000')  # SP 2147483655

        self.check_active_dex_offers_count(1)
        self.check_orderbook_count(0, MSC)
        self.check_orderbook_count(0, TMSC)
        self.check_orderbook_count(0, TIndiv1)
        self.check_orderbook_count(0, TDiv1)

        # 3. A1 offers 10.0 TMSC for 25 TIndiv1
        # 4.           11.5 TMSC for 0.75 TDiv1 (combined)
        entity_a1.trade('10.00000000', TMSC, '25', TIndiv1, ADD_1)
        entity_a1.trade('13.50000000', TMSC, '0.75', TDiv1, ADD_1)

        self.generate_block()
        self.check_balance(entity_a1.address, MSC,    '53.50000000', '10.00000000')  # SP 1
        self.check_balance(entity_a1.address, TMSC,   '40.00000000', '23.50000000')  # SP 2
        self.check_balance(entity_a1.address, TIndiv1, '0',           '0')           # SP 2147483651
        self.check_balance(entity_a1.address, TDiv1,   '0.00000000',  '0.00000000')  # SP 2147483655

        self.check_active_dex_offers_count(1)
        self.check_orderbook_count(0, MSC)
        self.check_orderbook_count(2, TMSC)

        # 5. A1 cancels 10.0 MSC for 2.0 BTC (traditional)
        TestInfo.log(entity_a1.address + ' cancels 10.00000000 MSC for 2.0 BTC')
        entity_a1.node.omni_sendrawtx(entity_a1.address,
                                    '0001001400000001000000003b9aca00000000000000000000000000000000000003')

        self.generate_block()
        self.check_balance(entity_a1.address, MSC,    '63.50000000',  '0.00000000')  # SP 1
        self.check_balance(entity_a1.address, TMSC,   '40.00000000', '23.50000000')  # SP 2
        self.check_balance(entity_a1.address, TIndiv1, '0',           '0')           # SP 2147483651
        self.check_balance(entity_a1.address, TDiv1,   '0.00000000',  '0.00000000')  # SP 2147483655

        self.check_active_dex_offers_count(0)
        self.check_orderbook_count(0, MSC)
        self.check_orderbook_count(2, TMSC)

        # 6. A1 cancels 10.0 TMSC for 25 TIndiv1
        # 7.            11.5 TMSC for 0.75 TDiv1 (combined)
        entity_a1.trade('10.00000000', TMSC, '25', TIndiv1, CANCEL_2)
        entity_a1.trade('13.50000000', TMSC, '0.75', TDiv1, CANCEL_2)

        self.generate_block()
        self.check_balance(entity_a1.address, MSC,    '63.50000000', '0.00000000')  # SP 1
        self.check_balance(entity_a1.address, TMSC,   '63.50000000', '0.00000000')  # SP 2
        self.check_balance(entity_a1.address, TIndiv1, '0',          '0')           # SP 2147483651
        self.check_balance(entity_a1.address, TDiv1,   '0.00000000', '0.00000000')  # SP 2147483655

        self.check_active_dex_offers_count(0)
        self.check_orderbook_count(0, MSC)
        self.check_orderbook_count(0, TMSC)
        self.check_orderbook_count(0, TIndiv1)
        self.check_orderbook_count(0, TDiv1)


    def test_dex_side_effects_on_same_ecosystem(self):
        """
        1. A1 starts with 63.5 MSC, 63.5 TMSC, 0 TIndiv1 and 0.0 TDiv1
        2. A1 offers 0.5 TMSC for 5000000000 TIndiv1
        3. A1 offers 3.0 TMSC for 30.0 TDiv1
        4. A1 offers 10.0 TMSC for 0.1 BTC (traditional)
        5. A1 cancels 10.0 TMSC for 0.1 BTC (traditional)
        6. A1 cancels 3.0 TMSC for 30.0 TDiv1
        7. A1 cancels 0.5 TMSC for 5000000000 TIndiv1

        After this test A1 should have the same balance as at the beginning."""
        entity_miner = self.entities[0]
        entity_a1 = self.entities[1]

        # 1. A1 starts with 63.5 MSC, 63.5 TMSC, 0 TIndiv1 and 0.0 TDiv1
        self.check_balance(entity_a1.address, MSC,    '63.50000000',  '0.00000000')  # SP 1
        self.check_balance(entity_a1.address, TMSC,   '63.50000000',  '0.00000000')  # SP 2
        self.check_balance(entity_a1.address, TIndiv1, '0',           '0')           # SP 2147483651
        self.check_balance(entity_a1.address, TDiv1,   '0.00000000',  '0.00000000')  # SP 2147483655

        self.check_active_dex_offers_count(0)
        self.check_orderbook_count(0, MSC)
        self.check_orderbook_count(0, TMSC)
        self.check_orderbook_count(0, TDiv1)
        self.check_orderbook_count(0, TIndiv1)

        # 2. A1 offers 0.5 TMSC for 5000000000 TIndiv1
        entity_a1.trade('0.50000000', TMSC, '5000000000', TIndiv1, ADD_1)

        self.generate_block()
        self.check_balance(entity_a1.address, MSC,    '63.50000000',  '0.00000000')
        self.check_balance(entity_a1.address, TMSC,   '63.00000000',  '0.50000000')
        self.check_balance(entity_a1.address, TIndiv1, '0',           '0')           # SP 2147483651
        self.check_balance(entity_a1.address, TDiv1,   '0.00000000',  '0.00000000')  # SP 2147483655

        self.check_active_dex_offers_count(0)
        self.check_orderbook_count(0, MSC)
        self.check_orderbook_count(1, TMSC)

        # 3. A1 offers 3.0 TMSC for 30.0 TDiv1
        entity_a1.trade('3.00000000', TMSC, '30.00000000', TDiv1, ADD_1)

        self.generate_block()
        self.check_balance(entity_a1.address, MSC,    '63.50000000',  '0.00000000')
        self.check_balance(entity_a1.address, TMSC,   '60.00000000',  '3.50000000')
        self.check_balance(entity_a1.address, TIndiv1, '0',           '0')           # SP 2147483651
        self.check_balance(entity_a1.address, TDiv1,   '0.00000000',  '0.00000000')  # SP 2147483655

        self.check_active_dex_offers_count(0)
        self.check_orderbook_count(0, MSC)
        self.check_orderbook_count(2, TMSC)
        self.check_orderbook_count(0, TDiv1)

        # 4. A1 offers 10.0 TMSC for 0.1 BTC
        TestInfo.log(entity_a1.address + ' offers 10.00000000 TMSC for 0.1 BTC')
        entity_a1.node.omni_sendrawtx(entity_a1.address,
                                    '0001001400000002000000003b9aca0000000000009896800a000000000000271001')

        self.generate_block()
        self.check_balance(entity_a1.address, MSC,    '63.50000000',  '0.00000000')
        self.check_balance(entity_a1.address, TMSC,   '50.00000000', '13.50000000')
        self.check_balance(entity_a1.address, TIndiv1, '0',           '0')           # SP 2147483651
        self.check_balance(entity_a1.address, TDiv1,   '0.00000000',  '0.00000000')  # SP 2147483655

        self.check_active_dex_offers_count(1)
        self.check_orderbook_count(0, MSC)
        self.check_orderbook_count(2, TMSC)

        # 5. A1 cancels 10.0 TMSC for 0.1 BTC
        TestInfo.log(entity_a1.address + ' cancels 10.00000000 TMSC for 0.1 BTC')
        entity_a1.node.omni_sendrawtx(entity_a1.address,
                                    '0001001400000002000000003b9aca0000000000000000000a000000000000000003')

        self.generate_block()
        self.check_balance(entity_a1.address, MSC,    '63.50000000',  '0.00000000')
        self.check_balance(entity_a1.address, TMSC,   '60.00000000',  '3.50000000')
        self.check_balance(entity_a1.address, TIndiv1, '0',           '0')           # SP 2147483651
        self.check_balance(entity_a1.address, TDiv1,   '0.00000000',  '0.00000000')  # SP 2147483655

        self.check_active_dex_offers_count(0)
        self.check_orderbook_count(0, MSC)
        self.check_orderbook_count(2, TMSC)

        # 6. A1 cancels 3.0 TMSC for 30.0 TDiv1
        # 7.            0.5 TMSC for 5000000000 TIndiv1
        entity_a1.trade('3.00000000', TMSC, '30.00000000', TDiv1, CANCEL_2)
        entity_a1.trade('0.50000000', TMSC, '5000000000', TIndiv1, CANCEL_2)

        self.generate_block()
        self.check_balance(entity_a1.address, MSC,    '63.50000000',  '0.00000000')
        self.check_balance(entity_a1.address, TMSC,   '63.50000000',  '0.00000000')
        self.check_balance(entity_a1.address, TIndiv1, '0',           '0')           # SP 2147483651
        self.check_balance(entity_a1.address, TDiv1,   '0.00000000',  '0.00000000')  # SP 2147483655

        self.check_active_dex_offers_count(0)
        self.check_orderbook_count(0, MSC)
        self.check_orderbook_count(0, TMSC)
        self.check_orderbook_count(0, TDiv1)
        self.check_orderbook_count(0, TIndiv1)


if __name__ == '__main__':
    DexCrossEcosystemSideEffectsTest().main()
