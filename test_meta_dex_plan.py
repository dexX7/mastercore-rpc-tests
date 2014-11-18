#!/usr/bin/python
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

from framework_extension import MasterTestFramework
from framework_entity import TestEntity

# Helper

BTC = 0
MSC = 1
TMSC = 2
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


class MetaDexPlanTest(MasterTestFramework):

    def run_test(self):
        self.entities = [TestEntity(node) for node in self.nodes]

        self.prepare_funding()
        self.prepare_properties()
        self.initial_distribution()

        self.test_invalid_version_other_than_zero()
        self.test_invalid_action()
        self.test_invalid_cancel_everything_no_active_offers()
        self.test_invalid_cancel_pair_no_active_offers()
        self.test_invalid_cancel_no_active_offers()
        self.test_invalid_add_same_currency()
        self.test_invalid_add_zero_amount()
        self.test_invalid_add_bitcoin()
        self.test_invalid_add_cross_ecosystem()
        self.test_invalid_insufficient_balance()
        self.test_invalid_amount_too_large()
        self.test_invalid_amount_too_large_raw()
        self.test_invalid_amount_negative()
        self.test_invalid_negative_zero()

        self.test_new_orders_for_divisible()
        self.test_match_divisible_at_same_unit_price()
        self.test_match_divisible_at_better_unit_price()
        self.test_match_divisible_with_three()

        # TODO: split into several sub test files


    def prepare_funding(self):
        entity_miner = self.entities[0]
        entity_a1 = self.entities[1]
        entity_a2 = self.entities[2]
        entity_a3 = self.entities[3]

        entity_miner.send_bitcoins(entity_miner.address)
        entity_miner.send_bitcoins(entity_a1.address, 50.0)
        entity_miner.send_bitcoins(entity_a2.address, 50.0)
        entity_miner.send_bitcoins(entity_a3.address, 50.0)
        entity_miner.purchase_mastercoins(500.0)

        self.generate_block()
        self.check_balance(entity_miner.address, MSC, '50000.00000000', '0.00000000')
        self.check_balance(entity_miner.address, TMSC, '50000.00000000', '0.00000000')


    def prepare_properties(self):
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

        self.generate_block()
        self.check_balance(addr, TIndiv1, '9223372036854775807', '0')
        self.check_balance(addr, TIndiv2, '9223372036854775807', '0')
        self.check_balance(addr, TIndiv3, '9223372036854775807', '0')
        self.check_balance(addr, TIndivMax, '9223372036854775807', '0')
        self.check_balance(addr, TDiv1, '92233720368.54775807', '0.00000000')
        self.check_balance(addr, TDiv2, '92233720368.54775807', '0.00000000')
        self.check_balance(addr, TDiv3, '92233720368.54775807', '0.00000000')
        self.check_balance(addr, TDivMax, '92233720368.54775807', '0.00000000')


    def initial_distribution(self):
        entity_miner = self.entities[0]
        entity_a1 = self.entities[1]
        entity_a2 = self.entities[2]
        entity_a3 = self.entities[3]

        entity_miner.send(entity_a1.address, TDiv1, '100.00000000')
        entity_miner.send(entity_a1.address, TIndiv1, '1000')
        entity_miner.send(entity_a1.address, TMSC, '150.00000000')

        entity_miner.send(entity_a2.address, TDiv1, '50.00000000')
        entity_miner.send(entity_a2.address, TDiv2, '200.00000000')
        entity_miner.send(entity_a2.address, TIndiv2, '2000')
        entity_miner.send(entity_a2.address, TDiv3, '200.00000000')
        entity_miner.send(entity_a2.address, TIndiv3, '200')
        entity_miner.send(entity_a2.address, TMSC, '50.00000000')

        entity_miner.send(entity_a3.address, TMSC, '25.00000000')
        entity_miner.send(entity_a3.address, TIndivMax, '9223372036854775807')
        entity_miner.send(entity_a3.address, TDivMax, '92233720368.54775807')
        entity_miner.send(entity_a3.address, TDiv3, '200.00000000')
        entity_miner.send(entity_a3.address, TIndiv3, '200')

        self.generate_block()

        self.check_balance(entity_a1.address, TMSC, '150.00000000', '0.00000000')
        self.check_balance(entity_a2.address, TMSC, '50.00000000', '0.00000000')
        self.check_balance(entity_a3.address, TMSC, '25.00000000', '0.00000000')

        self.check_balance(entity_a1.address, TDiv1, '100.00000000', '0.00000000')
        self.check_balance(entity_a2.address, TDiv1, '50.00000000', '0.00000000')
        self.check_balance(entity_a3.address, TDiv1, '0.00000000', '0.00000000')

        self.check_balance(entity_a1.address, TDiv2, '0.00000000', '0.00000000')
        self.check_balance(entity_a2.address, TDiv2, '200.00000000', '0.00000000')
        self.check_balance(entity_a3.address, TDiv2, '0.00000000', '0.00000000')

        self.check_balance(entity_a1.address, TDiv3, '0.00000000', '0.00000000')
        self.check_balance(entity_a2.address, TDiv3, '200.00000000', '0.00000000')
        self.check_balance(entity_a3.address, TDiv3, '200.00000000', '0.00000000')

        self.check_balance(entity_a1.address, TDivMax, '0.00000000', '0.00000000')
        self.check_balance(entity_a2.address, TDivMax, '0.00000000', '0.00000000')
        self.check_balance(entity_a3.address, TDivMax, '92233720368.54775807', '0.00000000')

        self.check_balance(entity_a1.address, TIndiv1, '1000', '0')
        self.check_balance(entity_a2.address, TIndiv1, '0', '0')
        self.check_balance(entity_a3.address, TIndiv1, '0', '0')

        self.check_balance(entity_a1.address, TIndiv2, '0', '0')
        self.check_balance(entity_a2.address, TIndiv2, '2000', '0')
        self.check_balance(entity_a3.address, TIndiv2, '0', '0')

        self.check_balance(entity_a1.address, TIndiv3, '0', '0')
        self.check_balance(entity_a2.address, TIndiv3, '200', '0')
        self.check_balance(entity_a3.address, TIndiv3, '200', '0')

        self.check_balance(entity_a1.address, TIndivMax, '0', '0')
        self.check_balance(entity_a2.address, TIndivMax, '0', '0')
        self.check_balance(entity_a3.address, TIndivMax, '9223372036854775807', '0')


    def check_invalid(self, reason='none provided', txid=''):
        tx_rejected = (len(txid) != 64 or txid == '0000000000000000000000000000000000000000000000000000000000000000')
        if tx_rejected:
            print('Transaction rejected (reason: %s) ... OK' % (reason,))
            return True

        self.generate_block()
        tx = self.nodes[0].gettransaction_MP(txid)
        tx_invalid = (not tx['valid'])
        if tx_invalid:
            print('Transaction invalid (reason: %s) ... OK' % (reason,))
            return True

        # Otherwise the transaction is valid and therefore this check failed
        raise AssertionError(
            '\nExpected transaction to be invalid (reason: %s):\nTransaction hash: %s\n%s\n%s\n' % (
                reason, txid, str(tx), self.nodes[0].getrawtransaction(txid),))


    # A20
    def test_invalid_version_other_than_zero(self):
        entity_a1 = self.entities[1]

        # TODO: depreciate transaction version tests, once new version of transaction is live

        #                    entity_a1.trade('2.00000000', TMSC, '2.00000000', TDiv1, ADD_1) with "version = 1"
        try:    txid_a20_1 = entity_a1.node.sendrawtx_MP(entity_a1.address,
                                                         '0001001500000002000000000bebc20080000007000000000bebc20001')
        except: txid_a20_1 = '0'
        self.check_invalid('tx version > 0', txid_a20_1)

        #                    entity_a1.trade('2.00000000', TMSC, '2.00000000', TDiv1, CANCEL_2) with "version = 1"
        try:    txid_a20_2 = entity_a1.node.sendrawtx_MP(entity_a1.address,
                                                         '0001001500000002000000000bebc20080000007000000000bebc20002')
        except: txid_a20_2 = '0'
        self.check_invalid('tx version > 0', txid_a20_2)

        #                    entity_a1.trade('2.00000000', TMSC, '2.00000000', TDiv1, CANCEL_3) with "version = 1"
        try:    txid_a20_3 = entity_a1.node.sendrawtx_MP(entity_a1.address,
                                                         '0001001500000002000000000bebc20080000007000000000bebc20003')
        except: txid_a20_3 = '0'
        self.check_invalid('tx version > 0', txid_a20_3)

        #                    entity_a1.trade('2.00000000', TMSC, '2.00000000', TDiv1, CANCEL_4) with "version = 1"
        try:    txid_a20_4 = entity_a1.node.sendrawtx_MP(entity_a1.address,
                                                         '0001001500000002000000000bebc20080000007000000000bebc20004')
        except: txid_a20_4 = '0'
        self.check_invalid('tx version > 0', txid_a20_4)


    # A21-22
    def test_invalid_action(self):
        entity_a1 = self.entities[1]

        try:    txid_a21 = entity_a1.trade('2.00000000', TMSC, '2.00000000', TDiv1, 0)
        except: txid_a21 = '0'
        self.check_invalid('invalid action (0)', txid_a21)

        try:    txid_a22 = entity_a1.trade('2.00000000', TMSC, '2.00000000', TDiv1, 5)
        except: txid_a22 = '0'
        self.check_invalid('invalid action (5)', txid_a22)


    # A23
    def test_invalid_cancel_everything_no_active_offers(self):
        entity_a1 = self.entities[1]

        try:    txid_a23_1 = entity_a1.trade('2.00000000', TMSC, '2.00000000', TDiv1, 4)
        except: txid_a23_1 = '0'
        self.check_invalid('no active orders, cancel-everything, positive amounts, test ecosystem', txid_a23_1)

        try:    txid_a23_2 = entity_a1.trade('2.00000000', TMSC, '2.00000000', TMSC, 4)
        except: txid_a23_2 = '0'
        self.check_invalid('no active orders, cancel-everything, positive amounts, TMSC, TMSC (!)', txid_a23_2)

        try:    txid_a23_3 = entity_a1.trade('2.00000000', MSC, '2.00000000', TMSC, 4)
        except: txid_a23_3 = '0'
        self.check_invalid('no active orders, cancel-everything, positive amounts, cross ecosystem (!)', txid_a23_3)

        try:    txid_a23_4 = entity_a1.trade('2.00000000', 67, '2.00000000', 68, 4)
        except: txid_a23_4 = '0'
        self.check_invalid('no active orders, cancel-everything, positive amounts, non-existing pair (!)', txid_a23_4)

        try:    txid_a23_5 = entity_a1.trade('0.00000000', TMSC, '0.00000000', TDiv1, 4)
        except: txid_a23_5 = '0'
        self.check_invalid('no active orders, cancel-everything, zero amounts (!), test ecosystem', txid_a23_5)

        try:    txid_a23_6 = entity_a1.trade('0.00000000', TMSC, '0.00000000', TMSC, 4)
        except: txid_a23_6 = '0'
        self.check_invalid('no active orders, cancel-everything, zero amounts (!), TMSC, TMSC (!)', txid_a23_6)

        try:    txid_a23_7 = entity_a1.trade('0.00000000', MSC, '0.00000000', TMSC, 4)
        except: txid_a23_7 = '0'
        self.check_invalid('no active orders, cancel-everything, zero amounts (!), cross ecosystem (!)', txid_a23_7)

        try:    txid_a23_8 = entity_a1.trade('0.00000000', 67, '0.00000000', 68, 4)
        except: txid_a23_8 = '0'
        self.check_invalid('no active orders, cancel-everything, zero amounts (!), non-existing pair (!)', txid_a23_8)


    # A24-25
    def test_invalid_cancel_pair_no_active_offers(self):
        entity_a1 = self.entities[1]

        try:    txid_a24 = entity_a1.trade('2.00000000', TMSC, '2.00000000', TDiv1, 3)
        except: txid_a24 = '0'
        self.check_invalid('no active orders for currency pair', txid_a24)

        try:    txid_a25 = entity_a1.trade('2.00000000', TDiv1, '2.00000000', TMSC, 3)
        except: txid_a25 = '0'
        self.check_invalid('no active orders for currency pair', txid_a25)


    # A26-27
    def test_invalid_cancel_no_active_offers(self):
        entity_a1 = self.entities[1]

        try:    txid_a26 = entity_a1.trade('2.00000000', TDiv2, '2.00000000', TMSC, 2)
        except: txid_a26 = '0'
        self.check_invalid('no active orders for currency pair and price', txid_a26)

        try:    txid_a27 = entity_a1.trade('2.00000000', TMSC, '2.00000000', TDiv2, 2)
        except: txid_a27 = '0'
        self.check_invalid('no active orders for currency pair and price', txid_a27)


    # A28-29
    def test_invalid_add_same_currency(self):
        entity_a1 = self.entities[1]

        try:    txid_a28 = entity_a1.trade('1.00000000', TDiv1, '2.00000000', TDiv1, 1)
        except: txid_a28 = '0'
        self.check_invalid('same currency (and neither is TMSC)', txid_a28)

        try:    txid_a29 = entity_a1.trade('1.00000000', TMSC, '2.00000000', TMSC, 1)
        except: txid_a29 = '0'
        self.check_invalid('same currency', txid_a29)


    # A30-31
    def test_invalid_add_zero_amount(self):
        entity_a1 = self.entities[1]

        try:    txid_a30 = entity_a1.trade('0.00000000', TDiv1, '1.00000000', TMSC, 1)
        except: txid_a30 = '0'
        self.check_invalid('amount for sale is 0.0', txid_a30)

        try:    txid_a31 = entity_a1.trade('1.00000000', TDiv1, '0.00000000', TMSC, 1)
        except: txid_a31 = '0'
        self.check_invalid('amount desired is 0.0', txid_a31)


    # A32-33
    def test_invalid_add_bitcoin(self):
        entity_a1 = self.entities[1]

        try:    txid_a32 = entity_a1.trade('1.00000000', BTC, '1.00000000', TMSC, 1)
        except: txid_a32 = '0'
        self.check_invalid('desired property is bitcoin', txid_a32)

        try:    txid_a33 = entity_a1.trade('1.00000000', TMSC, '1.00000000', BTC, 1)
        except: txid_a33 = '0'
        self.check_invalid('property for sale is bitcoin', txid_a33)


    # A34-35
    def test_invalid_add_cross_ecosystem(self):
        entity_a1 = self.entities[1]

        try:    txid_a34 = entity_a1.trade('1.00000000', MSC, '1.00000000', TDiv1, 1)
        except: txid_a34 = '0'
        self.check_invalid('cross ecosystem (main, test) (MSC, TDiv1)', txid_a34)

        try:    txid_a35 = entity_a1.trade('1.00000000', TDiv1, '1.00000000', MSC, 1)
        except: txid_a35 = '0'
        self.check_invalid('cross ecosystem (test, main) (MSC, TDiv1)', txid_a35)


    # A37-40
    def test_invalid_insufficient_balance(self):
        entity_a1 = self.entities[1]

        try:    txid_a37 = entity_a1.trade('1', TIndiv2, '1.00000000', TMSC, 1)
        except: txid_a37 = '0'
        self.check_invalid('A1 does not have any TIndiv2', txid_a37)

        try:    txid_a38 = entity_a1.trade('2001', TIndiv1, '1.00000000', TMSC, 1)
        except: txid_a38 = '0'
        self.check_invalid('A1 does not have enough TIndiv1', txid_a38)

        try:    txid_a39 = entity_a1.trade('1.00000000', TDiv2, '1.00000000', TMSC, 1)
        except: txid_a39 = '0'
        self.check_invalid('A1 does not have any TDiv2', txid_a39)

        try:    txid_a40 = entity_a1.trade('100.00000001', TDiv1, '1.00000000', TMSC, 1)
        except: txid_a40 = '0'
        self.check_invalid('A1 does not have enough TDiv1', txid_a40)


    # A42-47
    def test_invalid_amount_too_large(self):
        entity_a1 = self.entities[1]
        entity_a3 = self.entities[3]

        # TODO: testplan provided 92233720368.54780000 (max + x) and 9223372036854770,001 (within range)

        try:    txid_a42 = entity_a1.trade('0.00000001', TDiv1, '92233720368.54780000', TMSC, 1)
        except: txid_a42 = '0'
        self.check_invalid('amount desired is too large (92233720368.54780000 TMSC)', txid_a42)

        try:    txid_a43 = entity_a3.trade('92233720368.54780000', TDivMax, '0.00000001', TMSC, 1)
        except: txid_a43 = '0'
        self.check_invalid('amount for sale is too large (92233720368.54780000 TDivMax)', txid_a43)

        try:    txid_a44 = entity_a1.trade('1', TIndiv1, '92233720368.54780000', TMSC, 1)
        except: txid_a44 = '0'
        self.check_invalid('amount desired is too large (92233720368.54780000 TMSC)', txid_a44)

        try:    txid_a45 = entity_a3.trade('9223372036854780000', TIndivMax, '0.00000001', TMSC, 1)
        except: txid_a45 = '0'
        self.check_invalid('amount for sale is too large (9223372036854780000 TIndivMax)', txid_a45)

        try:    txid_a46 = entity_a1.trade('92233720368.54780000', TMSC, '92233720368.54780000', TDiv1, 1)
        except: txid_a46 = '0'
        self.check_invalid('both amounts are too large', txid_a46)

        try:    txid_a47 = entity_a1.trade('92233720368.54780000', TMSC, '9223372036854780000', TIndiv1, 1)
        except: txid_a47 = '0'
        self.check_invalid('both amounts are too large', txid_a47)


    # A42-47
    def test_invalid_amount_too_large_raw(self):
        entity_a1 = self.entities[1]
        entity_a3 = self.entities[3]

        # TODO: testplan provided 92233720368.54780000 (max + x) and 9223372036854770,001 (within range) ?

        #          entity_a1.trade('0.00000001', TDiv1, '92233720368.54780000', TMSC, 1)
        txid_a42 = entity_a1.node.sendrawtx_MP(entity_a1.address,
                                               '0000001580000007000000000000000100000002800000000000106001')
        self.check_invalid('amount desired is too large (0x8000000000001060 TMSC)', txid_a42)

        #          entity_a3.trade('92233720368.54780000', TDivMax, '0.00000001', TMSC, 1)
        txid_a43 = entity_a3.node.sendrawtx_MP(entity_a3.address,
                                               '000000158000000a800000000000106000000002000000000000000101')
        self.check_invalid('amount for sale is too large (0x8000000000001060 TDivMax)', txid_a43)

        #          entity_a1.trade('1', TIndiv1, '92233720368.54780000', TMSC, 1)
        txid_a44 = entity_a1.node.sendrawtx_MP(entity_a1.address,
                                               '0000001580000003000000000000000100000002800000000000106001')
        self.check_invalid('amount desired is too large (0x8000000000001060 TMSC)', txid_a44)

        #          entity_a3.trade('9223372036854780000', TIndivMax, '0.00000001', TMSC, 1)
        txid_a45 = entity_a3.node.sendrawtx_MP(entity_a3.address,
                                               '0000001580000006800000000000106000000002000000000000000101')
        self.check_invalid('amount for sale is too large (0x8000000000001060 TIndivMax)', txid_a45)

        #          entity_a1.trade('92233720368.54780000', TMSC, '92233720368.54780000', TDiv1, 1)
        txid_a46 = entity_a1.node.sendrawtx_MP(entity_a1.address,
                                               '0000001500000002800000000000106080000007800000000000106001')
        self.check_invalid('both amounts are too large (0x8000000000001060 TMSC, 0x8000000000001060 TDiv1)', txid_a46)

        #          entity_a1.trade('92233720368.54780000', TMSC, '9223372036854780000', TIndiv1, 1)
        txid_a47 = entity_a1.node.sendrawtx_MP(entity_a1.address,
                                               '0000001500000002800000000000106080000003800000000000106001')
        self.check_invalid('both amounts are too large (0x8000000000001060 TMSC, 0x8000000000001060 TIndiv1)', txid_a47)


    # A48-53
    def test_invalid_amount_negative(self):
        entity_a1 = self.entities[1]
        entity_a3 = self.entities[3]

        try:    txid_a48 = entity_a1.trade('0.00000001', TDiv1, '-0.00000001', TMSC, 1)
        except: txid_a48 = '0'
        self.check_invalid('amount desired is negative (-0.00000001 TMSC)', txid_a48)

        try:    txid_a49 = entity_a3.trade('-0.00000001', TDivMax, '0.00000001', TMSC, 1)
        except: txid_a49 = '0'
        self.check_invalid('amount for sale is negative (-0.00000001 TDivMax)', txid_a49)

        try:    txid_a50 = entity_a1.trade('1', TIndiv1, '-0.00000001', TMSC, 1)
        except: txid_a50 = '0'
        self.check_invalid('amount desired is negative (-0.00000001 TMSC)', txid_a50)

        try:    txid_a51 = entity_a3.trade('-1', TIndivMax, '0.00000001', TMSC, 1)
        except: txid_a51 = '0'
        self.check_invalid('amount for sale is negative (-1 TIndivMax)', txid_a51)

        try:    txid_a52 = entity_a1.trade('-0.00000001', TMSC, '-0.00000001', TDiv1, 1)
        except: txid_a52 = '0'
        self.check_invalid('both amounts are negative (-0.00000001 TMSC,-0.00000001 TDiv1)', txid_a52)

        try:    txid_a53 = entity_a1.trade('-0.00000001', TMSC, '-1', TIndiv1, 1)
        except: txid_a53 = '0'
        self.check_invalid('both amounts are negative (-0.00000001 TMSC,-1 TIndiv1)', txid_a53)


    # A54-55
    def test_invalid_negative_zero(self):
        entity_a1 = self.entities[1]
        entity_a3 = self.entities[3]

        # TODO: unclear, if 0xff or 0x80, so both done
        # TODO: tests with a3 are on top and not part of the plan

        #                    entity_a1.trade('-0.00000000', TMSC, '1.00000000', TDiv1, 1)
        try:    txid_a54_1 = entity_a1.node.sendrawtx_MP(entity_a1.address,
                                                         '00000015000000028000000000000000800000070000000005f5e10001')
        except: txid_a54_1 = '0'
        self.check_invalid('amount for sale is negative zero (0x8000000000000000 TMSC)', txid_a54_1)

        #                    entity_a1.trade('-0.00000000', TMSC, '1.00000000', TDiv1, 1)
        try:    txid_a54_2 = entity_a1.node.sendrawtx_MP(entity_a1.address,
                                                         '0000001500000002ffffffffffffffff800000070000000005f5e10001')
        except: txid_a54_2 = '0'
        self.check_invalid('amount for sale is negative zero (0xffffffffffffffff TMSC)', txid_a54_2)

        #                    entity_a3.trade('-0', TIndivMax, '1.00000000', TMSC, 1)
        try:    txid_a54_3 = entity_a3.node.sendrawtx_MP(entity_a3.address,
                                                         '00000015800000068000000000000000000000020000000005f5e10001')
        except: txid_a54_3 = '0'
        self.check_invalid('amount for sale is negative zero (0x8000000000000000 TIndivMax)', txid_a54_3)

        #                    entity_a3.trade('-0', TIndivMax, '1.00000000', TMSC, 1)
        try:    txid_a54_4 = entity_a3.node.sendrawtx_MP(entity_a3.address,
                                                         '0000001580000006ffffffffffffffff000000020000000005f5e10001')
        except: txid_a54_4 = '0'
        self.check_invalid('amount for sale is negative zero (0xffffffffffffffff TIndivMax)', txid_a54_4)

        #                    entity_a1.trade('1.00000000', TMSC, '-0', TIndiv1, 1)
        try:    txid_a55_1 = entity_a1.node.sendrawtx_MP(entity_a1.address,
                                                         '00000015000000020000000005f5e10080000003800000000000000001')
        except: txid_a55_1 = '0'
        self.check_invalid('amount desired is negative zero (0x8000000000000000 TMSC)', txid_a55_1)

        #                    entity_a1.trade('1.00000000', TMSC, '-0', TIndiv1, 1)
        try:    txid_a55_2 = entity_a1.node.sendrawtx_MP(entity_a1.address,
                                                         '00000015000000020000000005f5e10080000003ffffffffffffffff01')
        except: txid_a55_2 = '0'
        self.check_invalid('amount desired is negative zero (0xffffffffffffffff TMSC)', txid_a55_2)

        #                    entity_a3.trade('1.00000000', TMSC, '-1.00000000', TDivMax, 1)
        try:    txid_a55_3 = entity_a3.node.sendrawtx_MP(entity_a3.address,
                                                         '00000015000000020000000005f5e1008000000a800000000000000001')
        except: txid_a55_3 = '0'
        self.check_invalid('amount desired is negative zero (0x8000000000000000 TMSC)', txid_a55_3)

        #                    entity_a3.trade('1.00000000', TMSC, '-1.00000000', TDivMax, 1)
        try:    txid_a55_4 = entity_a3.node.sendrawtx_MP(entity_a3.address,
                                                         '00000015000000020000000005f5e1008000000affffffffffffffff01')
        except: txid_a55_4 = '0'
        self.check_invalid('amount desired is negative zero (0xffffffffffffffff TMSC)', txid_a55_4)


    def test_new_orders_for_divisible(self):
        entity_a1 = self.entities[1]

        self.check_balance(entity_a1.address, TMSC,  '150.00000000', '0.00000000')
        self.check_balance(entity_a1.address, TDiv1, '100.00000000', '0.00000000')
        self.check_balance(entity_a1.address, TIndiv1, '1000', '0')

        # A58
        entity_a1.trade('10.00000000', TDiv1, '10.00000000', TMSC)
        self.generate_block()
        #
        #
        # A1:   SELL   10.00000000 TDiv1   @   1.00000000 TMSC/TDiv1   (total: 10.00000000 TMSC)  <<  added
        #
        #
        self.check_balance(entity_a1.address, TMSC, '150.00000000',  '0.00000000')
        self.check_balance(entity_a1.address, TDiv1, '90.00000000', '10.00000000')
        self.check_balance(entity_a1.address, TIndiv1, '1000', '0')

        # A59
        try:    txid_a59 = entity_a1.trade('10.00000001', TMSC, '9.99999999', TDiv1, CANCEL_2)
        except: txid_a59 = '0'
        self.check_invalid('no active orders for that pair and price', txid_a59)

        # A60
        entity_a1.trade('3.00000000', TDiv1, '3.00000000', TMSC)
        self.generate_block()
        #
        #
        # A1:   SELL    3.00000000 TDiv1   @   1.00000000 TMSC/TDiv1   (total:  3.00000000 TMSC)  <<  added
        # A1:   SELL   10.00000000 TDiv1   @   1.00000000 TMSC/TDiv1   (total: 10.00000000 TMSC)
        #
        #
        self.check_balance(entity_a1.address, TMSC, '150.00000000',  '0.00000000')
        self.check_balance(entity_a1.address, TDiv1, '87.00000000', '13.00000000')

        # A62
        entity_a1.trade('1.00000000', TDiv1, '0.00000001', TMSC)
        self.generate_block()
        #
        #
        # A1:   SELL    3.00000000 TDiv1   @   1.00000000 TMSC/TDiv1   (total:  3.00000000 TMSC)
        # A1:   SELL   10.00000000 TDiv1   @   1.00000000 TMSC/TDiv1   (total: 10.00000000 TMSC)
        # A1:   SELL    1.00000000 TDiv1   @   0.00000001 TMSC/TDiv1   (total:  0.00000001 TMSC)  <<  added
        #
        #
        self.check_balance(entity_a1.address, TMSC, '150.00000000',  '0.00000000')
        self.check_balance(entity_a1.address, TDiv1, '86.00000000', '14.00000000')

        # A63
        entity_a1.trade('5', TIndiv1, '6.00000000', TMSC)
        self.generate_block()
        #
        #
        # A1:   SELL   5 TIndiv1   @   1.20000000 TMSC/TIndiv1   (total:  6.0 TMSC)  <<  added
        #
        #
        self.check_balance(entity_a1.address, TMSC, '150.00000000', '0.00000000')
        self.check_balance(entity_a1.address, TIndiv1, '995', '5')


    def test_match_divisible_at_same_unit_price(self):
        entity_a1 = self.entities[1]
        entity_a2 = self.entities[2]
        entity_a3 = self.entities[3]

        self.check_balance(entity_a1.address, TMSC, '150.00000000',  '0.00000000')
        self.check_balance(entity_a2.address, TMSC,  '50.00000000',  '0.00000000')
        self.check_balance(entity_a3.address, TMSC,  '25.00000000',  '0.00000000')
        self.check_balance(entity_a1.address, TDiv1, '86.00000000', '14.00000000')
        self.check_balance(entity_a2.address, TDiv1, '50.00000000',  '0.00000000')
        self.check_balance(entity_a3.address, TDiv1,  '0.00000000',  '0.00000000')

        # TODO: clarify A66 -- it matches with A62 !

        # A66
        entity_a1.trade('1.00000000', TMSC, '1.00000000', TDiv1)
        self.generate_block()
        #
        #
        # A1:   SELL    3.00000000 TDiv1   @   1.00000000 TMSC/TDiv1   (total:  3.00000000 TMSC)
        # A1:   SELL   10.00000000 TDiv1   @   1.00000000 TMSC/TDiv1   (total: 10.00000000 TMSC)
        # A1:   SELL    1.00000000 TDiv1   @   0.00000001 TMSC/TDiv1   (total:  0.00000001 TMSC)
        #
        # A1;   BUY     1.00000000 TDiv1   @   1.00000000 TMSC/TDiv1   (total:  1.00000000 TMSC)  <<  pending
        #
        # =>
        #
        # A1    BUYS    1.00000000 TDiv1   @   0.00000001 TMSC/TDiv1   (total:  0.00000001 TMSC)  [0.00000001 TMSC for 1 TDiv1]
        # A1    BUYS    0.99999999 TDiv1   @   1.00000000 TMSC/TDiv1   (total:  0.99999999 TMSC)  [1 TMSC for 1.99999999 TDiv1]
        #
        # =>
        #
        # A1:   SELL    3.00000000 TDiv1   @   1.00000000 TMSC/TDiv1   (total:  3.00000000 TMSC)
        # A1:   SELL    9.00000001 TDiv1   @   1.00000000 TMSC/TDiv1   (total:  9.00000001 TMSC)  <<  updated
        #
        #

        # Movements:
        # A1->A1: 0.00000001 TMSC, A1->A1: 1.00000000 TDiv1
        # A1->A1: 0.99999999 TMSC, A1->A1: 0.99999999 TDiv1
        #
        self.check_balance(entity_a1.address, TMSC, '150.00000000',  '0.00000000')
        self.check_balance(entity_a1.address, TDiv1, '87.99999999', '12.00000001')

        # A67
        entity_a2.trade('1.00000000', TMSC, '1.00000000', TDiv1)
        self.generate_block()
        #
        #
        # A1:   SELL    3.00000000 TDiv1   @   1.00000000 TMSC/TDiv1   (total:  3.00000000 TMSC)
        # A1:   SELL    9.00000001 TDiv1   @   1.00000000 TMSC/TDiv1   (total:  9.00000001 TMSC)
        #
        # A2;   BUY     1.00000000 TDiv1   @   1.00000000 TMSC/TDiv1   (total:  1.00000000 TMSC)  <<  pending
        #
        # =>
        #
        # A2    BUYS    1.00000000 TDiv1   @   1.00000000 TMSC/TDiv1   (total:  1.00000000 TMSC)  [1.0 TMSC for 1.0 TDiv1]
        #
        # =>
        #
        # A1:   SELL    3.00000000 TDiv1   @   1.00000000 TMSC/TDiv1   (total:  3.00000000 TMSC)
        # A1:   SELL    8.00000001 TDiv1   @   1.00000000 TMSC/TDiv1   (total:  8.00000001 TMSC)  <<  updated
        #
        #

        # Movements:
        # A2->A1: 1.00000000 TMSC, A1->A2: 1.00000000 TDiv1
        #
        self.check_balance(entity_a1.address, TMSC, '151.00000000',  '0.00000000')
        self.check_balance(entity_a2.address, TMSC,  '49.00000000',  '0.00000000')
        self.check_balance(entity_a1.address, TDiv1, '87.99999999', '11.00000001')
        self.check_balance(entity_a2.address, TDiv1, '51.00000000',  '0.00000000')

        # A69
        entity_a2.trade('6.00000000', TDiv1, '6.00000000', TMSC)
        self.generate_block()
        #
        #
        # A2:   SELL    6.00000000 TDiv1   @   1.00000000 TMSC/TDiv1   (total:  6.00000000 TMSC)  <<  added
        # A1:   SELL    3.00000000 TDiv1   @   1.00000000 TMSC/TDiv1   (total:  3.00000000 TMSC)
        # A1:   SELL    8.00000001 TDiv1   @   1.00000000 TMSC/TDiv1   (total:  8.00000001 TMSC)
        #
        #
        self.check_balance(entity_a1.address, TMSC, '151.00000000',  '0.00000000')
        self.check_balance(entity_a2.address, TMSC,  '49.00000000',  '0.00000000')
        self.check_balance(entity_a1.address, TDiv1, '87.99999999', '11.00000001')
        self.check_balance(entity_a2.address, TDiv1, '45.00000000',  '6.00000000')

        # A71
        entity_a3.trade('0.50000000', TMSC, '0.50000000', TDiv1)
        self.generate_block()
        #
        #
        # A2:   SELL    6.00000000 TDiv1   @   1.00000000 TMSC/TDiv1   (total:  6.00000000 TMSC)
        # A1:   SELL    3.00000000 TDiv1   @   1.00000000 TMSC/TDiv1   (total:  3.00000000 TMSC)
        # A1:   SELL    8.00000001 TDiv1   @   1.00000000 TMSC/TDiv1   (total:  8.00000001 TMSC)
        #
        # A3;   BUY     0.50000000 TDiv1   @   1.00000000 TMSC/TDiv1   (total:  0.50000000 TMSC)  <<  pending
        #
        # =>
        #
        # A3    BUYS    0.50000000 TDiv1   @   1.00000000 TMSC/TDiv1   (total:  0.50000000 TMSC)  [0.5 TMSC for 0.5 TDiv1]
        #
        # =>
        #
        # A2:   SELL    6.00000000 TDiv1   @   1.00000000 TMSC/TDiv1   (total:  6.00000000 TMSC)
        # A1:   SELL    3.00000000 TDiv1   @   1.00000000 TMSC/TDiv1   (total:  3.00000000 TMSC)
        # A1:   SELL    7.50000001 TDiv1   @   1.00000000 TMSC/TDiv1   (total:  7.50000001 TMSC)  <<  updated
        #
        #

        # Movements:
        # A3->A1: 0.50000000 TMSC, A1->A3: 0.50000000 TDiv1
        #
        self.check_balance(entity_a1.address, TMSC, '151.50000000',  '0.00000000')
        self.check_balance(entity_a3.address, TMSC,  '24.50000000',  '0.00000000')
        self.check_balance(entity_a1.address, TDiv1, '87.99999999', '10.50000001')
        self.check_balance(entity_a3.address, TDiv1,  '0.50000000',  '0.00000000')

        # A72
        entity_a3.trade('11.50000000', TMSC, '11.50000000', TDiv1)
        self.generate_block()
        #
        #
        # A2:   SELL    6.00000000 TDiv1   @   1.00000000 TMSC/TDiv1   (total:  6.00000000 TMSC)
        # A1:   SELL    3.00000000 TDiv1   @   1.00000000 TMSC/TDiv1   (total:  3.00000000 TMSC)
        # A1:   SELL    7.50000001 TDiv1   @   1.00000000 TMSC/TDiv1   (total:  7.50000001 TMSC)
        #
        # A3;   BUY    11.50000000 TDiv1   @   1.00000000 TMSC/TDiv1   (total: 11.50000000 TMSC)  <<  pending
        #
        # =>
        #
        # A3    BUYS    7.50000001 TDiv1   @   1.00000000 TMSC/TDiv1   (total:  7.50000001 TMSC)  [ 7.5~ TMSC for  7.5~ TDiv1]
        # A3    BUYS    3.00000000 TDiv1   @   1.00000000 TMSC/TDiv1   (total:  3.00000000 TMSC)  [10.5~ TMSC for 10.5~ TDiv1]
        # A3    BUYS    0.99999999 TDiv1   @   1.00000000 TMSC/TDiv1   (total:  0,99999999 TMSC)  [11.50 TMSC for 11.50 TDiv1]
        #
        # =>
        #
        # A2:   SELL    5.00000001 TDiv1   @   1.00000000 TMSC/TDiv1   (total:  5.00000001 TMSC)  <<  updated
        #
        #

        # Movements:
        # A3->A1: 7.50000001 TMSC, A1->A3: 7.50000001 TDiv1
        # A3->A1: 3.00000000 TMSC, A1->A3: 3.00000000 TDiv1
        # A3->A2: 0,99999999 TMSC, A2->A3: 0.99999999 TDiv1
        #
        self.check_balance(entity_a1.address, TMSC, '162.00000001', '0.00000000')
        self.check_balance(entity_a2.address, TMSC,  '49.99999999', '0.00000000')
        self.check_balance(entity_a3.address, TMSC,  '13.00000000', '0.00000000')
        self.check_balance(entity_a1.address, TDiv1, '87.99999999', '0.00000000')
        self.check_balance(entity_a2.address, TDiv1, '45.00000000', '5.00000001')
        self.check_balance(entity_a3.address, TDiv1, '12.00000000', '0.00000000')


    def test_match_divisible_at_better_unit_price(self):
        entity_a1 = self.entities[1]
        entity_a2 = self.entities[2]
        entity_a3 = self.entities[3]
        #
        # Orderbook:
        #
        # A1:   SELL   5 TIndiv1   @   1.20000000 TMSC/TIndiv1   (total:  6.0 TMSC)
        #
        # A2:   SELL   5.00000001 TDiv1   @   1.00000000 TMSC/TDiv1   (total:  5.00000001 TMSC)
        #
        #
        self.check_balance(entity_a1.address, TMSC, '162.00000001', '0.00000000')
        self.check_balance(entity_a2.address, TMSC,  '49.99999999', '0.00000000')
        self.check_balance(entity_a3.address, TMSC,  '13.00000000', '0.00000000')
        self.check_balance(entity_a1.address, TDiv1, '87.99999999', '0.00000000')
        self.check_balance(entity_a2.address, TDiv1, '45.00000000', '5.00000001')
        self.check_balance(entity_a3.address, TDiv1, '12.00000000', '0.00000000')

        # A75
        entity_a3.trade('2.00000000', TMSC, '1.00000000', TDiv1)
        self.generate_block()
        #
        #
        # A2:   SELL   5.00000001 TDiv1   @   1.00000000 TMSC/TDiv1   (total:  5.00000001 TMSC)
        #
        # A3;   BUY    1.00000000 TDiv1   @   2.00000000 TMSC/TDiv1   (total:  2.00000000 TMSC)  <<  pending
        #
        #              ^ TODO: looks very, very strange.. only one to buy, but bought two..
        # =>
        #
        # A3    BUYS   2.00000000 TDiv1   @   1.00000000 TMSC/TDiv1   (total:  2.00000000 TMSC)  [2.0 TMSC for 2.0 TDiv1]
        #
        # =>
        #
        # A2:   SELL   3.00000001 TDiv1   @   1.00000000 TMSC/TDiv1   (total:  3.00000001 TMSC)  <<  updated
        #
        #

        # Movements:
        # A3->A2: 2.00000000 TMSC, A2->A3: 2.00000000 TDiv1
        #
        self.check_balance(entity_a2.address, TMSC,  '51.99999999', '0.00000000')
        self.check_balance(entity_a3.address, TMSC,  '11.00000000', '0.00000000')
        self.check_balance(entity_a2.address, TDiv1, '45.00000000', '3.00000001')
        self.check_balance(entity_a3.address, TDiv1, '14.00000000', '0.00000000')

        # A76
        entity_a3.trade('0.00000002', TMSC, '0.00000001', TDiv1)
        self.generate_block()
        #
        #
        # A2:   SELL   3.00000001 TDiv1   @   1.00000000 TMSC/TDiv1   (total:  3.00000001 TMSC)
        #
        # A3:   BUY    0.00000001 TDiv1   @   2.00000000 TMSC/TDiv1   (total:  0.00000002 TMSC)  <<  pending
        #
        # =>
        #
        # A3    BUYS   0.00000002 TDiv1   @   1.00000000 TMSC/TDiv1   (total:  0.00000002 TMSC)  [0.0~2 TMSC for 0.0~2 TDiv1]
        #
        # =>
        #
        # A2:   SELL   2.99999999 TDiv1   @   1.00000000 TMSC/TDiv1   (total:  2.99999999 TMSC)  <<  updated
        #
        #

        # Movements:
        # A3->A2: 0.00000002 TMSC, A2->A3: 0.00000002 TDiv1
        #
        self.check_balance(entity_a2.address, TMSC,  '52.00000001', '0.00000000')
        self.check_balance(entity_a3.address, TMSC,  '10.99999998', '0.00000000')
        self.check_balance(entity_a2.address, TDiv1, '45.00000000', '2.99999999')
        self.check_balance(entity_a3.address, TDiv1, '14.00000002', '0.00000000')

        # A77
        entity_a3.trade('5.00000000', TMSC, '4.00000000', TDiv1)
        self.generate_block()
        #
        #
        # A2:   SELL   2.99999999 TDiv1   @   1.00000000 TMSC/TDiv1   (total:  2.99999999 TMSC)
        #
        # A3:   BUY    4.00000000 TDiv1   @   1.25000000 TMSC/TDiv1   (total:  5.00000000 TMSC)  <<  pending
        #
        # =>
        #
        # A3    BUYS   2.99999999 TDiv1   @   1.00000000 TMSC/TDiv1   (total:  2.99999999 TMSC)  [2.9~9 TMSC for 2.9~9 TDiv1]
        #
        # =>
        #
        # A3:   BUY    1,600000008 TDiv1  @   1.25000000 TMSC/TDiv1   (total:  2.00000001 TMSC)  <<  added
        #
        #

        # Movements:
        # A3->A2: 2.99999999 TMSC, A2->A3: 2.99999999 TDiv1
        #
        self.check_balance(entity_a2.address, TMSC,  '55.00000000', '0.00000000')
        self.check_balance(entity_a3.address, TMSC,   '5.99999998', '2.00000001')
        self.check_balance(entity_a2.address, TDiv1, '45.00000000', '0.00000000')
        self.check_balance(entity_a3.address, TDiv1, '17.00000001', '0.00000000')

        # A78
        entity_a3.trade('5.00000000', TMSC, '4.00000000', TDiv1, CANCEL_2)
        self.generate_block()
        #
        #
        # A3:   BUY    1,600000008 TDiv1   @   1.25000000 TMSC/TDiv1   (total:  2.00000001 TMSC)
        #
        # A3:   CANCEL 4.00000000  TDiv1   @   1.25000000 TMSC/TDiv1   (total:  5.00000000 TMSC)  <<  pending
        #
        # =>
        #
        # No more open orders for TDiv1 / TMSC
        #
        #
        self.check_balance(entity_a3.address, TMSC,   '7.99999999', '0.00000000')
        self.check_balance(entity_a3.address, TDiv1, '17.00000001', '0.00000000')


    def test_match_divisible_with_three(self):
        entity_a1 = self.entities[1]
        entity_a2 = self.entities[2]
        entity_a3 = self.entities[3]
        #
        # Orderbook:
        #
        # A1:   SELL   5 TIndiv1   @   1.20000000 TMSC/TIndiv1   (total:  6.0 TMSC)
        #
        #
        self.check_balance(entity_a1.address, TMSC,  '162.00000001', '0.00000000')
        self.check_balance(entity_a2.address, TMSC,   '55.00000000', '0.00000000')
        self.check_balance(entity_a3.address, TMSC,    '7.99999999', '0.00000000')
        self.check_balance(entity_a1.address, TDiv3,   '0.00000000', '0.00000000')
        self.check_balance(entity_a2.address, TDiv3, '200.00000000', '0.00000000')
        self.check_balance(entity_a3.address, TDiv3, '200.00000000', '0.00000000')

        # A81
        try:    txid_a81 = entity_a2.trade('-0.00000001', TDiv3, '0.00000000', TMSC, CANCEL_3)
        except: txid_a81 = '0'
        self.check_invalid('A2 does not have any open order of pair TDiv3 - TMSC', txid_a81)

        # A82
        try:    txid_a82 = entity_a3.trade('0.00000000', TDiv3, '-0.00000001', TMSC, CANCEL_3)
        except: txid_a82 = '0'
        self.check_invalid('A3 does not have any open order of pair TDiv3 - TMSC', txid_a82)

        # A83 with zero amounts
        try:    txid_a83_a = entity_a1.trade('0.00000000', TMSC, '0.00000000', TDiv3, CANCEL_3)
        except: txid_a83_a = '0'
        self.check_invalid('A1 does not have any open order of pair TMSC - TDiv3', txid_a83_a)

        # A83 with positive amounts
        try:    txid_a83_b = entity_a1.trade('6.00000000', TMSC, '0.00000005', TDiv3, CANCEL_3)
        except: txid_a83_b = '0'
        self.check_invalid('A1 does not have any open order of pair TMSC - TDiv3', txid_a83_b)

        # A84
        entity_a2.trade('10.00000000', TDiv3, '5.00000000', TMSC)
        self.generate_block()
        #
        #
        # A2:   SELL   10.00000000 TDiv3   @   0.50000000 TMSC/TDiv3   (total:  5.0 TMSC)  <<  added
        #
        #
        self.check_balance(entity_a2.address, TMSC,   '55.00000000',  '0.00000000')
        self.check_balance(entity_a2.address, TDiv3, '190.00000000', '10.00000000')

        # A85
        entity_a3.trade('10.00000000', TDiv3, '10.00000000', TMSC)
        self.generate_block()
        #
        #
        # A3:   SELL    10.00000000 TDiv3   @   1.00000000 TMSC/TDiv3   (total: 10.0 TMSC)  <<  added
        # A2:   SELL    10.00000000 TDiv3   @   0.50000000 TMSC/TDiv3   (total:  5.0 TMSC)
        #
        #
        self.check_balance(entity_a3.address, TMSC,    '7.99999999',  '0.00000000')
        self.check_balance(entity_a3.address, TDiv3, '190.00000000', '10.00000000')

        # A86
        entity_a2.trade('15.00000000', TDiv3, '22.50000000', TMSC)
        self.generate_block()
        #
        #
        # A2:   SELL    15.00000000 TDiv3   @   1.50000000 TMSC/TDiv3   (total: 22.5 TMSC)  <<  added
        # A3:   SELL    10.00000000 TDiv3   @   1.00000000 TMSC/TDiv3   (total: 10.0 TMSC)
        # A2:   SELL    10.00000000 TDiv3   @   0.50000000 TMSC/TDiv3   (total:  5.0 TMSC)
        #
        #
        self.check_balance(entity_a2.address, TMSC,   '55.00000000',  '0.00000000')
        self.check_balance(entity_a2.address, TDiv3, '175.00000000', '25.00000000')


        # A87
        entity_a1.trade('60.00000000', TMSC, '120.00000001', TDiv3)
        self.generate_block()
        #
        #
        # A2:   SELL   15.00000000 TDiv3   @   1.50000000 TMSC/TDiv3   (total: 22.5 TMSC)
        # A3:   SELL   10.00000000 TDiv3   @   1.00000000 TMSC/TDiv3   (total: 10.0 TMSC)
        # A2:   SELL   10.00000000 TDiv3   @   0.50000000 TMSC/TDiv3   (total:  5.0 TMSC)
        #
        # A1:   BUY   120.00000001 TDiv3   @   0.49999999995833333333680555555527 TMSC/TDiv3   (total: 60.0 TMSC)  <<  added
        #
        #
        self.check_balance(entity_a1.address, TMSC, '102.00000001', '60.00000000')
        self.check_balance(entity_a1.address, TDiv3,  '0.00000000',  '0.00000000')

        # A88
        entity_a1.trade('45.00000000', TMSC, '22.50000000', TDiv3)
        self.generate_block()
        #
        #
        # A2:   SELL   15.00000000 TDiv3   @   1.50000000 TMSC/TDiv3   (total: 22.5 TMSC)
        # A3:   SELL   10.00000000 TDiv3   @   1.00000000 TMSC/TDiv3   (total: 10.0 TMSC)
        # A2:   SELL   10.00000000 TDiv3   @   0.50000000 TMSC/TDiv3   (total:  5.0 TMSC)
        #
        # A1:   BUY    22.50000000 TDiv3   @   2.00000000 TMSC/TDiv3   (total: 45.0 TMSC)  <<  pending
        # A1:   BUY   120.00000001 TDiv3   @   0.49999999 TMSC/TDiv3   (total: 60.0 TMSC)
        #
        # =>
        #
        # A1   BUYS   10.00000000 TDiv3   @   0.50000000 TMSC/TDiv3   (total:  5.0 TMSC)   [total:  5.0 TMSC for 10.0 TDiv3]
        # A1   BUYS   10.00000000 TDiv3   @   1.00000000 TMSC/TDiv3   (total: 10.0 TMSC)   [total: 15.0 TMSC for 20.0 TDiv3]
        # A1   BUYS   15.00000000 TDiv3   @   1.50000000 TMSC/TDiv3   (total: 22.5 TMSC)   [total: 37.5 TMSC for 35.0 TDiv3]
        #
        # =>
        #
        # A1:   BUY     3.75000000 TDiv3   @   2.00000000 TMSC/TDiv3   (total:  7.5 TMSC)  <<  updated
        # A1:   BUY   120.00000001 TDiv3   @   0.49999999 TMSC/TDiv3   (total: 60.0 TMSC)
        #
        #

        # Movements:
        # A1->A2:  5.0 TMSC, A2->A1: 10.0 TDiv3
        # A1->A3: 10.0 TMSC, A3->A1: 10.0 TDiv3
        # A1->A2: 22.5 TMSC, A2->A1: 15.0 TDiv3
        #
        self.check_balance(entity_a1.address, TMSC,   '57.00000001', '67.50000000')
        self.check_balance(entity_a2.address, TMSC,   '82.50000000',  '0.00000000')
        self.check_balance(entity_a3.address, TMSC,   '17.99999999',  '0.00000000')
        self.check_balance(entity_a1.address, TDiv3,  '35.00000000',  '0.00000000')
        self.check_balance(entity_a2.address, TDiv3, '175.00000000',  '0.00000000')
        self.check_balance(entity_a3.address, TDiv3, '190.00000000',  '0.00000000')


if __name__ == '__main__':
    MetaDexPlanTest().main()
