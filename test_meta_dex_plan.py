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
        self.test_invalid_action_raw()
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
        self.test_match_large_and_small_amounts()

        self.test_new_orders_for_indivisible()
        self.test_match_indivisible_at_same_unit_price()
        self.test_match_indivisible_at_better_unit_price()
        self.test_match_indivisible_with_three()

        self.success = TestInfo.Status()


    def prepare_funding(self):
        """A1, A2, A3 (node 2-4) are funded with 50.0 BTC each.

        The miner (node 1) furthermore purchases 50000.0 MSC and 50000.0 TMSC.
        Those tokens are not yet distributed and used later.

        MSC and TMSC balance of the miner is tested."""
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

        self.generate_block()
        self.check_balance(addr, TIndiv1,   '9223372036854775807',  '0')
        self.check_balance(addr, TIndiv2,   '9223372036854775807',  '0')
        self.check_balance(addr, TIndiv3,   '9223372036854775807',  '0')
        self.check_balance(addr, TIndivMax, '9223372036854775807',  '0')
        self.check_balance(addr, TDiv1,     '92233720368.54775807', '0.00000000')
        self.check_balance(addr, TDiv2,     '92233720368.54775807', '0.00000000')
        self.check_balance(addr, TDiv3,     '92233720368.54775807', '0.00000000')
        self.check_balance(addr, TDivMax,   '92233720368.54775807', '0.00000000')


    def initial_distribution(self):
        """Tokens are sent from the miner (node 1) to A1, A2, A3 (node 2-4).

        Final balances are tested."""
        entity_miner = self.entities[0]
        entity_a1 = self.entities[1]
        entity_a2 = self.entities[2]
        entity_a3 = self.entities[3]

        entity_miner.send(entity_a1.address, TMSC,  '150.00000000')
        entity_miner.send(entity_a2.address, TMSC,   '50.00000000')
        entity_miner.send(entity_a3.address, TMSC,   '25.00000000')
        entity_miner.send(entity_a1.address, TDiv1, '100.00000000')
        entity_miner.send(entity_a2.address, TDiv1,  '50.00000000')
        # A3 does not receive any TDiv1
        # A1 does not receive any TDiv2
        entity_miner.send(entity_a2.address, TDiv2, '200.00000000')
        # A3 does not receive any TDiv2
        # A1 does not receive any TDiv3
        entity_miner.send(entity_a2.address, TDiv3, '200.00000000')
        entity_miner.send(entity_a3.address, TDiv3, '200.00000000')
        # A1 does not receive any TDivMax
        # A2 does not receive any TDivMax
        entity_miner.send(entity_a3.address, TDivMax, '92233720368.54775807')
        entity_miner.send(entity_a1.address, TIndiv1, '1000')
        entity_miner.send(entity_a2.address, TIndiv1, '50')
        # A3 does not receive any TIndiv1
        # A1 does not receive any TIndiv2
        entity_miner.send(entity_a2.address, TIndiv2, '2000')
        # A3 does not receive any TIndiv2
        # A1 does not receive any TIndiv3
        entity_miner.send(entity_a2.address, TIndiv3,  '200')
        entity_miner.send(entity_a3.address, TIndiv3,  '200')
        # A1 does not receive any TIndivMax
        # A2 does not receive any TIndivMax
        entity_miner.send(entity_a3.address, TIndivMax, '9223372036854775807')

        self.generate_block()

        self.check_balance(entity_a1.address, TMSC,  '150.00000000', '0.00000000')
        self.check_balance(entity_a2.address, TMSC,   '50.00000000', '0.00000000')
        self.check_balance(entity_a3.address, TMSC,   '25.00000000', '0.00000000')
        self.check_balance(entity_a1.address, TDiv1, '100.00000000', '0.00000000')
        self.check_balance(entity_a2.address, TDiv1,  '50.00000000', '0.00000000')
        self.check_balance(entity_a3.address, TDiv1,   '0.00000000', '0.00000000')
        self.check_balance(entity_a1.address, TDiv2,   '0.00000000', '0.00000000')
        self.check_balance(entity_a2.address, TDiv2, '200.00000000', '0.00000000')
        self.check_balance(entity_a3.address, TDiv2,   '0.00000000', '0.00000000')
        self.check_balance(entity_a1.address, TDiv3,   '0.00000000', '0.00000000')
        self.check_balance(entity_a2.address, TDiv3, '200.00000000', '0.00000000')
        self.check_balance(entity_a3.address, TDiv3, '200.00000000', '0.00000000')
        self.check_balance(entity_a1.address, TDivMax, '0.00000000', '0.00000000')
        self.check_balance(entity_a2.address, TDivMax, '0.00000000', '0.00000000')
        self.check_balance(entity_a3.address, TDivMax, '92233720368.54775807', '0.00000000')
        self.check_balance(entity_a1.address, TIndiv1, '1000', '0')
        self.check_balance(entity_a2.address, TIndiv1,   '50', '0')
        self.check_balance(entity_a3.address, TIndiv1,    '0', '0')
        self.check_balance(entity_a1.address, TIndiv2,    '0', '0')
        self.check_balance(entity_a2.address, TIndiv2, '2000', '0')
        self.check_balance(entity_a3.address, TIndiv2,    '0', '0')
        self.check_balance(entity_a1.address, TIndiv3,    '0', '0')
        self.check_balance(entity_a2.address, TIndiv3,  '200', '0')
        self.check_balance(entity_a3.address, TIndiv3,  '200', '0')
        self.check_balance(entity_a1.address, TIndivMax,  '0', '0')
        self.check_balance(entity_a2.address, TIndivMax,  '0', '0')
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
            'Expected transaction to be invalid (reason: %s):\nTransaction hash: %s\n%s\n%s\n' % (
                reason, txid, str(tx), self.nodes[0].getrawtransaction(txid),))


    # A21
    def test_invalid_version_other_than_zero(self):
        """Tests transaction 21 "trade tokens for tokens" with invalid version of 1."""
        entity_a1 = self.entities[1]

        # TODO: Depreciate transaction version tests, once new version of transaction is live.

        TestInfo.ExpectFail()

        #                    entity_a1.trade('2.00000000', TMSC, '2.00000000', TDiv1, ADD_1) with "version = 1"
        try:    txid_a21_1 = entity_a1.node.sendrawtx_MP(entity_a1.address,
                                                         '0001001500000002000000000bebc20080000007000000000bebc20001')
        except: txid_a21_1 = '0'
        self.check_invalid('transaction version > 0', txid_a21_1)

        #                    entity_a1.trade('2.00000000', TMSC, '2.00000000', TDiv1, CANCEL_2) with "version = 1"
        try:    txid_a21_2 = entity_a1.node.sendrawtx_MP(entity_a1.address,
                                                         '0001001500000002000000000bebc20080000007000000000bebc20002')
        except: txid_a21_2 = '0'
        self.check_invalid('transaction version > 0', txid_a21_2)

        #                    entity_a1.trade('2.00000000', TMSC, '2.00000000', TDiv1, CANCEL_3) with "version = 1"
        try:    txid_a21_3 = entity_a1.node.sendrawtx_MP(entity_a1.address,
                                                         '0001001500000002000000000bebc20080000007000000000bebc20003')
        except: txid_a21_3 = '0'
        self.check_invalid('transaction version > 0', txid_a21_3)

        #                    entity_a1.trade('2.00000000', TMSC, '2.00000000', TDiv1, CANCEL_4) with "version = 1"
        try:    txid_a21_4 = entity_a1.node.sendrawtx_MP(entity_a1.address,
                                                         '0001001500000002000000000bebc20080000007000000000bebc20004')
        except: txid_a21_4 = '0'
        self.check_invalid('transaction version > 0', txid_a21_4)

        TestInfo.StopExpectation()


    # A22-23
    def test_invalid_action(self):
        """Tests invalidation of orders with non-existing subaction values.

        The data is submitted via RPC command trade_MP."""
        entity_a1 = self.entities[1]

        TestInfo.ExpectFail()

        try:    txid_a22 = entity_a1.trade('2.00000000', TMSC, '2.00000000', TDiv1, 0)
        except: txid_a22 = '0'
        self.check_invalid('invalid action (0)', txid_a22)

        try:    txid_a23 = entity_a1.trade('2.00000000', TMSC, '2.00000000', TDiv1, 5)
        except: txid_a23 = '0'
        self.check_invalid('invalid action (5)', txid_a23)

        TestInfo.StopExpectation()


    # A22-23
    def test_invalid_action_raw(self):
        """Tests invalidation of orders with non-existing subaction values.

        The data is submitted as raw transaction to get around RPC interface checks."""
        entity_a1 = self.entities[1]

        TestInfo.ExpectFail()

        #                  entity_a1.trade('2.00000000', TMSC, '2.00000000', TDiv1, 0)
        try:    txid_a22 = entity_a1.node.sendrawtx_MP(entity_a1.address,
                                                       '0000001500000002000000000bebc20080000007000000000bebc20000')
        except: txid_a22 = '0'
        self.check_invalid('invalid action (0)', txid_a22)

        #                  entity_a1.trade('2.00000000', TMSC, '2.00000000', TDiv1, 5)
        try:    txid_a23 = entity_a1.node.sendrawtx_MP(entity_a1.address,
                                                       '0000001500000002000000000bebc20080000007000000000bebc20005')
        except: txid_a23 = '0'
        self.check_invalid('invalid action (5)', txid_a23)

        TestInfo.StopExpectation()


    # NOTE: Invalidation tests should be done via trade_MP, but also via raw transactions, to get around input filters.

    # A24
    def test_invalid_cancel_everything_no_active_offers(self):
        """Tests invalidation of transactions with CANCEL-EVERYTHING command, but no active, matching offers."""
        entity_a1 = self.entities[1]

        TestInfo.ExpectFail()

        try:    txid_a24_1 = entity_a1.trade('2.00000000', TMSC, '2.00000000', TDiv1, CANCEL_4)
        except: txid_a24_1 = '0'
        self.check_invalid('no active orders, cancel-everything, positive amounts, test ecosystem', txid_a24_1)

        try:    txid_a24_2 = entity_a1.trade('2.00000000', TMSC, '2.00000000', TMSC,  CANCEL_4)
        except: txid_a24_2 = '0'
        self.check_invalid('no active orders, cancel-everything, positive amounts, TMSC, TMSC (!)', txid_a24_2)

        try:    txid_a24_3 = entity_a1.trade('2.00000000', MSC,  '2.00000000', TMSC,  CANCEL_4)
        except: txid_a24_3 = '0'
        self.check_invalid('no active orders, cancel-everything, positive amounts, cross ecosystem (!)', txid_a24_3)

        try:    txid_a24_4 = entity_a1.trade('2.00000000', 67,   '2.00000000', 68,    CANCEL_4)
        except: txid_a24_4 = '0'
        self.check_invalid('no active orders, cancel-everything, positive amounts, non-existing pair (!)', txid_a24_4)

        try:    txid_a24_5 = entity_a1.trade('0.00000000', TMSC, '0.00000000', TDiv1, CANCEL_4)
        except: txid_a24_5 = '0'
        self.check_invalid('no active orders, cancel-everything, zero amounts (!), test ecosystem', txid_a24_5)

        try:    txid_a24_6 = entity_a1.trade('0.00000000', TMSC, '0.00000000', TMSC,  CANCEL_4)
        except: txid_a24_6 = '0'
        self.check_invalid('no active orders, cancel-everything, zero amounts (!), TMSC, TMSC (!)', txid_a24_6)

        try:    txid_a24_7 = entity_a1.trade('0.00000000', MSC,  '0.00000000', TMSC,  CANCEL_4)
        except: txid_a24_7 = '0'
        self.check_invalid('no active orders, cancel-everything, zero amounts (!), cross ecosystem (!)', txid_a24_7)

        try:    txid_a24_8 = entity_a1.trade('0.00000000', 67,   '0.00000000', 68,    CANCEL_4)
        except: txid_a24_8 = '0'
        self.check_invalid('no active orders, cancel-everything, zero amounts (!), non-existing pair (!)', txid_a24_8)

        TestInfo.StopExpectation()


    # A25-26
    def test_invalid_cancel_pair_no_active_offers(self):
        """Tests invalidation of transactions with CANCEL-PAIR command, but no active, matching offers."""
        entity_a1 = self.entities[1]

        TestInfo.ExpectFail()

        try:    txid_a25 = entity_a1.trade('2.00000000', TMSC,  '2.00000000', TDiv1, CANCEL_3)
        except: txid_a25 = '0'
        self.check_invalid('no active orders for currency pair', txid_a25)

        try:    txid_a26 = entity_a1.trade('2.00000000', TDiv1, '2.00000000', TMSC,  CANCEL_3)
        except: txid_a26 = '0'
        self.check_invalid('no active orders for currency pair', txid_a26)

        TestInfo.StopExpectation()


    # A27-28
    def test_invalid_cancel_no_active_offers(self):
        """"Tests invalidation of transactions with CANCEL command, but no active, matching offers."""
        entity_a1 = self.entities[1]

        TestInfo.ExpectFail()

        try:    txid_a27 = entity_a1.trade('2.00000000', TDiv2, '2.00000000', TMSC,  CANCEL_2)
        except: txid_a27 = '0'
        self.check_invalid('no active orders for currency pair and price', txid_a27)

        try:    txid_a28 = entity_a1.trade('2.00000000', TMSC,  '2.00000000', TDiv2, CANCEL_2)
        except: txid_a28 = '0'
        self.check_invalid('no active orders for currency pair and price', txid_a28)

        TestInfo.StopExpectation()


    # A29-30
    def test_invalid_add_same_currency(self):
        """Tests invalidation of transactions with the same property on both sides of an offer."""
        entity_a1 = self.entities[1]

        TestInfo.ExpectFail()

        try:    txid_a29 = entity_a1.trade('1.00000000', TDiv1, '2.00000000', TDiv1, ADD_1)
        except: txid_a29 = '0'
        self.check_invalid('same currency (and neither is TMSC)', txid_a29)

        try:    txid_a30 = entity_a1.trade('1.00000000', TMSC,  '2.00000000', TMSC,  ADD_1)
        except: txid_a30 = '0'
        self.check_invalid('same currency', txid_a30)

        TestInfo.StopExpectation()


    # A31-32
    def test_invalid_add_zero_amount(self):
        """Tests invalidation of offers with zero amounts."""
        entity_a1 = self.entities[1]

        TestInfo.ExpectFail()

        try:    txid_a31 = entity_a1.trade('0.00000000', TDiv1, '1.00000000', TMSC, ADD_1)
        except: txid_a31 = '0'
        self.check_invalid('amount for sale is 0.0', txid_a31)

        try:    txid_a32 = entity_a1.trade('1.00000000', TDiv1, '0.00000000', TMSC, ADD_1)
        except: txid_a32 = '0'
        self.check_invalid('amount desired is 0.0', txid_a32)

        TestInfo.StopExpectation()


    # A33-34
    def test_invalid_add_bitcoin(self):
        """Tests invalidation of offers with bitcoin."""
        entity_a1 = self.entities[1]

        TestInfo.ExpectFail()

        try:    txid_a33 = entity_a1.trade('1.00000000', BTC,  '1.00000000', TMSC, ADD_1)
        except: txid_a33 = '0'
        self.check_invalid('desired property is bitcoin', txid_a33)

        try:    txid_a34 = entity_a1.trade('1.00000000', TMSC, '1.00000000', BTC,  ADD_1)
        except: txid_a34 = '0'
        self.check_invalid('property for sale is bitcoin', txid_a34)

        TestInfo.StopExpectation()


    # A35-36
    def test_invalid_add_cross_ecosystem(self):
        """Tests invalidation of offers with properties that are not in the same ecosystem."""
        entity_a1 = self.entities[1]

        TestInfo.ExpectFail()

        try:    txid_a35 = entity_a1.trade('1.00000000', MSC,   '1.00000000', TDiv1, ADD_1)
        except: txid_a35 = '0'
        self.check_invalid('cross ecosystem (main, test) (MSC, TDiv1)', txid_a35)

        try:    txid_a36 = entity_a1.trade('1.00000000', TDiv1, '1.00000000', MSC,   ADD_1)
        except: txid_a36 = '0'
        self.check_invalid('cross ecosystem (test, main) (MSC, TDiv1)', txid_a36)

        TestInfo.StopExpectation()


    # A38-41
    def test_invalid_insufficient_balance(self):
        """Tests invalidation of offers due to insufficient balance."""
        entity_a1 = self.entities[1]

        TestInfo.ExpectFail()

        try:    txid_a38 = entity_a1.trade('1', TIndiv2, '1.00000000', TMSC, ADD_1)
        except: txid_a38 = '0'
        self.check_invalid('A1 does not have any TIndiv2', txid_a38)

        try:    txid_a39 = entity_a1.trade('2001', TIndiv1, '1.00000000', TMSC, ADD_1)
        except: txid_a39 = '0'
        self.check_invalid('A1 does not have enough TIndiv1', txid_a39)

        try:    txid_a40 = entity_a1.trade('1.00000000', TDiv2, '1.00000000', TMSC, ADD_1)
        except: txid_a40 = '0'
        self.check_invalid('A1 does not have any TDiv2', txid_a40)

        try:    txid_a41 = entity_a1.trade('100.00000001', TDiv1, '1.00000000', TMSC, ADD_1)
        except: txid_a41 = '0'
        self.check_invalid('A1 does not have enough TDiv1', txid_a41)

        TestInfo.StopExpectation()


    # NOTE: The following tests do not reflect the test plan strictly, because there are no negative amounts
    # when using unsigned numbers.

    def test_invalid_amount_too_large(self):
        """Tests invalidation of offers with amounts that are out of range.

        NOTE: a different number than max. + 1 (9223372036854775808, 92233720368.54775808) was chosen,
        because max. + 1, represented as unsigned integer 0x8000000000000000, is basically also tested
        in test_invalid_negative_zero().

        The data is submitted via RPC command trade_MP."""
        entity_a1 = self.entities[1]
        entity_a3 = self.entities[3]

        # TODO: StrToInt64, which is used in trade_MP, parses out-of-range amounts as 0.

        TestInfo.ExpectFail()

        try:    txid_a42 = entity_a1.trade('0.00000001', TDiv1, '92233720368.54780000', TMSC, ADD_1)
        except: txid_a42 = '0'
        self.check_invalid('amount desired is too large (92233720368.54780000 TMSC)', txid_a42)

        try:    txid_a43 = entity_a3.trade('92233720368.54780000', TDivMax, '0.00000001', TMSC, ADD_1)
        except: txid_a43 = '0'
        self.check_invalid('amount for sale is too large (92233720368.54780000 TDivMax)', txid_a43)

        try:    txid_a44 = entity_a1.trade('1', TIndiv1, '92233720368.54780000', TMSC, ADD_1)
        except: txid_a44 = '0'
        self.check_invalid('amount desired is too large (92233720368.54780000 TMSC)', txid_a44)

        try:    txid_a45 = entity_a3.trade('9223372036854780000', TIndivMax, '0.00000001', TMSC, ADD_1)
        except: txid_a45 = '0'
        self.check_invalid('amount for sale is too large (9223372036854780000 TIndivMax)', txid_a45)

        try:    txid_a46 = entity_a1.trade('92233720368.54780000', TMSC, '92233720368.54780000', TDiv1, ADD_1)
        except: txid_a46 = '0'
        self.check_invalid('both amounts are too large', txid_a46)

        try:    txid_a47 = entity_a1.trade('92233720368.54780000', TMSC, '9223372036854780000', TIndiv1, ADD_1)
        except: txid_a47 = '0'
        self.check_invalid('both amounts are too large', txid_a47)

        TestInfo.StopExpectation()


    def test_invalid_amount_too_large_raw(self):
        """Tests invalidation of offers with amounts that are out of range.

        NOTE: a different number than max. + 1 (9223372036854775808, 92233720368.54775808) was chosen,
        because max. + 1, represented as unsigned integer 0x8000000000000000, is basically also tested
        in test_invalid_negative_zero().

        The data is submitted as raw transaction to get around RPC interface checks."""
        entity_a1 = self.entities[1]
        entity_a3 = self.entities[3]

        TestInfo.ExpectFail()

        #          entity_a1.trade('0.00000001', TDiv1, '92233720368.54780000', TMSC, ADD_1)
        txid_a42 = entity_a1.node.sendrawtx_MP(entity_a1.address,
                                               '0000001580000007000000000000000100000002800000000000106001')
        self.check_invalid('amount desired is too large (0x8000000000001060 TMSC)', txid_a42)

        #          entity_a3.trade('92233720368.54780000', TDivMax, '0.00000001', TMSC, ADD_1)
        txid_a43 = entity_a3.node.sendrawtx_MP(entity_a3.address,
                                               '000000158000000a800000000000106000000002000000000000000101')
        self.check_invalid('amount for sale is too large (0x8000000000001060 TDivMax)', txid_a43)

        #          entity_a1.trade('1', TIndiv1, '92233720368.54780000', TMSC, ADD_1)
        txid_a44 = entity_a1.node.sendrawtx_MP(entity_a1.address,
                                               '0000001580000003000000000000000100000002800000000000106001')
        self.check_invalid('amount desired is too large (0x8000000000001060 TMSC)', txid_a44)

        #          entity_a3.trade('9223372036854780000', TIndivMax, '0.00000001', TMSC, ADD_1)
        txid_a45 = entity_a3.node.sendrawtx_MP(entity_a3.address,
                                               '0000001580000006800000000000106000000002000000000000000101')
        self.check_invalid('amount for sale is too large (0x8000000000001060 TIndivMax)', txid_a45)

        #          entity_a1.trade('92233720368.54780000', TMSC, '92233720368.54780000', TDiv1, ADD_1)
        txid_a46 = entity_a1.node.sendrawtx_MP(entity_a1.address,
                                               '0000001500000002800000000000106080000007800000000000106001')
        self.check_invalid('both amounts are too large (0x8000000000001060 TMSC, 0x8000000000001060 TDiv1)', txid_a46)

        #          entity_a1.trade('92233720368.54780000', TMSC, '9223372036854780000', TIndiv1, ADD_1)
        txid_a47 = entity_a1.node.sendrawtx_MP(entity_a1.address,
                                               '0000001500000002800000000000106080000003800000000000106001')
        self.check_invalid('both amounts are too large (0x8000000000001060 TMSC, 0x8000000000001060 TIndiv1)', txid_a47)

        TestInfo.StopExpectation()


    def test_invalid_amount_negative(self):
        """Tests invalidation of offers with negative amounts."""
        entity_a1 = self.entities[1]
        entity_a3 = self.entities[3]

        # NOTE: StrToInt64, which is used in trade_MP, parses negative amounts as 0.

        TestInfo.ExpectFail()

        try:    txid_a48 = entity_a1.trade('0.00000001', TDiv1, '-0.00000001', TMSC, ADD_1)
        except: txid_a48 = '0'
        self.check_invalid('amount desired is negative (-0.00000001 TMSC)', txid_a48)

        try:    txid_a49 = entity_a3.trade('-0.00000001', TDivMax, '0.00000001', TMSC, ADD_1)
        except: txid_a49 = '0'
        self.check_invalid('amount for sale is negative (-0.00000001 TDivMax)', txid_a49)

        try:    txid_a50 = entity_a1.trade('1', TIndiv1, '-0.00000001', TMSC, ADD_1)
        except: txid_a50 = '0'
        self.check_invalid('amount desired is negative (-0.00000001 TMSC)', txid_a50)

        try:    txid_a51 = entity_a3.trade('-1', TIndivMax, '0.00000001', TMSC, ADD_1)
        except: txid_a51 = '0'
        self.check_invalid('amount for sale is negative (-1 TIndivMax)', txid_a51)

        try:    txid_a52 = entity_a1.trade('-0.00000001', TMSC, '-0.00000001', TDiv1, ADD_1)
        except: txid_a52 = '0'
        self.check_invalid('both amounts are negative (-0.00000001 TMSC, -0.00000001 TDiv1)', txid_a52)

        try:    txid_a53 = entity_a1.trade('-0.00000001', TMSC, '-1', TIndiv1, ADD_1)
        except: txid_a53 = '0'
        self.check_invalid('both amounts are negative (-0.00000001 TMSC,-1 TIndiv1)', txid_a53)

        TestInfo.StopExpectation()


    def test_invalid_negative_zero(self):
        """Tests invalidation of offers with amounts that might be interpreted as negative zero.

        NOTE: there is no negative zero in two's complement representation, but it is simulated with amounts of
        0x8000000000000000 and 0xffffffffffffffff, which are interpreted as out-of-range or negative number. Due
        to this behavior, this test currently acts as enhancement for out-of-range and negative-number tests.

        The data is submitted as raw transaction to get around RPC interface checks."""
        entity_a1 = self.entities[1]
        entity_a3 = self.entities[3]

        # TODO: Split, rename or merge this test with other out-of-range tests.

        TestInfo.ExpectFail()

        #                    entity_a1.trade('-0.00000000', TMSC, '1.00000000', TDiv1, ADD_1)
        try:    txid_a54_1 = entity_a1.node.sendrawtx_MP(entity_a1.address,
                                                         '00000015000000028000000000000000800000070000000005f5e10001')
        except: txid_a54_1 = '0'
        self.check_invalid('amount for sale is not within valid range (0x8000000000000000 TMSC)', txid_a54_1)

        #                    entity_a1.trade('-0.00000000', TMSC, '1.00000000', TDiv1, ADD_1)
        try:    txid_a54_2 = entity_a1.node.sendrawtx_MP(entity_a1.address,
                                                         '0000001500000002ffffffffffffffff800000070000000005f5e10001')
        except: txid_a54_2 = '0'
        self.check_invalid('amount for sale is not within valid range (0xffffffffffffffff TMSC)', txid_a54_2)

        #                    entity_a3.trade('-0', TIndivMax, '1.00000000', TMSC, ADD_1)
        try:    txid_a54_3 = entity_a3.node.sendrawtx_MP(entity_a3.address,
                                                         '00000015800000068000000000000000000000020000000005f5e10001')
        except: txid_a54_3 = '0'
        self.check_invalid('amount for sale is not within valid range (0x8000000000000000 TIndivMax)', txid_a54_3)

        #                    entity_a3.trade('-0', TIndivMax, '1.00000000', TMSC, ADD_1)
        try:    txid_a54_4 = entity_a3.node.sendrawtx_MP(entity_a3.address,
                                                         '0000001580000006ffffffffffffffff000000020000000005f5e10001')
        except: txid_a54_4 = '0'
        self.check_invalid('amount for sale is not within valid range (0xffffffffffffffff TIndivMax)', txid_a54_4)

        #                    entity_a1.trade('1.00000000', TMSC, '-0', TIndiv1, ADD_1)
        try:    txid_a55_1 = entity_a1.node.sendrawtx_MP(entity_a1.address,
                                                         '00000015000000020000000005f5e10080000003800000000000000001')
        except: txid_a55_1 = '0'
        self.check_invalid('amount desired is not within valid range (0x8000000000000000 TMSC)', txid_a55_1)

        #                    entity_a1.trade('1.00000000', TMSC, '-0', TIndiv1, ADD_1)
        try:    txid_a55_2 = entity_a1.node.sendrawtx_MP(entity_a1.address,
                                                         '00000015000000020000000005f5e10080000003ffffffffffffffff01')
        except: txid_a55_2 = '0'
        self.check_invalid('amount desired is not within valid range (0xffffffffffffffff TMSC)', txid_a55_2)

        #                    entity_a3.trade('1.00000000', TMSC, '-1.00000000', TDivMax, ADD_1)
        try:    txid_a55_3 = entity_a3.node.sendrawtx_MP(entity_a3.address,
                                                         '00000015000000020000000005f5e1008000000a800000000000000001')
        except: txid_a55_3 = '0'
        self.check_invalid('amount desired is not within valid range (0x8000000000000000 TMSC)', txid_a55_3)

        #                    entity_a3.trade('1.00000000', TMSC, '-1.00000000', TDivMax, ADD_1)
        try:    txid_a55_4 = entity_a3.node.sendrawtx_MP(entity_a3.address,
                                                         '00000015000000020000000005f5e1008000000affffffffffffffff01')
        except: txid_a55_4 = '0'
        self.check_invalid('amount desired is not within valid range (0xffffffffffffffff TMSC)', txid_a55_4)

        TestInfo.StopExpectation()

    # A59-65
    def test_new_orders_for_divisible(self):
        """Tests creation of offers with divisible amounts.

        There is also one invalid attempt to cancel an offer where no active order for that pair and price exists."""
        entity_a1 = self.entities[1]

        self.check_balance(entity_a1.address, TMSC,  '150.00000000', '0.00000000')
        self.check_balance(entity_a1.address, TDiv1, '100.00000000', '0.00000000')
        self.check_balance(entity_a1.address, TIndiv1,  '1000', '0')

        # A59
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

        TestInfo.ExpectFail()

        # A60
        try:    txid_a60 = entity_a1.trade('10.00000001', TMSC, '9.99999999', TDiv1, CANCEL_2)
        except: txid_a60 = '0'
        self.check_invalid('no active orders for that pair and price', txid_a60)

        TestInfo.StopExpectation()

        # A61
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

        # A63
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

        # A64
        entity_a1.trade('5', TIndiv1, '6.00000000', TMSC)
        self.generate_block()
        #
        #
        # A1:   SELL   5 TIndiv1   @   1.20000000 TMSC/TIndiv1   (total:  6.0 TMSC)  <<  added
        #
        #
        self.check_balance(entity_a1.address, TMSC, '150.00000000',  '0.00000000')
        self.check_balance(entity_a1.address, TIndiv1,  '995', '5')

        # A65
        entity_a1.trade('1.00000000', TDiv1, '0.00000001', TMSC, CANCEL_2)
        self.generate_block()
        #
        #
        # A1:   SELL    3.00000000 TDiv1   @   1.00000000 TMSC/TDiv1   (total:  3.00000000 TMSC)
        # A1:   SELL   10.00000000 TDiv1   @   1.00000000 TMSC/TDiv1   (total: 10.00000000 TMSC)
        # A1:   SELL    1.00000000 TDiv1   @   0.00000001 TMSC/TDiv1   (total:  0.00000001 TMSC)
        #
        # A1:   CANCEL  1.00000000 TDiv1   @   0.00000001 TMSC/TDiv1   (total:  0.00000001 TMSC)  <<  pending
        #
        # =>
        #
        # A1:   SELL    3.00000000 TDiv1   @   1.00000000 TMSC/TDiv1   (total:  3.00000000 TMSC)
        # A1:   SELL   10.00000000 TDiv1   @   1.00000000 TMSC/TDiv1   (total: 10.00000000 TMSC)
        #
        #
        self.check_balance(entity_a1.address, TMSC, '150.00000000',  '0.00000000')
        self.check_balance(entity_a1.address, TDiv1, '87.00000000', '13.00000000')


    # A68-74
    def test_match_divisible_at_same_unit_price(self):
        """Tests matching and execution of orders at the same unit price.

        There is also one invalid attempt to cancel an offer where no active order for that pair and price exists."""
        entity_a1 = self.entities[1]
        entity_a2 = self.entities[2]
        entity_a3 = self.entities[3]

        self.check_balance(entity_a1.address, TMSC, '150.00000000',  '0.00000000')
        self.check_balance(entity_a2.address, TMSC,  '50.00000000',  '0.00000000')
        self.check_balance(entity_a3.address, TMSC,  '25.00000000',  '0.00000000')
        self.check_balance(entity_a1.address, TDiv1, '87.00000000', '13.00000000')
        self.check_balance(entity_a2.address, TDiv1, '50.00000000',  '0.00000000')
        self.check_balance(entity_a3.address, TDiv1,  '0.00000000',  '0.00000000')

        # A68
        entity_a1.trade('1.00000000', TMSC, '1.00000000', TDiv1)
        self.generate_block()
        #
        #
        # A1:   SELL    3.00000000 TDiv1   @   1.00000000 TMSC/TDiv1   (total:  3.00000000 TMSC)
        # A1:   SELL   10.00000000 TDiv1   @   1.00000000 TMSC/TDiv1   (total: 10.00000000 TMSC)
        #
        # A1;   BUY     1.00000000 TDiv1   @   1.00000000 TMSC/TDiv1   (total:  1.00000000 TMSC)  <<  pending
        #
        # =>
        #
        # A1    BUYS    1.00000000 TDiv1   @   1.00000000 TMSC/TDiv1   (total:  1.00000000 TMSC)
        #
        # =>
        #
        # A1:   SELL    3.00000000 TDiv1   @   1.00000000 TMSC/TDiv1   (total:  3.00000000 TMSC)
        # A1:   SELL    9.00000000 TDiv1   @   1.00000000 TMSC/TDiv1   (total:  9.00000000 TMSC)  <<  updated
        #
        #

        # Movements:
        # A1->A1: 1.00000000 TMSC, A1->A1: 1.00000000 TDiv1
        #
        self.check_balance(entity_a1.address, TMSC, '150.00000000',  '0.00000000')
        self.check_balance(entity_a1.address, TDiv1, '88.00000000', '12.00000000')

        # A69
        entity_a2.trade('1.00000000', TMSC, '1.00000000', TDiv1)
        self.generate_block()
        #
        #
        # A1:   SELL    3.00000000 TDiv1   @   1.00000000 TMSC/TDiv1   (total:  3.00000000 TMSC)
        # A1:   SELL    9.00000000 TDiv1   @   1.00000000 TMSC/TDiv1   (total:  9.00000000 TMSC)
        #
        # A2;   BUY     1.00000000 TDiv1   @   1.00000000 TMSC/TDiv1   (total:  1.00000000 TMSC)  <<  pending
        #
        # =>
        #
        # A2    BUYS    1.00000000 TDiv1   @   1.00000000 TMSC/TDiv1   (total:  1.00000000 TMSC)
        #
        # =>
        #
        # A1:   SELL    3.00000000 TDiv1   @   1.00000000 TMSC/TDiv1   (total:  3.00000000 TMSC)
        # A1:   SELL    8.00000000 TDiv1   @   1.00000000 TMSC/TDiv1   (total:  8.00000000 TMSC)  <<  updated
        #
        #

        # Movements:
        # A2->A1: 1.00000000 TMSC, A1->A2: 1.00000000 TDiv1
        #
        self.check_balance(entity_a1.address, TMSC, '151.00000000',  '0.00000000')
        self.check_balance(entity_a2.address, TMSC,  '49.00000000',  '0.00000000')
        self.check_balance(entity_a1.address, TDiv1, '88.00000000', '11.00000000')
        self.check_balance(entity_a2.address, TDiv1, '51.00000000',  '0.00000000')

        # A71
        entity_a2.trade('6.00000000', TDiv1, '6.00000000', TMSC)
        self.generate_block()
        #
        #
        # A2:   SELL    6.00000000 TDiv1   @   1.00000000 TMSC/TDiv1   (total:  6.00000000 TMSC)  <<  added
        # A1:   SELL    3.00000000 TDiv1   @   1.00000000 TMSC/TDiv1   (total:  3.00000000 TMSC)
        # A1:   SELL    8.00000000 TDiv1   @   1.00000000 TMSC/TDiv1   (total:  8.00000000 TMSC)
        #
        #
        self.check_balance(entity_a1.address, TMSC, '151.00000000',  '0.00000000')
        self.check_balance(entity_a2.address, TMSC,  '49.00000000',  '0.00000000')
        self.check_balance(entity_a1.address, TDiv1, '88.00000000', '11.00000000')
        self.check_balance(entity_a2.address, TDiv1, '45.00000000',  '6.00000000')

        # A73
        entity_a3.trade('0.50000000', TMSC, '0.50000000', TDiv1)
        self.generate_block()
        #
        #
        # A2:   SELL    6.00000000 TDiv1   @   1.00000000 TMSC/TDiv1   (total:  6.00000000 TMSC)
        # A1:   SELL    3.00000000 TDiv1   @   1.00000000 TMSC/TDiv1   (total:  3.00000000 TMSC)
        # A1:   SELL    8.00000000 TDiv1   @   1.00000000 TMSC/TDiv1   (total:  8.00000000 TMSC)
        #
        # A3;   BUY     0.50000000 TDiv1   @   1.00000000 TMSC/TDiv1   (total:  0.50000000 TMSC)  <<  pending
        #
        # =>
        #
        # A3    BUYS    0.50000000 TDiv1   @   1.00000000 TMSC/TDiv1   (total:  0.50000000 TMSC)
        #
        # =>
        #
        # A2:   SELL    6.00000000 TDiv1   @   1.00000000 TMSC/TDiv1   (total:  6.00000000 TMSC)
        # A1:   SELL    3.00000000 TDiv1   @   1.00000000 TMSC/TDiv1   (total:  3.00000000 TMSC)
        # A1:   SELL    7.50000000 TDiv1   @   1.00000000 TMSC/TDiv1   (total:  7.50000000 TMSC)  <<  updated
        #
        #

        # Movements:
        # A3->A1: 0.50000000 TMSC, A1->A3: 0.50000000 TDiv1
        #
        self.check_balance(entity_a1.address, TMSC, '151.50000000',  '0.00000000')
        self.check_balance(entity_a3.address, TMSC,  '24.50000000',  '0.00000000')
        self.check_balance(entity_a1.address, TDiv1, '88.00000000', '10.50000000')
        self.check_balance(entity_a3.address, TDiv1,  '0.50000000',  '0.00000000')

        # A74
        entity_a3.trade('11.50000000', TMSC, '11.50000000', TDiv1)
        self.generate_block()
        #
        #
        # A2:   SELL    6.00000000 TDiv1   @   1.00000000 TMSC/TDiv1   (total:  6.00000000 TMSC)
        # A1:   SELL    3.00000000 TDiv1   @   1.00000000 TMSC/TDiv1   (total:  3.00000000 TMSC)
        # A1:   SELL    7.50000000 TDiv1   @   1.00000000 TMSC/TDiv1   (total:  7.50000000 TMSC)
        #
        # A3;   BUY    11.50000000 TDiv1   @   1.00000000 TMSC/TDiv1   (total: 11.50000000 TMSC)  <<  pending
        #
        # =>
        #
        # A3    BUYS    7.50000000 TDiv1   @   1.00000000 TMSC/TDiv1   (total:  7.50000001 TMSC)
        # A3    BUYS    3.00000000 TDiv1   @   1.00000000 TMSC/TDiv1   (total:  3.00000000 TMSC)
        # A3    BUYS    1.00000000 TDiv1   @   1.00000000 TMSC/TDiv1   (total:  1.00000000 TMSC)
        #
        # =>
        #
        # A2:   SELL    5.00000000 TDiv1   @   1.00000000 TMSC/TDiv1   (total:  5.00000000 TMSC)  <<  updated
        #
        #

        # Movements:
        # A3->A1: 7.50000000 TMSC, A1->A3: 7.50000000 TDiv1
        # A3->A1: 3.00000000 TMSC, A1->A3: 3.00000000 TDiv1
        # A3->A2: 1.00000000 TMSC, A2->A3: 1.00000000 TDiv1
        #
        self.check_balance(entity_a1.address, TMSC, '162.00000000', '0.00000000')
        self.check_balance(entity_a2.address, TMSC,  '50.00000000', '0.00000000')
        self.check_balance(entity_a3.address, TMSC,  '13.00000000', '0.00000000')
        self.check_balance(entity_a1.address, TDiv1, '88.00000000', '0.00000000')
        self.check_balance(entity_a2.address, TDiv1, '45.00000000', '5.00000000')
        self.check_balance(entity_a3.address, TDiv1, '12.00000000', '0.00000000')


    # A77-80
    def test_match_divisible_at_better_unit_price(self):
        """Tests matching and execution of orders at a better unit price.

        There is also one valid CANCEL operation."""
        entity_a1 = self.entities[1]
        entity_a2 = self.entities[2]
        entity_a3 = self.entities[3]
        #
        # Orderbook:
        #
        # A1:   SELL   5 TIndiv1   @   1.20000000 TMSC/TIndiv1   (total:  6.0 TMSC)
        #
        # A2:   SELL   5.00000000 TDiv1   @   1.00000000 TMSC/TDiv1   (total:  5.00000000 TMSC)
        #
        #
        self.check_balance(entity_a1.address, TMSC, '162.00000000', '0.00000000')
        self.check_balance(entity_a2.address, TMSC,  '50.00000000', '0.00000000')
        self.check_balance(entity_a3.address, TMSC,  '13.00000000', '0.00000000')
        self.check_balance(entity_a1.address, TDiv1, '88.00000000', '0.00000000')
        self.check_balance(entity_a2.address, TDiv1, '45.00000000', '5.00000000')
        self.check_balance(entity_a3.address, TDiv1, '12.00000000', '0.00000000')

        # A77
        entity_a3.trade('2.00000000', TMSC, '1.00000000', TDiv1)
        self.generate_block()
        #
        #
        # A2:   SELL   5.00000000 TDiv1   @   1.00000000 TMSC/TDiv1   (total:  5.00000000 TMSC)
        #
        # A3;   BUY    1.00000000 TDiv1   @   2.00000000 TMSC/TDiv1   (total:  2.00000000 TMSC)  <<  pending
        #
        #              ^ TODO: "BUY" looks strange in this context, because in fact 2.0 TMSC are offered.
        # =>
        #
        # A3    BUYS   2.00000000 TDiv1   @   1.00000000 TMSC/TDiv1   (total:  2.00000000 TMSC)
        #
        # =>
        #
        # A2:   SELL   3.00000000 TDiv1   @   1.00000000 TMSC/TDiv1   (total:  3.00000000 TMSC)  <<  updated
        #
        #

        # Movements:
        # A3->A2: 2.00000000 TMSC, A2->A3: 2.00000000 TDiv1
        #
        self.check_balance(entity_a2.address, TMSC,  '52.00000000', '0.00000000')
        self.check_balance(entity_a3.address, TMSC,  '11.00000000', '0.00000000')
        self.check_balance(entity_a2.address, TDiv1, '45.00000000', '3.00000000')
        self.check_balance(entity_a3.address, TDiv1, '14.00000000', '0.00000000')

        # A78
        entity_a3.trade('0.00000002', TMSC, '0.00000001', TDiv1)
        self.generate_block()
        #
        #
        # A2:   SELL   3.00000000 TDiv1   @   1.00000000 TMSC/TDiv1   (total:  3.00000000 TMSC)
        #
        # A3:   BUY    0.00000001 TDiv1   @   2.00000000 TMSC/TDiv1   (total:  0.00000002 TMSC)  <<  pending
        #
        # =>
        #
        # A3    BUYS   0.00000002 TDiv1   @   1.00000000 TMSC/TDiv1   (total:  0.00000002 TMSC)
        #
        # =>
        #
        # A2:   SELL   2.99999998 TDiv1   @   1.00000000 TMSC/TDiv1   (total:  2.99999998 TMSC)  <<  updated
        #
        #

        # Movements:
        # A3->A2: 0.00000002 TMSC, A2->A3: 0.00000002 TDiv1
        #
        self.check_balance(entity_a2.address, TMSC,  '52.00000002', '0.00000000')
        self.check_balance(entity_a3.address, TMSC,  '10.99999998', '0.00000000')
        self.check_balance(entity_a2.address, TDiv1, '45.00000000', '2.99999998')
        self.check_balance(entity_a3.address, TDiv1, '14.00000002', '0.00000000')

        # A79
        entity_a3.trade('5.00000000', TMSC, '4.00000000', TDiv1)
        self.generate_block()
        #
        #
        # A2:   SELL   2.99999998 TDiv1   @   1.00000000 TMSC/TDiv1   (total:  2.99999998 TMSC)
        #
        # A3:   BUY    4.00000000 TDiv1   @   1.25000000 TMSC/TDiv1   (total:  5.00000000 TMSC)  <<  pending
        #
        # =>
        #
        # A3    BUYS   2.99999998 TDiv1   @   1.00000000 TMSC/TDiv1   (total:  2.99999998 TMSC)
        #
        # =>
        #
        # A3:   BUY    1.600000016 TDiv1  @   1.25000000 TMSC/TDiv1   (total:  2.00000002 TMSC)  <<  added
        #
        #

        # Movements:
        # A3->A2: 2.99999998 TMSC, A2->A3: 2.99999998 TDiv1
        #
        self.check_balance(entity_a2.address, TMSC,  '55.00000000', '0.00000000')
        self.check_balance(entity_a3.address, TMSC,   '5.99999998', '2.00000002')
        self.check_balance(entity_a2.address, TDiv1, '45.00000000', '0.00000000')
        self.check_balance(entity_a3.address, TDiv1, '17.00000000', '0.00000000')

        # A78
        entity_a3.trade('5.00000000', TMSC, '4.00000000', TDiv1, CANCEL_2)
        self.generate_block()
        #
        #
        # A3:   BUY    1.600000016 TDiv1  @   1.25000000 TMSC/TDiv1   (total:  2.00000002 TMSC)
        #
        # A3:   CANCEL 4.00000000  TDiv1  @   1.25000000 TMSC/TDiv1   (total:  5.00000000 TMSC)  <<  pending
        #
        # =>
        #
        # No more open orders for TDiv1 / TMSC
        #
        #
        self.check_balance(entity_a3.address, TMSC,   '8.00000000', '0.00000000')
        self.check_balance(entity_a3.address, TDiv1, '17.00000000', '0.00000000')


    # 83-90
    def test_match_divisible_with_three(self):
        """Tests matching and execution of orders with more than one match.

        Tests also invalidation of CANCEL-PAIR commands where no matching, open orders exists."""
        entity_a1 = self.entities[1]
        entity_a2 = self.entities[2]
        entity_a3 = self.entities[3]
        #
        # Orderbook:
        #
        # A1:   SELL   5 TIndiv1   @   1.20000000 TMSC/TIndiv1   (total:  6.0 TMSC)
        #
        #
        self.check_balance(entity_a1.address, TMSC,  '162.00000000', '0.00000000')
        self.check_balance(entity_a2.address, TMSC,   '55.00000000', '0.00000000')
        self.check_balance(entity_a3.address, TMSC,    '8.00000000', '0.00000000')
        self.check_balance(entity_a1.address, TDiv3,   '0.00000000', '0.00000000')
        self.check_balance(entity_a2.address, TDiv3, '200.00000000', '0.00000000')
        self.check_balance(entity_a3.address, TDiv3, '200.00000000', '0.00000000')

        # NOTE: Negative amounts are currently parsed as 0 by StrToInt64, but it should not matter in this context.

        TestInfo.ExpectFail()

        # A83 (amounts should be ignored in CANCEL-PAIR operations)
        try:    txid_a83 = entity_a2.trade('-0.00000001', TDiv3, '0.00000000', TMSC,  CANCEL_3)
        except: txid_a83 = '0'
        self.check_invalid('A2 does not have any open order of pair TDiv3 - TMSC', txid_a83)

        # A84 (amounts should be ignored in CANCEL-PAIR operations)
        try:    txid_a84 = entity_a3.trade('0.00000000', TDiv3, '-0.00000001', TMSC,  CANCEL_3)
        except: txid_a84 = '0'
        self.check_invalid('A3 does not have any open order of pair TDiv3 - TMSC', txid_a84)

        # A85 with zero amounts (amounts should be ignored in CANCEL-PAIR operations)
        try:    txid_a85_a = entity_a1.trade('0.00000000', TMSC, '0.00000000', TDiv3, CANCEL_3)
        except: txid_a85_a = '0'
        self.check_invalid('A1 does not have any open order of pair TMSC - TDiv3', txid_a85_a)

        # A85 with positive amounts (amounts should be ignored in CANCEL-PAIR operations)
        try:    txid_a85_b = entity_a1.trade('6.00000000', TMSC, '0.00000005', TDiv3, CANCEL_3)
        except: txid_a85_b = '0'
        self.check_invalid('A1 does not have any open order of pair TMSC - TDiv3', txid_a85_b)

        TestInfo.StopExpectation()

        # A86
        entity_a2.trade('10.00000000', TDiv3, '5.00000000', TMSC)
        self.generate_block()
        #
        #
        # A2:   SELL   10.00000000 TDiv3   @   0.50000000 TMSC/TDiv3   (total:  5.0 TMSC)  <<  added
        #
        #
        self.check_balance(entity_a2.address, TMSC,   '55.00000000',  '0.00000000')
        self.check_balance(entity_a2.address, TDiv3, '190.00000000', '10.00000000')

        # A87
        entity_a3.trade('10.00000000', TDiv3, '10.00000000', TMSC)
        self.generate_block()
        #
        #
        # A3:   SELL    10.00000000 TDiv3   @   1.00000000 TMSC/TDiv3   (total: 10.0 TMSC)  <<  added
        # A2:   SELL    10.00000000 TDiv3   @   0.50000000 TMSC/TDiv3   (total:  5.0 TMSC)
        #
        #
        self.check_balance(entity_a3.address, TMSC,    '8.00000000',  '0.00000000')
        self.check_balance(entity_a3.address, TDiv3, '190.00000000', '10.00000000')

        # A88
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

        # A89
        entity_a1.trade('60.00000000', TMSC, '120.00000001', TDiv3)
        self.generate_block()
        #
        #
        # A2:   SELL   15.00000000 TDiv3   @   1.50000000 TMSC/TDiv3   (total: 22.5 TMSC)
        # A3:   SELL   10.00000000 TDiv3   @   1.00000000 TMSC/TDiv3   (total: 10.0 TMSC)
        # A2:   SELL   10.00000000 TDiv3   @   0.50000000 TMSC/TDiv3   (total:  5.0 TMSC)
        #
        # A1:   BUY   120.00000001 TDiv3   @   0.49999999995833333333680555.. TMSC/TDiv3   (total: 60.0 TMSC)  <<  added
        #
        #
        self.check_balance(entity_a1.address, TMSC, '102.00000000', '60.00000000')
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
        # A1   BUYS   10.00000000 TDiv3   @   0.50000000 TMSC/TDiv3   (total:  5.0 TMSC)
        # A1   BUYS   10.00000000 TDiv3   @   1.00000000 TMSC/TDiv3   (total: 10.0 TMSC)
        # A1   BUYS   15.00000000 TDiv3   @   1.50000000 TMSC/TDiv3   (total: 22.5 TMSC)
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
        self.check_balance(entity_a1.address, TMSC,   '57.00000000', '67.50000000')
        self.check_balance(entity_a2.address, TMSC,   '82.50000000',  '0.00000000')
        self.check_balance(entity_a3.address, TMSC,   '18.00000000',  '0.00000000')
        self.check_balance(entity_a1.address, TDiv3,  '35.00000000',  '0.00000000')
        self.check_balance(entity_a2.address, TDiv3, '175.00000000',  '0.00000000')
        self.check_balance(entity_a3.address, TDiv3, '190.00000000',  '0.00000000')


    # A93-101
    def test_match_large_and_small_amounts(self):
        """Tests to use largest and smallest amounts, and new order sends more than amount desired
        by matched existing order."""
        entity_a2 = self.entities[2]
        entity_a3 = self.entities[3]

        # Make sure start state is as expected
        self.check_balance(entity_a2.address, TMSC,                       '82.50000000', '0.00000000')
        self.check_balance(entity_a3.address, TMSC,                       '18.00000000', '0.00000000')
        self.check_balance(entity_a2.address, TIndivMax,                   '0',          '0')
        self.check_balance(entity_a3.address, TIndivMax, '9223372036854775807',          '0')
        self.check_balance(entity_a2.address, TDivMax,                     '0.00000000', '0.00000000')
        self.check_balance(entity_a3.address, TDivMax,           '92233720368.54775807', '0.00000000')

        # A93
        entity_a3.trade('92233720368.54775807', TDivMax, '0.00000001', TMSC)
        self.generate_block()
        #
        #
        # A3:   SELL   92233720368.54775807 TDivMax   for   0.00000001 TMSC  <<  added
        #
        #
        self.check_balance(entity_a3.address, TDivMax, '0.00000000', '92233720368.54775807')

        # A94
        entity_a2.trade('0.00000001', TMSC, '92233720368.54775807', TDivMax)
        self.generate_block()
        #
        #
        # A3:   SELL   92233720368.54775807 TDivMax   for   0.00000001 TMSC
        #
        # A2:   BUY    92233720368.54775807 TDivMax   for   0.00000001 TMSC  <<  pending
        #
        # =>
        #
        # A2    BUYS   92233720368.54775807 TDivMax   for   0.00000001 TMSC
        #
        # =>
        #
        # No more open orders for TDivMax / TMSC
        #
        #

        # Movements:
        # A2->A3: 0.00000001 TMSC, A3->A2: 92233720368.54775807 TDivMax
        #
        self.check_balance(entity_a2.address, TMSC,             '82.49999999', '0.00000000')
        self.check_balance(entity_a3.address, TMSC,             '18.00000001', '0.00000000')
        self.check_balance(entity_a2.address, TDivMax, '92233720368.54775807', '0.00000000')
        self.check_balance(entity_a3.address, TDivMax,           '0.00000000', '0.00000000')

        # A95
        entity_a2.trade('92233720368.54775807', TDivMax, '0.00000001', TMSC)
        self.generate_block()
        #
        #
        # A2:   SELL   92233720368.54775807 TDivMax   for   0.00000001 TMSC  <<  added     @  1.084e-19 TMSC/TDivMax
        #
        #
        self.check_balance(entity_a2.address, TDivMax, '0.00000000', '92233720368.54775807')

        # A96
        entity_a3.trade('0.00000002', TMSC, '92233720368.54775807', TDivMax)
        self.generate_block()
        #
        #
        # A2:   SELL   92233720368.54775807 TDivMax   for   0.00000001 TMSC                @  1.084e-19 TMSC/TDivMax
        #
        # A3:   BUY    92233720368.54775807 TDivMax   for   0.00000002 TMSC  <<  pending   @  2.168e-19 TMSC/TDivMax
        #
        # =>
        #
        # A2    BUYS   92233720368.54775807 TDivMax   for   0.00000001 TMSC                @  1.084e-19 TMSC/TDivMax
        #
        # =>
        #
        # A2:   BUY    46116860184.27387904 TDivMax   for   0.00000001 TMSC  <<  added     @  2.168e-19 TMSC/TDivMax
        #
        #

        # Movements:
        # A3->A2: 0.00000001 TMSC, A2->A3: 92233720368.54775807 TDivMax
        #
        self.check_balance(entity_a2.address, TMSC,             '82.50000000', '0.00000000')
        self.check_balance(entity_a3.address, TMSC,             '17.99999999', '0.00000001')
        self.check_balance(entity_a2.address, TDivMax,           '0.00000000', '0.00000000')
        self.check_balance(entity_a3.address, TDivMax, '92233720368.54775807', '0.00000000')

        # A98
        entity_a3.trade('9223372036854775807', TIndivMax, '0.00000001', TMSC)
        self.generate_block()
        #
        #
        # A3:   SELL   9223372036854775807 TIndivMax   for   0.00000001 TMSC  <<  added
        #
        #
        self.check_balance(entity_a3.address, TIndivMax, '0', '9223372036854775807')

        # A99
        entity_a2.trade('0.00000001', TMSC, '9223372036854775807', TIndivMax)
        self.generate_block()
        #
        #
        # A3:   SELL   9223372036854775807 TIndivMax   for   0.00000001 TMSC
        #
        # A2:   BUY    9223372036854775807 TIndivMax   for   0.00000001 TMSC  <<  pending
        #
        # =>
        #
        # A2    BUYS   9223372036854775807 TIndivMax   for   0.00000001 TMSC
        #
        # =>
        #
        # No more open orders for TIndivMax / TMSC
        #
        #

        # Movements:
        # A2->A3: 0.00000001 TMSC, A3->A2: 9223372036854775807 TIndivMax
        #
        self.check_balance(entity_a2.address, TMSC,                       '82.49999999', '0.00000000')
        self.check_balance(entity_a3.address, TMSC,                       '18.00000000', '0.00000001')
        self.check_balance(entity_a2.address, TIndivMax, '9223372036854775807',          '0')
        self.check_balance(entity_a3.address, TIndivMax,                   '0',          '0')

        # A100
        entity_a2.trade('9223372036854775807', TIndivMax, '0.00000001', TMSC)
        self.generate_block()
        #
        #
        # A2:   SELL   9223372036854775807 TIndivMax   for   0.00000001 TMSC  <<  added    @  1.084e-27 TMSC/TIndivMax
        #
        #
        self.check_balance(entity_a2.address, TIndivMax, '0', '9223372036854775807')

        # A101
        entity_a3.trade('0.00000002', TMSC, '9223372036854775807', TIndivMax)
        self.generate_block()
        #
        #
        # A2:   SELL   9223372036854775807 TIndivMax   for   0.00000001 TMSC               @  1.084e-27 TMSC/TIndivMax
        #
        # A3:   BUY    9223372036854775807 TIndivMax   for   0.00000002 TMSC  <<  pending  @  2.168e-27 TMSC/TIndivMax
        #
        # =>
        #
        # A2    BUYS   9223372036854775807 TIndivMax   for   0.00000001 TMSC               @  1.084e-27 TMSC/TIndivMax
        #
        # =>
        #
        # A2:   BUY    4611686018427387903,5 TIndivMax   for   0.00000001 TMSC  <<  added  @  2.168e-27 TMSC/TIndivMax
        #
        #

        # Movements:
        # A3->A2: 0.00000001 TMSC, A2->A3: 9223372036854775807 TIndivMax
        #
        self.check_balance(entity_a2.address, TMSC,                       '82.50000000', '0.00000000')
        self.check_balance(entity_a3.address, TMSC,                       '17.99999998', '0.00000002')
        self.check_balance(entity_a2.address, TIndivMax,                   '0',          '0')
        self.check_balance(entity_a3.address, TIndivMax, '9223372036854775807',          '0')


    # A105-111
    def test_new_orders_for_indivisible(self):
        """Tests the creation of offers of properties with indivisible units."""
        entity_a1 = self.entities[1]
        #
        # Orderbook:
        #
        # A1:   SELL    5 TIndiv1   @   1.20000000 TMSC/TIndiv1   (total:  6.0 TMSC)  created with A64
        #
        #
        self.check_balance(entity_a1.address, TMSC,   '57.00000000', '67.50000000')
        self.check_balance(entity_a1.address, TIndiv1, '995', '5')

        # A105
        entity_a1.trade('10', TIndiv1, '10.00000000', TMSC)
        self.generate_block()
        #
        #
        # A1:   SELL    5 TIndiv1   @   1.20000000 TMSC/TIndiv1   (total:  6.0 TMSC)
        # A1:   SELL   10 TIndiv1   @   1.00000000 TMSC/TIndiv1   (total: 10.0 TMSC)  <<  added
        #
        #
        self.check_balance(entity_a1.address, TIndiv1, '985', '15')

        TestInfo.ExpectFail()

        # A106
        try:    txid_a104 = entity_a1.trade('10.00000001', TMSC, '10', TIndiv1, CANCEL_2)
        except: txid_a104 = '0'
        self.check_invalid('no active orders for that pair and price', txid_a104)

        TestInfo.StopExpectation()

        # A107
        entity_a1.trade('3', TIndiv1, '3.00000000', TMSC)
        self.generate_block()
        #
        #
        # A1:   SELL    5 TIndiv1   @   1.20000000 TMSC/TIndiv1   (total:  6.0 TMSC)
        # A1:   SELL    3 TIndiv1   @   1.00000000 TMSC/TIndiv1   (total:  3.0 TMSC)  <<  added
        # A1:   SELL   10 TIndiv1   @   1.00000000 TMSC/TIndiv1   (total: 10.0 TMSC)
        #
        #
        self.check_balance(entity_a1.address, TIndiv1, '982', '18')

        # A109
        entity_a1.trade('1', TIndiv1, '0.00000001', TMSC)
        self.generate_block()
        #
        #
        # A1:   SELL    5 TIndiv1   @   1.20000000 TMSC/TIndiv1   (total:  6.0        TMSC)
        # A1:   SELL    3 TIndiv1   @   1.00000000 TMSC/TIndiv1   (total:  3.0        TMSC)
        # A1:   SELL   10 TIndiv1   @   1.00000000 TMSC/TIndiv1   (total: 10.0        TMSC)
        # A1:   SELL    1 TIndiv1   @   0.00000001 TMSC/TIndiv1   (total:  0.00000001 TMSC)  <<  added
        #
        #
        self.check_balance(entity_a1.address, TIndiv1, '981', '19')

        # A110
        entity_a1.trade('6', TIndiv1, '7.00000000', TMSC)
        self.generate_block()
        #
        #
        # A1:   SELL    5 TIndiv1   @   1.20000000 TMSC/TIndiv1   (total:  6.0        TMSC)
        # A1:   SELL    6 TIndiv1   @   1.16666667 TMSC/TIndiv1   (total:  7.0        TMSC)  <<  added
        # A1:   SELL    3 TIndiv1   @   1.00000000 TMSC/TIndiv1   (total:  3.0        TMSC)
        # A1:   SELL   10 TIndiv1   @   1.00000000 TMSC/TIndiv1   (total: 10.0        TMSC)
        # A1:   SELL    1 TIndiv1   @   0.00000001 TMSC/TIndiv1   (total:  0.00000001 TMSC)
        #
        #
        self.check_balance(entity_a1.address, TIndiv1, '975', '25')

        # A111
        entity_a1.trade('1', TIndiv1, '0.00000001', TMSC, CANCEL_2)
        self.generate_block()
        #
        #
        # A1:   SELL    5 TIndiv1   @   1.20000000 TMSC/TIndiv1   (total:  6.0        TMSC)
        # A1:   SELL    6 TIndiv1   @   1.16666667 TMSC/TIndiv1   (total:  7.0        TMSC)
        # A1:   SELL    3 TIndiv1   @   1.00000000 TMSC/TIndiv1   (total:  3.0        TMSC)
        # A1:   SELL   10 TIndiv1   @   1.00000000 TMSC/TIndiv1   (total: 10.0        TMSC)
        # A1:   SELL    1 TIndiv1   @   0.00000001 TMSC/TIndiv1   (total:  0.00000001 TMSC)
        #
        # A1:   CANCEL  1 TIndiv1   @   0.00000001 TMSC/TIndiv1   (total:  0.00000001 TMSC)  <<  pending
        #
        # =>
        #
        # A1:   SELL    5 TIndiv1   @   1.20000000 TMSC/TIndiv1   (total:  6.0 TMSC)
        # A1:   SELL    6 TIndiv1   @   1.16666667 TMSC/TIndiv1   (total:  7.0 TMSC)
        # A1:   SELL    3 TIndiv1   @   1.00000000 TMSC/TIndiv1   (total:  3.0 TMSC)
        # A1:   SELL   10 TIndiv1   @   1.00000000 TMSC/TIndiv1   (total: 10.0 TMSC)
        #
        #
        self.check_balance(entity_a1.address, TIndiv1, '976', '24')


    # A114-120
    def test_match_indivisible_at_same_unit_price(self):
        """Tests matching of properties with indivisible units at the same unit price."""
        entity_a1 = self.entities[1]
        entity_a2 = self.entities[2]
        entity_a3 = self.entities[3]

        self.check_balance(entity_a1.address, TMSC, '57.00000000', '67.50000000')
        self.check_balance(entity_a2.address, TMSC, '82.50000000',  '0.00000000')
        self.check_balance(entity_a3.address, TMSC, '17.99999998',  '0.00000002')
        self.check_balance(entity_a1.address, TIndiv1, '976', '24')
        self.check_balance(entity_a2.address, TIndiv1,  '50',  '0')
        self.check_balance(entity_a3.address, TIndiv1,   '0',  '0')

        # A114
        entity_a1.trade('1.00000000', TMSC, '1', TIndiv1)
        self.generate_block()
        #
        #
        # A1:   SELL    5 TIndiv1   @   1.20000000 TMSC/TIndiv1   (total:  6.0 TMSC)
        # A1:   SELL    6 TIndiv1   @   1.16666667 TMSC/TIndiv1   (total:  7.0 TMSC)
        # A1:   SELL    3 TIndiv1   @   1.00000000 TMSC/TIndiv1   (total:  3.0 TMSC)
        # A1:   SELL   10 TIndiv1   @   1.00000000 TMSC/TIndiv1   (total: 10.0 TMSC)
        #
        # A1;   BUY     1 TIndiv1   @   1.00000000 TMSC/TIndiv1   (total:  1.0 TMSC)  <<  pending
        #
        # =>
        #
        # A1    BUYS    1 TIndiv1   @   1.00000000 TMSC/TIndiv1   (total:  1.0 TMSC)
        #
        # =>
        #
        # A1:   SELL    5 TIndiv1   @   1.20000000 TMSC/TIndiv1   (total:  6.0 TMSC)
        # A1:   SELL    6 TIndiv1   @   1.16666667 TMSC/TIndiv1   (total:  7.0 TMSC)
        # A1:   SELL    3 TIndiv1   @   1.00000000 TMSC/TIndiv1   (total:  3.0 TMSC)
        # A1:   SELL    9 TIndiv1   @   1.00000000 TMSC/TIndiv1   (total:  9.0 TMSC)  <<  updated
        #
        #

        # Movements:
        # A1->A1: 1.00000000 TMSC, A1->A1: 1 TIndiv1
        #
        self.check_balance(entity_a1.address, TMSC, '57.00000000', '67.50000000')
        self.check_balance(entity_a1.address, TIndiv1, '977', '23')

        # A115
        entity_a2.trade('1.00000000', TMSC, '1', TIndiv1)
        self.generate_block()
        #
        #
        # A1:   SELL    5 TIndiv1   @   1.20000000 TMSC/TIndiv1   (total:  6.0 TMSC)
        # A1:   SELL    6 TIndiv1   @   1.16666667 TMSC/TIndiv1   (total:  7.0 TMSC)
        # A1:   SELL    3 TIndiv1   @   1.00000000 TMSC/TIndiv1   (total:  3.0 TMSC)
        # A1:   SELL    9 TIndiv1   @   1.00000000 TMSC/TIndiv1   (total:  9.0 TMSC)
        #
        # A2;   BUY     1 TIndiv1   @   1.00000000 TMSC/TIndiv1   (total:  1.0 TMSC)  <<  pending
        #
        # =>
        #
        # A2    BUYS    1 TIndiv1   @   1.00000000 TMSC/TIndiv1   (total:  1.0 TMSC)
        #
        # =>
        #
        # A1:   SELL    5 TIndiv1   @   1.20000000 TMSC/TIndiv1   (total:  6.0 TMSC)
        # A1:   SELL    6 TIndiv1   @   1.16666667 TMSC/TIndiv1   (total:  7.0 TMSC)
        # A1:   SELL    3 TIndiv1   @   1.00000000 TMSC/TIndiv1   (total:  3.0 TMSC)
        # A1:   SELL    8 TIndiv1   @   1.00000000 TMSC/TIndiv1   (total:  8.0 TMSC)  <<  updated
        #
        #

        # Movements:
        # A2->A1: 1.00000000 TMSC, A1->A2: 1 TIndiv1
        #
        self.check_balance(entity_a1.address, TMSC, '58.00000000', '67.50000000')
        self.check_balance(entity_a2.address, TMSC, '81.50000000',  '0.00000000')
        self.check_balance(entity_a1.address, TIndiv1, '977', '22')
        self.check_balance(entity_a2.address, TIndiv1,  '51',  '0')

        # A117
        entity_a2.trade('6', TIndiv1, '6.00000000', TMSC)
        self.generate_block()
        #
        #
        # A1:   SELL    5 TIndiv1   @   1.20000000 TMSC/TIndiv1   (total:  6.0 TMSC)
        # A1:   SELL    6 TIndiv1   @   1.16666667 TMSC/TIndiv1   (total:  7.0 TMSC)
        # A2:   SELL    6 TIndiv1   @   1.00000000 TMSC/TIndiv1   (total:  6.0 TMSC)  <<  added
        # A1:   SELL    3 TIndiv1   @   1.00000000 TMSC/TIndiv1   (total:  3.0 TMSC)
        # A1:   SELL    8 TIndiv1   @   1.00000000 TMSC/TIndiv1   (total:  8.0 TMSC)
        #
        #
        self.check_balance(entity_a1.address, TMSC, '58.00000000', '67.50000000')
        self.check_balance(entity_a2.address, TMSC, '81.50000000',  '0.00000000')
        self.check_balance(entity_a1.address, TIndiv1, '977', '22')
        self.check_balance(entity_a2.address, TIndiv1,  '45',  '6')

        # A119
        entity_a3.trade('2.00000000', TMSC, '2', TIndiv1)
        self.generate_block()
        #
        #
        # A1:   SELL    5 TIndiv1   @   1.20000000 TMSC/TIndiv1   (total:  6.0 TMSC)
        # A1:   SELL    6 TIndiv1   @   1.16666667 TMSC/TIndiv1   (total:  7.0 TMSC)
        # A2:   SELL    6 TIndiv1   @   1.00000000 TMSC/TIndiv1   (total:  6.0 TMSC)
        # A1:   SELL    3 TIndiv1   @   1.00000000 TMSC/TIndiv1   (total:  3.0 TMSC)
        # A1:   SELL    8 TIndiv1   @   1.00000000 TMSC/TIndiv1   (total:  8.0 TMSC)
        #
        # A3;   BUY     2 TIndiv1   @   1.00000000 TMSC/TIndiv1   (total:  2.0 TMSC)  <<  pending
        #
        # =>
        #
        # A3    BUYS    2 TIndiv1   @   1.00000000 TMSC/TIndiv1   (total:  2.0 TMSC)
        #
        # =>
        #
        # A1:   SELL    5 TIndiv1   @   1.20000000 TMSC/TIndiv1   (total:  6.0 TMSC)
        # A1:   SELL    6 TIndiv1   @   1.16666667 TMSC/TIndiv1   (total:  7.0 TMSC)
        # A2:   SELL    6 TIndiv1   @   1.00000000 TMSC/TIndiv1   (total:  6.0 TMSC)
        # A1:   SELL    3 TIndiv1   @   1.00000000 TMSC/TIndiv1   (total:  3.0 TMSC)
        # A1:   SELL    6 TIndiv1   @   1.00000000 TMSC/TIndiv1   (total:  6.0 TMSC)  <<  updated
        #
        #

        # Movements:
        # A3->A1: 2.00000000 TMSC, A1->A3: 2 TIndiv1
        #
        self.check_balance(entity_a1.address, TMSC, '60.00000000', '67.50000000')
        self.check_balance(entity_a2.address, TMSC, '81.50000000',  '0.00000000')
        self.check_balance(entity_a3.address, TMSC, '15.99999998',  '0.00000002')
        self.check_balance(entity_a1.address, TIndiv1, '977', '20')
        self.check_balance(entity_a2.address, TIndiv1,  '45',  '6')
        self.check_balance(entity_a3.address, TIndiv1,   '2',  '0')

        # A120
        entity_a3.trade('12.00000000', TMSC, '12', TIndiv1)
        self.generate_block()
        #
        #
        # A1:   SELL    5 TIndiv1   @   1.20000000 TMSC/TIndiv1   (total:  6.0 TMSC)
        # A1:   SELL    6 TIndiv1   @   1.16666667 TMSC/TIndiv1   (total:  7.0 TMSC)
        # A2:   SELL    6 TIndiv1   @   1.00000000 TMSC/TIndiv1   (total:  6.0 TMSC)
        # A1:   SELL    3 TIndiv1   @   1.00000000 TMSC/TIndiv1   (total:  3.0 TMSC)
        # A1:   SELL    6 TIndiv1   @   1.00000000 TMSC/TIndiv1   (total:  6.0 TMSC)
        #
        # A3;   BUY    12 TIndiv1   @   1.00000000 TMSC/TIndiv1   (total: 12.0 TMSC)  <<  pending
        #
        # =>
        #
        # A3    BUYS   12 TIndiv1   @   1.00000000 TMSC/TIndiv1   (total: 12.0 TMSC)
        #
        # =>
        #
        # A1:   SELL    5 TIndiv1   @   1.20000000 TMSC/TIndiv1   (total:  6.0 TMSC)
        # A1:   SELL    6 TIndiv1   @   1.16666667 TMSC/TIndiv1   (total:  7.0 TMSC)
        # A2:   SELL    3 TIndiv1   @   1.00000000 TMSC/TIndiv1   (total:  3.0 TMSC)  <<  updated
        #
        #

        # Movements:
        # A3->A1: 6.00000000 TMSC, A1->A3: 6 TIndiv1
        # A3->A1: 3.00000000 TMSC, A1->A3: 3 TIndiv1
        # A3->A2: 3.00000000 TMSC, A2->A3: 3 TIndiv1
        #
        self.check_balance(entity_a1.address, TMSC, '69.00000000', '67.50000000')
        self.check_balance(entity_a2.address, TMSC, '84.50000000',  '0.00000000')
        self.check_balance(entity_a3.address, TMSC,  '3.99999998',  '0.00000002')
        self.check_balance(entity_a1.address, TIndiv1, '977', '11')
        self.check_balance(entity_a2.address, TIndiv1,  '45',  '3')
        self.check_balance(entity_a3.address, TIndiv1,  '14',  '0')


    # A123-125
    def test_match_indivisible_at_better_unit_price(self):
        """Tests matching of properties with indivisible units at a better unit price."""

        entity_a1 = self.entities[1]
        entity_a2 = self.entities[2]
        entity_a3 = self.entities[3]

        self.check_balance(entity_a1.address, TMSC, '69.00000000', '67.50000000')
        self.check_balance(entity_a2.address, TMSC, '84.50000000',  '0.00000000')
        self.check_balance(entity_a3.address, TMSC,  '3.99999998',  '0.00000002')
        self.check_balance(entity_a1.address, TIndiv1, '977', '11')
        self.check_balance(entity_a2.address, TIndiv1,  '45',  '3')
        self.check_balance(entity_a3.address, TIndiv1,  '14',  '0')

        # A123
        entity_a3.trade('2.00000000', TMSC, '1', TIndiv1)
        self.generate_block()
        #
        #
        # A1:   SELL    5 TIndiv1   @   1.20000000 TMSC/TIndiv1   (total:  6.0 TMSC)
        # A1:   SELL    6 TIndiv1   @   1.16666667 TMSC/TIndiv1   (total:  7.0 TMSC)
        # A2:   SELL    3 TIndiv1   @   1.00000000 TMSC/TIndiv1   (total:  3.0 TMSC)
        #
        # A3;   BUY     1 TIndiv1   @   2.00000000 TMSC/TIndiv1   (total:  2.0 TMSC)  <<  pending
        #
        # =>
        #
        # A3    BUYS    2 TIndiv1   @   1.00000000 TMSC/TIndiv1   (total:  2.0 TMSC)
        #
        # =>
        #
        # A1:   SELL    5 TIndiv1   @   1.20000000 TMSC/TIndiv1   (total:  6.0 TMSC)
        # A1:   SELL    6 TIndiv1   @   1.16666667 TMSC/TIndiv1   (total:  7.0 TMSC)
        # A2:   SELL    1 TIndiv1   @   1.00000000 TMSC/TIndiv1   (total:  1.0 TMSC)  <<  updated
        #
        #

        # Movements:
        # A3->A2: 2.00000000 TMSC, A2->A3: 2 TIndiv1
        #
        self.check_balance(entity_a1.address, TMSC, '69.00000000', '67.50000000')
        self.check_balance(entity_a2.address, TMSC, '86.50000000',  '0.00000000')
        self.check_balance(entity_a3.address, TMSC,  '1.99999998',  '0.00000002')
        self.check_balance(entity_a1.address, TIndiv1, '977', '11')
        self.check_balance(entity_a2.address, TIndiv1,  '45',  '1')
        self.check_balance(entity_a3.address, TIndiv1,  '16',  '0')

        # TODO: A124 fails, because A3 has not enough TMSC to open this offer

        # A124
        #entity_a3.trade('5.00000000', TMSC, '4', TIndiv1)
        #self.generate_block()

        # A125
        #entity_a3.trade('5.00000000', TMSC, '4', TIndiv1, CANCEL_2)
        #self.generate_block()


    # A128-134
    def test_match_indivisible_with_three(self):
        """Tests matching of three offers with properties with indivisible units."""
        # TODO: update balances after #124 is clear

        entity_a1 = self.entities[1]
        entity_a2 = self.entities[2]
        entity_a3 = self.entities[3]

        self.check_balance(entity_a1.address, TMSC,      '69.00000000', '67.50000000')
        self.check_balance(entity_a2.address, TMSC,      '86.50000000',  '0.00000000')
        self.check_balance(entity_a3.address, TMSC,       '1.99999998',  '0.00000002')
        self.check_balance(entity_a1.address, TIndiv3,    '0',           '0')
        self.check_balance(entity_a2.address, TIndiv3,  '200',           '0')
        self.check_balance(entity_a3.address, TIndiv3,  '200',           '0')

        # A128
        entity_a2.trade('15', TIndiv3, '22.50000000', TMSC)
        self.generate_block()
        #
        #
        # A2:   SELL   15 TIndiv1   @   1.50000000 TMSC/TIndiv3   (total: 25.5 TMSC)  << added
        #
        #
        self.check_balance(entity_a2.address, TMSC,      '86.50000000',  '0.00000000')
        self.check_balance(entity_a2.address, TIndiv3,  '185',          '15')

        # A129
        entity_a3.trade('10', TIndiv3, '10.00000000', TMSC)
        self.generate_block()
        #
        #
        # A2:   SELL   15 TIndiv1   @   1.50000000 TMSC/TIndiv3   (total: 25.5 TMSC)
        # A3:   SELL   10 TIndiv1   @   1.00000000 TMSC/TIndiv3   (total: 10.0 TMSC)  << added
        #
        #
        self.check_balance(entity_a3.address, TMSC,       '1.99999998',  '0.00000002')
        self.check_balance(entity_a3.address, TIndiv3,  '190',          '10')

        # A130
        entity_a2.trade('10', TIndiv3, '5.00000000', TMSC)
        self.generate_block()
        #
        #
        # A2:   SELL   15 TIndiv1   @   1.50000000 TMSC/TIndiv3   (total: 25.5 TMSC)
        # A3:   SELL   10 TIndiv1   @   1.00000000 TMSC/TIndiv3   (total: 10.0 TMSC)
        # A2:   SELL   10 TIndiv1   @   0.50000000 TMSC/TIndiv3   (total:  5.0 TMSC)  << added
        #
        #
        self.check_balance(entity_a2.address, TMSC,      '86.50000000',  '0.00000000')
        self.check_balance(entity_a2.address, TIndiv3,  '175',          '25')

        # A131
        entity_a1.trade('60.00000000', TMSC, '121', TIndiv3)
        self.generate_block()
        #
        #
        # A2:   SELL   15 TIndiv1   @   1.50000000 TMSC/TIndiv3   (total: 25.5 TMSC)
        # A3:   SELL   10 TIndiv1   @   1.00000000 TMSC/TIndiv3   (total: 10.0 TMSC)
        # A2:   SELL   10 TIndiv1   @   0.50000000 TMSC/TIndiv3   (total:  5.0 TMSC)
        #
        # A1:   BUY   121 TIndiv1   @   0,49586777 TMSC/TIndiv3   (total: 60.0 TMSC)  << added
        #
        #
        self.check_balance(entity_a1.address, TMSC,       '9.00000000', '127.50000000')
        self.check_balance(entity_a1.address, TIndiv3,    '0',            '0')

        # TODO: A32 fails, because A1 has not enough TMSC to open this offer

        # A132
        #entity_a1.trade('46.00000000', TMSC, '23', TIndiv3)
        #self.generate_block()

        # A133
        #entity_a2.trade('0.00000000', TMSC, '0', TIndiv3, CANCEL_3)
        #self.generate_block()

        # A134
        #entity_a2.trade('0.00000000', TMSC, '0', TIndiv3, CANCEL_4)
        #self.generate_block()




if __name__ == '__main__':
    MetaDexPlanTest().main()
