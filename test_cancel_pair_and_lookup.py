#!/usr/bin/python
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

from framework_extension import MasterTestFramework
from framework_entity import TestEntity

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


class MetaDexCancelPairAndLookupTest(MasterTestFramework):

    def run_test(self):
        self.entities = [TestEntity(node) for node in self.nodes]

        self.prepare_funding()
        self.prepare_properties()
        self.initial_distribution()

        self.test_orderbook_with_two_properties()
        self.test_orderbook_with_one_main_property()
        self.test_orderbook_with_multiple_main_properties()
        self.test_orderbook_with_multiple_test_properties()
        self.test_lookup_primary_first()
        self.test_lookup_secondary_first()
        self.test_cancel_pair_msc_indiv_sane_sane()
        self.test_cancel_pair_msc_indiv_zero_sane()
        self.test_cancel_pair_msc_indiv_sane_zero()
        self.test_cancel_pair_msc_indiv_zero_zero()
        self.test_cancel_pair_indiv_msc_sane_sane()
        self.test_cancel_pair_indiv_msc_zero_sane()
        self.test_cancel_pair_indiv_msc_sane_zero()
        self.test_cancel_pair_indiv_msc_zero_zero()
        self.test_cancel_pair_msc_div_sane_sane()
        self.test_cancel_pair_of_several_combinations()


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


    def test_orderbook_with_two_properties(self):
        """
        1. Orderbook should be empty
        2. A1 starts with 50.0 MSC
        3. A1 offers 25.0 MSC for 25.0 MDiv1
        4. A1 cancels 25.0 MSC for 25.0 MDiv1 (cancel-at-price)

        After this test A1 should have the same balance as at the beginning."""
        entity_miner = self.entities[0]
        entity_a1 = self.entities[1]

        # 1. Orderbook should be empty
        self.check_orderbook_count(0, MSC, MDiv1)

        # 2. A1 starts with 50.0 MSC
        self.check_balance(entity_a1.address, MSC, '50.00000000', '0.00000000')

        # 3. A1 offers 25.0 MSC for 25.0 MDiv1
        entity_a1.trade('25.00000000', MSC, '25.00000000', MDiv1, ADD_1)
        self.generate_block()
        self.check_balance(entity_a1.address, MSC, '25.00000000', '25.00000000')
        self.check_orderbook_count(1, MSC, MDiv1)

        # 4. A1 cancels 25.0 MSC for 25.0 MDiv1 (cancel-at-price)
        entity_a1.trade('25.00000000', MSC, '25.00000000', MDiv1, CANCEL_2)
        self.generate_block()
        self.check_balance(entity_a1.address, MSC, '50.00000000', '0.00000000')
        self.check_orderbook_count(0, MSC, MDiv1)


    def test_orderbook_with_one_main_property(self):
        """
        1. Orderbook should be empty
        2. A1 starts with 50 MIndiv1
        3. A1 offers 10 MIndiv1 for 400 MSC
        4. A1 cancels 10 MIndiv1 for 400 MSC (cancel-at-price)

        After this test A1 should have the same balance as at the beginning."""
        entity_a1 = self.entities[1]

        # 1. Orderbook should be empty
        self.check_orderbook_count(0, MIndiv1)

        # 2. A1 starts with 50 MIndiv1
        self.check_balance(entity_a1.address, MIndiv1, '50', '0')

        # 3. A1 offers 10 MIndiv1 for 400 MSC
        entity_a1.trade('10', MIndiv1, '400', MSC, ADD_1)
        self.generate_block()
        self.check_balance(entity_a1.address, MIndiv1, '40', '10')
        self.check_orderbook_count(1, MIndiv1)

        # 4. A1 cancels 10 MIndiv1 for 400 MSC (cancel-at-price)
        entity_a1.trade('10', MIndiv1, '400', MSC, CANCEL_2)
        self.generate_block()
        self.check_balance(entity_a1.address, MIndiv1, '50', '0')
        self.check_orderbook_count(0, MIndiv1)


    def test_orderbook_with_multiple_main_properties(self):
        """
        1. Orderbook should be empty
        2. A1 starts with 50.0 MSC, 50 MIndiv1
        3. A1 offers 5.0 MSC for 5.0 MDiv1
        4. A1 offers 10.0 MSC for 20.0 MDiv1
        5. A1 offers 7.5 MSC for 40 MIndiv1
        6. A1 cancels 5.0 MSC for 5.0 MDiv1 (cancel-at-price)
        7. A1 offers 20 MIndiv1 for 7500.0 MSC
        8. A1 cancels 7.5 MSC for 40 MIndiv1 (cancel-at-price)
        9. A1 cancels 10.0 MSC for 20.0 MDiv1 (cancel-at-price)
        10. A1 cancels 20 MIndiv1 for 7500.0 MSC (cancel-at-price)

        After this test A1 should have the same balance as at the beginning."""
        entity_miner = self.entities[0]
        entity_a1 = self.entities[1]

        # 1. Orderbook should be empty
        self.check_orderbook_count(0, MSC, MDiv1)
        self.check_orderbook_count(0, MSC, MIndiv1)
        self.check_orderbook_count(0, MIndiv1, MSC)

        # 2. A1 starts with 50.0 MSC, 50 MIndiv1
        self.check_balance(entity_a1.address, MSC,     '50.00000000', '0.00000000')
        self.check_balance(entity_a1.address, MIndiv1, '50',          '0')

        # 3. A1 offers 5.0 MSC for 5.0 MDiv1
        entity_a1.trade('5.00000000', MSC, '5.00000000', MDiv1, ADD_1)
        self.generate_block()
        self.check_balance(entity_a1.address, MSC, '45.00000000', '5.00000000')
        self.check_orderbook_count(1, MSC, MDiv1)
        self.check_orderbook_count(0, MSC, MIndiv1)
        self.check_orderbook_count(0, MIndiv1, MSC)

        # 4. A1 offers 10.0 MSC for 20.0 MDiv1
        entity_a1.trade('10.00000000', MSC, '20.00000000', MDiv1, ADD_1)
        self.generate_block()
        self.check_balance(entity_a1.address, MSC, '35.00000000', '15.00000000')
        self.check_orderbook_count(2, MSC, MDiv1)
        self.check_orderbook_count(0, MSC, MIndiv1)
        self.check_orderbook_count(0, MIndiv1, MSC)

        # 5. A1 offers 7.5 MSC for 40 MIndiv1
        entity_a1.trade('7.50000000', MSC, '40', MIndiv1, ADD_1)
        self.generate_block()
        self.check_balance(entity_a1.address, MSC, '27.50000000', '22.50000000')
        self.check_orderbook_count(2, MSC, MDiv1)
        self.check_orderbook_count(1, MSC, MIndiv1)
        self.check_orderbook_count(0, MIndiv1, MSC)

        # 6. A1 cancels 5.0 MSC for 5.0 MDiv1 (cancel-at-price)
        entity_a1.trade('5.00000000', MSC, '5.00000000', MDiv1, CANCEL_2)
        self.generate_block()
        self.check_balance(entity_a1.address, MSC, '32.50000000', '17.50000000')
        self.check_orderbook_count(1, MSC, MDiv1)
        self.check_orderbook_count(1, MSC, MIndiv1)
        self.check_orderbook_count(0, MIndiv1, MSC)

        # 7. A1 offers 20 MIndiv1 for 7500.0 MSC
        entity_a1.trade('20', MIndiv1, '7500.00000000', MSC, ADD_1)
        self.generate_block()
        self.check_balance(entity_a1.address, MIndiv1, '30', '20')
        self.check_orderbook_count(1, MSC, MDiv1)
        self.check_orderbook_count(1, MSC, MIndiv1)
        self.check_orderbook_count(1, MIndiv1, MSC)

        # 8. A1 cancels 7.5 MSC for 40 MIndiv1 (cancel-at-price)
        entity_a1.trade('7.50000000', MSC, '40', MIndiv1, CANCEL_2)
        self.generate_block()
        self.check_balance(entity_a1.address, MSC, '40.00000000', '10.00000000')
        self.check_orderbook_count(1, MSC, MDiv1)
        self.check_orderbook_count(0, MSC, MIndiv1)
        self.check_orderbook_count(1, MIndiv1, MSC)

        # 9. A1 cancels 10.0 MSC for 20.0 MDiv1 (cancel-at-price)
        entity_a1.trade('10.00000000', MSC, '20.00000000', MDiv1, CANCEL_2)
        self.generate_block()
        self.check_balance(entity_a1.address, MSC, '50.00000000', '0.00000000')
        self.check_orderbook_count(0, MSC, MDiv1)
        self.check_orderbook_count(0, MSC, MIndiv1)
        self.check_orderbook_count(1, MIndiv1, MSC)

        # 10. A1 cancels 20 MIndiv1 for 7500.0 MSC (cancel-at-price)
        entity_a1.trade('20', MIndiv1, '7500.00000000', MSC, CANCEL_2)
        self.generate_block()
        self.check_balance(entity_a1.address, MIndiv1, '50', '0')
        self.check_orderbook_count(0, MSC, MDiv1)
        self.check_orderbook_count(0, MSC, MIndiv1)
        self.check_orderbook_count(0, MIndiv1, MSC)


    def test_orderbook_with_multiple_test_properties(self):
        """Tests a bunch of offers and cancellation via cancel-pair.

        1. Orderbook should be empty
        2. A1 starts with 50.0 TMSC and 50.0 TDiv1
        3. A1 creates 4 TMSC-TIndiv and 4 TMSC-TDiv1 offers
        4. A1 cancels all offers of TMSC-TIndiv1 and TMSC-TDiv1 (cancel-pair)
        5. A1 creates 7 TDiv1-TMSC and 5 TMSC-TDiv1 offers
        6. A1 cancels all offers of TDiv1-TMSC (cancel-pair)
        7. A1 cancels all offers of TMSC-TDiv (cancel-pair)

        After this test A1 should have the same balance as at the beginning."""
        entity_miner = self.entities[0]
        entity_a1 = self.entities[1]

        # 1. Orderbook should be empty
        self.check_orderbook_count(0, TMSC)
        self.check_orderbook_count(0, TIndiv1)
        self.check_orderbook_count(0, TDiv1)

        # 2. A1 starts with 50.0 TMSC and 50.0 TDiv1
        self.check_balance(entity_a1.address, TMSC,  '50.00000000', '0.00000000')
        self.check_balance(entity_a1.address, TDiv1, '50.00000000', '0.00000000')

        # 3. A1 creates 4 TMSC-TIndiv and 4 TMSC-TDiv1 offers
        entity_a1.trade('4.00000000', TMSC, '23', TIndiv1, ADD_1)
        entity_a1.trade('5.00000000', TMSC, '37', TIndiv1, ADD_1)
        entity_a1.trade('5.00000000', TMSC, '37', TIndiv1, ADD_1)
        entity_a1.trade('6.00000000', TMSC, '59', TIndiv1, ADD_1)
        entity_a1.trade('5.00000000', TMSC, '200.00000000', TDiv1, ADD_1)
        entity_a1.trade('5.00000000', TMSC, '200.00000000', TDiv1, ADD_1)
        entity_a1.trade('10.00000000', TMSC, '400.00000000', TDiv1, ADD_1)
        entity_a1.trade('10.00000000', TMSC, '800.00000000', TDiv1, ADD_1)
        self.generate_block()
        self.check_balance(entity_a1.address, TMSC, '0.00000000', '50.00000000')
        self.check_orderbook_count(8, TMSC)
        self.check_orderbook_count(4, TMSC, TIndiv1)
        self.check_orderbook_count(4, TMSC, TDiv1)

        # 4. A1 cancels all offers of TMSC-TIndiv1 and TMSC-TDiv1 (cancel-pair)
        entity_a1.trade('0.00000000', TMSC, '0', TIndiv1, CANCEL_3)
        entity_a1.trade('0.00000000', TMSC, '0.00000000', TDiv1, CANCEL_3)
        self.generate_block()
        self.check_balance(entity_a1.address, TMSC, '50.00000000', '0.00000000')
        self.check_orderbook_count(0, TMSC)
        self.check_orderbook_count(0, TMSC, TIndiv1)
        self.check_orderbook_count(0, TMSC, TDiv1)

        # 5. A1 creates 7 TDiv1-TMSC and 5 TMSC-TDiv1 offers
        entity_a1.trade('1.00000000', TDiv1, '10.00000000', TMSC, ADD_1)
        entity_a1.trade('1.00000000', TDiv1, '10.00000000', TMSC, ADD_1)
        entity_a1.trade('1.00000000', TDiv1, '10.00000000', TMSC, ADD_1)
        entity_a1.trade('1.00000000', TDiv1, '10.00000000', TMSC, ADD_1)
        entity_a1.trade('1.00000000', TDiv1, '10.00000000', TMSC, ADD_1)
        entity_a1.trade('1.00000000', TDiv1, '10.00000000', TMSC, ADD_1)
        entity_a1.trade('1.00000000', TDiv1, '10.00000000', TMSC, ADD_1)
        entity_a1.trade('1.00000000', TMSC, '0.50000000', TDiv1, ADD_1)
        entity_a1.trade('1.00000000', TMSC, '0.50000000', TDiv1, ADD_1)
        entity_a1.trade('1.00000000', TMSC, '0.50000000', TDiv1, ADD_1)
        entity_a1.trade('1.00000000', TMSC, '0.50000000', TDiv1, ADD_1)
        entity_a1.trade('1.00000000', TMSC, '0.50000000', TDiv1, ADD_1)
        self.generate_block()
        self.check_orderbook_count(7, TDiv1, TMSC)
        self.check_orderbook_count(5, TMSC, TDiv1)

        # 6. A1 cancels all offers of TDiv1-TMSC (cancel-pair)
        entity_a1.trade('0.00000000', TDiv1, '0.00000000', TMSC, CANCEL_3)
        self.generate_block()
        self.check_orderbook_count(0, TDiv1, TMSC)
        self.check_orderbook_count(5, TMSC, TDiv1)

        # 7. A1 cancels all offers of TMSC-TDiv (cancel-pair)
        entity_a1.trade('0.00000000', TMSC, '0.00000000', TDiv1, CANCEL_3)
        self.generate_block()
        self.check_orderbook_count(0, TDiv1, TMSC)
        self.check_orderbook_count(0, TMSC, TDiv1)

        self.check_balance(entity_a1.address, TMSC,  '50.00000000', '0.00000000')
        self.check_balance(entity_a1.address, TDiv1, '50.00000000', '0.00000000')


    def test_lookup_primary_first(self):
        """
        1. Orderbook should be empty
        2. A1 starts with 50.0 TMSC
        3. A1 offers TMSC for TIndiv1
        4. Cleanup (cancel-pair)

        After this test A1 should have the same balance as at the beginning."""
        entity_a1 = self.entities[1]

        # 1. Orderbook should be empty
        self.check_orderbook_count(0, TMSC)
        self.check_orderbook_count(0, TIndiv1)

        # 2. A1 starts with 50.0 TMSC
        self.check_balance(entity_a1.address, TMSC, '50.00000000', '0.00000000')

        # 3. A1 offers TMSC for TIndiv1
        entity_a1.trade('0.00000007', TMSC, '51137', TIndiv1, ADD_1)
        entity_a1.trade('0.00000011', TMSC, '97387', TIndiv1, ADD_1)
        self.generate_block()
        self.check_orderbook_count(2, TMSC)
        self.check_orderbook_count(2, TMSC, TIndiv1)

        # 4. Cleanup
        entity_a1.trade('9000', TIndiv1, '9000.00000000', TMSC, CANCEL_3)
        entity_a1.trade('9000000.00000000', TMSC, '9000', TIndiv1, CANCEL_3)
        self.generate_block()
        self.check_orderbook_count(0, TMSC)
        self.check_orderbook_count(0, TIndiv1)

        self.check_balance(entity_a1.address, TMSC,  '50.00000000', '0.00000000')


    def test_lookup_secondary_first(self):
        """
        1. Orderbook should be empty
        2. A1 starts with 50.0 TDiv1
        3. A1 offers TDiv1 for TMSC
        4. Cleanup (cancel-pair)

        After this test A1 should have the same balance as at the beginning."""

        entity_a1 = self.entities[1]

        # 1. Orderbook should be empty
        self.check_orderbook_count(0, TMSC)
        self.check_orderbook_count(0, TDiv1)

        # 2. A1 starts with 50.0 TDiv1
        self.check_balance(entity_a1.address, TDiv1, '50.00000000', '0.00000000')

        # 3. A1 offers TDiv1 for TMSC
        entity_a1.trade('15.00000000', TDiv1, '0.00000015', TMSC, ADD_1)
        entity_a1.trade('30.00000000', TDiv1, '0.00000005', TMSC, ADD_1)
        self.generate_block()
        self.check_orderbook_count(2, TDiv1)
        self.check_orderbook_count(2, TDiv1, TMSC)

        # 5. Cleanup
        entity_a1.trade('0.00000001', TDiv1, '0.00000001', TMSC, CANCEL_3)
        entity_a1.trade('0.00000001', TMSC, '0.00000001', TDiv1, CANCEL_3)
        self.generate_block()
        self.check_orderbook_count(0, TMSC)
        self.check_orderbook_count(0, TIndiv1)
        self.check_balance(entity_a1.address, TDiv1, '50.00000000', '0.00000000')


    def test_cancel_pair_msc_indiv_sane_sane(self):
        """
        1. Orderbook should be empty
        2. ...

        After this test A1 should have the same balance as at the beginning."""
        entity_a1 = self.entities[1]

        # 1. Orderbook should be empty
        self.check_orderbook_count(0, MSC)
        self.check_orderbook_count(0, MIndiv1)

        # 2. A1 starts with 50.0 MSC
        self.check_balance(entity_a1.address, MSC, '50.00000000', '0.00000000')

        # 3. A1 offers MSC for MIndiv1
        entity_a1.trade('15.00000000', MSC, '15', MIndiv1, ADD_1)
        entity_a1.trade('30.00000000', MSC, '32', MIndiv1, ADD_1)
        self.generate_block()
        self.check_orderbook_count(2, MSC, MIndiv1)
        self.check_balance(entity_a1.address, MSC, '5.00000000', '45.00000000')

        # 5. A1 cancels with cancel-pair
        txid = entity_a1.trade('0.00000001', MSC, '1', MIndiv1, CANCEL_3)
        self.generate_block()
        self.check_orderbook_count(0, MSC, MIndiv1)
        self.check_balance(entity_a1.address, MSC, '50.00000000', '0.00000000')


    def test_cancel_pair_msc_indiv_zero_sane(self):
        """
        1. Orderbook should be empty
        2. ...

        After this test A1 should have the same balance as at the beginning."""
        entity_a1 = self.entities[1]

        # 1. Orderbook should be empty
        self.check_orderbook_count(0, MSC)
        self.check_orderbook_count(0, MIndiv1)

        # 2. A1 starts with 50.0 MSC
        self.check_balance(entity_a1.address, MSC, '50.00000000', '0.00000000')

        # 3. A1 offers MSC for MIndiv1
        entity_a1.trade('15.00000000', MSC, '15', MIndiv1, ADD_1)
        entity_a1.trade('30.00000000', MSC, '32', MIndiv1, ADD_1)
        self.generate_block()
        self.check_orderbook_count(2, MSC, MIndiv1)
        self.check_balance(entity_a1.address, MSC, '5.00000000', '45.00000000')

        # 5. A1 cancels with cancel-pair
        txid = entity_a1.trade('0.00000000', MSC, '1', MIndiv1, CANCEL_3)
        self.generate_block()
        self.check_orderbook_count(0, MSC, MIndiv1)
        self.check_balance(entity_a1.address, MSC, '50.00000000', '0.00000000')


    def test_cancel_pair_msc_indiv_sane_zero(self):
        """
        1. Orderbook should be empty
        2. ...

        After this test A1 should have the same balance as at the beginning."""
        entity_a1 = self.entities[1]

        # 1. Orderbook should be empty
        self.check_orderbook_count(0, MSC)
        self.check_orderbook_count(0, MIndiv1)

        # 2. A1 starts with 50.0 MSC
        self.check_balance(entity_a1.address, MSC, '50.00000000', '0.00000000')

        # 3. A1 offers MSC for MIndiv1
        entity_a1.trade('15.00000000', MSC, '15', MIndiv1, ADD_1)
        entity_a1.trade('30.00000000', MSC, '32', MIndiv1, ADD_1)
        self.generate_block()
        self.check_orderbook_count(2, MSC, MIndiv1)
        self.check_balance(entity_a1.address, MSC, '5.00000000', '45.00000000')

        # 5. A1 cancels with cancel-pair
        txid = entity_a1.trade('0.00000001', MSC, '0', MIndiv1, CANCEL_3)
        self.generate_block()
        self.check_orderbook_count(0, MSC, MIndiv1)
        self.check_balance(entity_a1.address, MSC, '50.00000000', '0.00000000')


    def test_cancel_pair_msc_indiv_zero_zero(self):
        """
        1. Orderbook should be empty
        2. ...

        After this test A1 should have the same balance as at the beginning."""
        entity_a1 = self.entities[1]

        # 1. Orderbook should be empty
        self.check_orderbook_count(0, MSC)
        self.check_orderbook_count(0, MIndiv1)

        # 2. A1 starts with 50.0 MSC
        self.check_balance(entity_a1.address, MSC, '50.00000000', '0.00000000')

        # 3. A1 offers MSC for MIndiv1
        entity_a1.trade('15.00000000', MSC, '15', MIndiv1, ADD_1)
        entity_a1.trade('30.00000000', MSC, '32', MIndiv1, ADD_1)
        self.generate_block()
        self.check_orderbook_count(2, MSC, MIndiv1)
        self.check_balance(entity_a1.address, MSC, '5.00000000', '45.00000000')

        # 5. A1 cancels with cancel-pair
        txid = entity_a1.trade('0.00000000', MSC, '0', MIndiv1, CANCEL_3)
        self.generate_block()
        self.check_orderbook_count(0, MSC, MIndiv1)
        self.check_balance(entity_a1.address, MSC, '50.00000000', '0.00000000')


    def test_cancel_pair_indiv_msc_sane_sane(self):
        """
        1. Orderbook should be empty
        2. ...

        After this test A1 should have the same balance as at the beginning."""
        entity_a1 = self.entities[1]

        # 1. Orderbook should be empty
        self.check_orderbook_count(0, MSC)
        self.check_orderbook_count(0, MIndiv1)

        # 2. A1 starts with 50 MIndiv1
        self.check_balance(entity_a1.address, MIndiv1, '50', '0')

        # 3. A1 offers MIndiv1 for MIndiv1
        entity_a1.trade('15', MIndiv1, '15.00000000', MSC, ADD_1)
        entity_a1.trade('30', MIndiv1, '32.00000000', MSC, ADD_1)
        self.generate_block()
        self.check_orderbook_count(2, MIndiv1, MSC)
        self.check_balance(entity_a1.address, MIndiv1, '5', '45')

        # 5. A1 cancels with cancel-pair
        txid = entity_a1.trade('1', MIndiv1, '0.00000001', MSC, CANCEL_3)
        self.generate_block()
        self.check_orderbook_count(0, MIndiv1, MSC)
        self.check_balance(entity_a1.address, MIndiv1, '50', '0')


    def test_cancel_pair_indiv_msc_zero_sane(self):
        """
        1. Orderbook should be empty
        2. ...

        After this test A1 should have the same balance as at the beginning."""
        entity_a1 = self.entities[1]

        # 1. Orderbook should be empty
        self.check_orderbook_count(0, MSC)
        self.check_orderbook_count(0, MIndiv1)

        # 2. A1 starts with 50 MIndiv1
        self.check_balance(entity_a1.address, MIndiv1, '50', '0')

        # 3. A1 offers MIndiv1 for MIndiv1
        entity_a1.trade('15', MIndiv1, '15.00000000', MSC, ADD_1)
        entity_a1.trade('30', MIndiv1, '32.00000000', MSC, ADD_1)
        self.generate_block()
        self.check_orderbook_count(2, MIndiv1, MSC)
        self.check_balance(entity_a1.address, MIndiv1, '5', '45')

        # 5. A1 cancels with cancel-pair
        txid = entity_a1.trade('0', MIndiv1, '0.00000001', MSC, CANCEL_3)
        self.generate_block()
        self.check_orderbook_count(0, MIndiv1, MSC)
        self.check_balance(entity_a1.address, MIndiv1, '50', '0')


    def test_cancel_pair_indiv_msc_sane_zero(self):
        """
        1. Orderbook should be empty
        2. ...

        After this test A1 should have the same balance as at the beginning."""
        entity_a1 = self.entities[1]

        # 1. Orderbook should be empty
        self.check_orderbook_count(0, MSC)
        self.check_orderbook_count(0, MIndiv1)

        # 2. A1 starts with 50 MIndiv1
        self.check_balance(entity_a1.address, MIndiv1, '50', '0')

        # 3. A1 offers MIndiv1 for MIndiv1
        entity_a1.trade('15', MIndiv1, '15.00000000', MSC, ADD_1)
        entity_a1.trade('30', MIndiv1, '32.00000000', MSC, ADD_1)
        self.generate_block()
        self.check_orderbook_count(2, MIndiv1, MSC)
        self.check_balance(entity_a1.address, MIndiv1, '5', '45')

        # 5. A1 cancels with cancel-pair
        txid = entity_a1.trade('1', MIndiv1, '0.00000000', MSC, CANCEL_3)
        self.generate_block()
        self.check_orderbook_count(0, MIndiv1, MSC)
        self.check_balance(entity_a1.address, MIndiv1, '50', '0')


    def test_cancel_pair_indiv_msc_zero_zero(self):
        """
        1. Orderbook should be empty
        2. ...

        After this test A1 should have the same balance as at the beginning."""
        entity_a1 = self.entities[1]

        # 1. Orderbook should be empty
        self.check_orderbook_count(0, MSC)
        self.check_orderbook_count(0, MIndiv1)

        # 2. A1 starts with 50 MIndiv1
        self.check_balance(entity_a1.address, MIndiv1, '50', '0')

        # 3. A1 offers MIndiv1 for MIndiv1
        entity_a1.trade('15', MIndiv1, '15.00000000', MSC, ADD_1)
        entity_a1.trade('30', MIndiv1, '32.00000000', MSC, ADD_1)
        self.generate_block()
        self.check_orderbook_count(2, MIndiv1, MSC)
        self.check_balance(entity_a1.address, MIndiv1, '5', '45')

        # 5. A1 cancels with cancel-pair
        txid = entity_a1.trade('0', MIndiv1, '0.00000000', MSC, CANCEL_3)
        self.generate_block()
        self.check_orderbook_count(0, MIndiv1, MSC)
        self.check_balance(entity_a1.address, MIndiv1, '50', '0')


    def test_cancel_pair_msc_div_sane_sane(self):
        """
        1. Orderbook should be empty
        2. ...

        After this test A1 should have the same balance as at the beginning."""
        entity_a1 = self.entities[1]

        # 1. Orderbook should be empty
        self.check_orderbook_count(0, MSC)
        self.check_orderbook_count(0, MDiv1)

        # 2. A1 starts with 50.0 MSC
        self.check_balance(entity_a1.address, MSC, '50.00000000', '0.00000000')

        # 3. A1 offers MSC for MIndiv1
        entity_a1.trade('15.00000000', MSC, '15.00000000', MDiv1, ADD_1)
        entity_a1.trade('30.00000000', MSC, '32.00000000', MDiv1, ADD_1)
        self.generate_block()
        self.check_orderbook_count(2, MSC, MDiv1)
        self.check_balance(entity_a1.address, MSC, '5.00000000', '45.00000000')

        # 5. A1 cancels with cancel-pair
        txid = entity_a1.trade('0.00000001', MSC, '0.00000001', MDiv1, CANCEL_3)
        self.generate_block()
        self.check_orderbook_count(0, MSC, MDiv1)
        self.check_balance(entity_a1.address, MSC, '50.00000000', '0.00000000')


    def test_cancel_pair_of_several_combinations(self):
        """
        1. Orderbook should be empty
        2. A1 creates offers to link available properties
        3. A1 cancels all pairs until there no more left (cancel-pair)

        After this test A1 should have the same balance as at the beginning."""
        entity_miner = self.entities[0]
        entity_a1 = self.entities[1]

        # 1. Orderbook should be empty
        self.check_orderbook_count(0, MSC)
        self.check_orderbook_count(0, TMSC)
        self.check_orderbook_count(0, MIndiv1)
        self.check_orderbook_count(0, MDiv1)
        self.check_orderbook_count(0, TIndiv1)
        self.check_orderbook_count(0, TDiv1)

        # 2. A1 creates offers to link available properties
        self.check_balance(entity_a1.address, MSC,     '50.00000000', '0.00000000')  # SP 1
        self.check_balance(entity_a1.address, TMSC,    '50.00000000', '0.00000000')  # SP 2
        self.check_balance(entity_a1.address, MIndiv1, '50',          '0')           # SP 3
        self.check_balance(entity_a1.address, MDiv1,    '0.00000000', '0.00000000')  # SP 4
        self.check_balance(entity_a1.address, TIndiv1,  '0',          '0')           # SP 2147483651
        self.check_balance(entity_a1.address, TDiv1,   '50.00000000', '0.00000000')  # SP 2147483655

        entity_a1.trade('10.10101010', TMSC, '9999.99999999', TDiv1, ADD_1)
        entity_a1.trade('15.02020202', TMSC, '9999.99999998', TDiv1, ADD_1)

        entity_a1.trade('3.10010000', TDiv1, '1.11', TMSC, ADD_1)
        entity_a1.trade('5.20002000', TDiv1, '1.12', TMSC, ADD_1)
        entity_a1.trade('7.30000300', TDiv1, '1.13', TMSC, ADD_1)

        entity_a1.trade('1.00000001', MSC, '100.00000000', MDiv1, ADD_1)
        entity_a1.trade('1.00000002', MSC, '300.00000000', MDiv1, ADD_1)
        entity_a1.trade('1.00000003', MSC, '900.00000000', MDiv1, ADD_1)
        entity_a1.trade('1.00000004', MSC, '1300.00000000', MDiv1, ADD_1)

        entity_a1.trade('2.10000000', MSC, '1', MIndiv1, ADD_1)
        entity_a1.trade('2.20000000', MSC, '1', MIndiv1, ADD_1)
        entity_a1.trade('2.30000000', MSC, '1', MIndiv1, ADD_1)
        entity_a1.trade('2.40000000', MSC, '1', MIndiv1, ADD_1)
        entity_a1.trade('2.50000000', MSC, '1', MIndiv1, ADD_1)

        entity_a1.trade('1', MIndiv1, '3.00000000',  MSC, ADD_1)
        entity_a1.trade('2', MIndiv1, '7.00000000',  MSC, ADD_1)
        entity_a1.trade('3', MIndiv1, '11.00000000', MSC, ADD_1)
        entity_a1.trade('4', MIndiv1, '17.00000000', MSC, ADD_1)
        entity_a1.trade('5', MIndiv1, '23.00000000', MSC, ADD_1)
        entity_a1.trade('6', MIndiv1, '29.00000000', MSC, ADD_1)

        entity_a1.trade('0.10000001', TMSC, '1', TIndiv1, ADD_1)
        entity_a1.trade('0.20000002', TMSC, '10', TIndiv1, ADD_1)
        entity_a1.trade('0.30000003', TMSC, '100', TIndiv1, ADD_1)
        entity_a1.trade('0.40000004', TMSC, '1000', TIndiv1, ADD_1)
        entity_a1.trade('0.50000005', TMSC, '10000', TIndiv1, ADD_1)
        entity_a1.trade('0.60000006', TMSC, '100000', TIndiv1, ADD_1)
        entity_a1.trade('0.70000007', TMSC, '1000000', TIndiv1, ADD_1)

        self.generate_block()
        self.check_orderbook_count(2, TMSC, TDiv1)
        self.check_orderbook_count(3, TDiv1, TMSC)
        self.check_orderbook_count(4, MSC, MDiv1)
        self.check_orderbook_count(5, MSC, MIndiv1)
        self.check_orderbook_count(6, MIndiv1, MSC)
        self.check_orderbook_count(7, TMSC, TIndiv1)

        # TODO: clarify if inverted properties should be included
        self.check_orderbook_count(9, MSC)      # SP 1
        self.check_orderbook_count(9, TMSC)     # SP 2
        self.check_orderbook_count(6, MIndiv1)  # SP 3
        self.check_orderbook_count(0, MDiv1)    # SP 4
        self.check_orderbook_count(0, TIndiv1)  # SP 2147483651
        self.check_orderbook_count(3, TDiv1)    # SP 2147483655

        # This should have no effect, because there is no link in this direction
        entity_a1.trade('0.00000000', MDiv1, '0.00000000', MSC, CANCEL_3)
        entity_a1.trade('7535577', TIndiv1, '0.00000000', TMSC, CANCEL_3)

        self.generate_block()
        self.check_orderbook_count(4, MSC, MDiv1)
        self.check_orderbook_count(0, MDiv1, MSC)
        self.check_orderbook_count(7, TMSC, TIndiv1)
        self.check_orderbook_count(0, TIndiv1, TMSC)

        # 3. A1 cancels all pairs until there no more left (cancel-pair)
        entity_a1.trade('10.00000000', MSC, '0.12345678', MDiv1, CANCEL_3)
        entity_a1.trade('0.00000000', TMSC, '99999999', TIndiv1, CANCEL_3)

        self.generate_block()
        self.check_orderbook_count(2, TMSC, TDiv1)
        self.check_orderbook_count(3, TDiv1, TMSC)
        self.check_orderbook_count(0, MSC, MDiv1)     # updated
        self.check_orderbook_count(5, MSC, MIndiv1)
        self.check_orderbook_count(6, MIndiv1, MSC)
        self.check_orderbook_count(0, TMSC, TIndiv1)  # updated

        entity_a1.trade('0.00000001', TDiv1, '92233720368.54775807', TMSC, CANCEL_3)
        entity_a1.trade('1', MIndiv1, '92233720368.54775807', MSC, CANCEL_3)

        self.generate_block()
        self.check_orderbook_count(2, TMSC, TDiv1)
        self.check_orderbook_count(0, TDiv1, TMSC)    # updated
        self.check_orderbook_count(0, MSC, MDiv1)
        self.check_orderbook_count(5, MSC, MIndiv1)
        self.check_orderbook_count(0, MIndiv1, MSC)   # updated
        self.check_orderbook_count(0, TMSC, TIndiv1)

        entity_a1.trade('92233720368.54775807', TMSC, '92233720368.54775807', TDiv1, CANCEL_3)

        self.generate_block()
        self.check_orderbook_count(0, TMSC, TDiv1)    # updated
        self.check_orderbook_count(0, TDiv1, TMSC)
        self.check_orderbook_count(0, MSC, MDiv1)
        self.check_orderbook_count(5, MSC, MIndiv1)
        self.check_orderbook_count(0, MIndiv1, MSC)
        self.check_orderbook_count(0, TMSC, TIndiv1)

        entity_a1.trade('92233720368.54775807', MSC, '9223372036854775807', MIndiv1, CANCEL_3)

        self.generate_block()
        self.check_orderbook_count(0, TMSC, TDiv1)
        self.check_orderbook_count(0, TDiv1, TMSC)
        self.check_orderbook_count(0, MSC, MDiv1)
        self.check_orderbook_count(0, MSC, MIndiv1)   # updated
        self.check_orderbook_count(0, MIndiv1, MSC)
        self.check_orderbook_count(0, TMSC, TIndiv1)

        self.check_orderbook_count(0, MSC)
        self.check_orderbook_count(0, TMSC)
        self.check_orderbook_count(0, MIndiv1)
        self.check_orderbook_count(0, MDiv1)
        self.check_orderbook_count(0, TIndiv1)
        self.check_orderbook_count(0, TDiv1)

        # Original state
        self.check_balance(entity_a1.address, MSC,     '50.00000000', '0.00000000')  # SP 1
        self.check_balance(entity_a1.address, TMSC,    '50.00000000', '0.00000000')  # SP 2
        self.check_balance(entity_a1.address, MIndiv1, '50',          '0')           # SP 3
        self.check_balance(entity_a1.address, MDiv1,    '0.00000000', '0.00000000')  # SP 4
        self.check_balance(entity_a1.address, TIndiv1,  '0',          '0')           # SP 2147483651
        self.check_balance(entity_a1.address, TDiv1,   '50.00000000', '0.00000000')  # SP 2147483655


if __name__ == '__main__':
    MetaDexCancelPairAndLookupTest().main()
