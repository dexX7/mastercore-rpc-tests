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


class CancelMixedDexTradeTest(MasterTestFramework):

    def run_test(self):
        self.entities = [TestEntity(node) for node in self.nodes]

        self.prepare_funding()
        self.prepare_properties()
        self.initial_distribution()

        self.test_cancel_traditional_trade()


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
        """Tokens and bitcoins are sent from the miner (node 1) to A1 (node 2).

        Final balances are tested."""
        entity_miner = self.entities[0]
        entity_a1 = self.entities[1]

        entity_miner.send_bitcoins(entity_a1.address, 50.0)
        entity_miner.send(entity_a1.address, TMSC,  '63.50000000')

        self.generate_block()

        self.check_balance(entity_a1.address, TMSC,   '63.50000000', '0.00000000')
        self.check_balance(entity_a1.address, TDiv1,   '0.00000000', '0.00000000')
        self.check_balance(entity_a1.address, TIndiv1, '0', '0')


    def test_cancel_traditional_trade(self):
        """Tests if cancel operations of traditional DEx offers has an unexpected impact on reserved balances.

        After the test A1 should have 60.0 TMSC and 3.5 TMSC reserved.
        After the test A1 appears to have 63.5 TMSC and 0.0 TMSC reserved."""
        entity_a1 = self.entities[1]

        print('\nStart test:\n')

        # A1 starts with 50.0 BTC, 63.5 TMSC, 0.0 TDiv1, 0 TIndiv1
        self.check_balance(entity_a1.address, TMSC,   '63.50000000', '0.00000000')
        self.check_balance(entity_a1.address, TDiv1,   '0.00000000', '0.00000000')
        self.check_balance(entity_a1.address, TIndiv1, '0', '0')


        # 1. A1 offers 0.5 TMSC for 5000000000 TIndiv1
        entity_a1.trade('0.50000000', TMSC, '5000000000', TIndiv1)
        self.generate_block()

        print('\n1. A1 offers 0.5 TMSC for 5000000000 TIndiv1:')
        print(entity_a1.get_balance(TMSC))

        print('\nTraditional DEx orderbook:')
        print(entity_a1.node.getactivedexsells_MP())
        print('\nMeta DEx orderbook for TMSC:')
        print(entity_a1.node.getorderbook_MP(TMSC))
        print('\nMeta DEx orderbook for TDiv1:')
        print(entity_a1.node.getorderbook_MP(TDiv1))
        print('\nMeta DEx orderbook for TIndiv1:')
        print(entity_a1.node.getorderbook_MP(TIndiv1))


        # 2. A1 offers 3.0 TMSC for 30.00000000 TDiv1
        entity_a1.trade('3.00000000', TMSC, '30.00000000', TDiv1)
        self.generate_block()

        print('\n2. A1 offers 3.0 TMSC for 30.00000000 TDiv1:')
        print(entity_a1.get_balance(TMSC))

        print('\nTraditional DEx orderbook:')
        print(entity_a1.node.getactivedexsells_MP())
        print('\nMeta DEx orderbook for TMSC:')
        print(entity_a1.node.getorderbook_MP(TMSC))
        print('\nMeta DEx orderbook for TDiv1:')
        print(entity_a1.node.getorderbook_MP(TDiv1))
        print('\nMeta DEx orderbook for TIndiv1:')
        print(entity_a1.node.getorderbook_MP(TIndiv1))


        # 3. A1 offers 10.00000000 TMSC for 0.1 BTC
        entity_a1.node.sendrawtx_MP(entity_a1.address, '0001001400000002000000003b9aca0000000000009896800a000000000000271001')
        self.generate_block()

        print('\n3. A1 offers 10.00000000 TMSC for 0.1 BTC:')
        print(entity_a1.get_balance(TMSC))

        print('\nTraditional DEx orderbook:')
        print(entity_a1.node.getactivedexsells_MP())
        print('\nMeta DEx orderbook for TMSC:')
        print(entity_a1.node.getorderbook_MP(TMSC))
        print('\nMeta DEx orderbook for TDiv1:')
        print(entity_a1.node.getorderbook_MP(TDiv1))
        print('\nMeta DEx orderbook for TIndiv1:')
        print(entity_a1.node.getorderbook_MP(TIndiv1))


        # 4. A1 canceles 10.00000000 TMSC for 0.1 BTC
        entity_a1.node.sendrawtx_MP(entity_a1.address, '0001001400000002000000003b9aca0000000000000000000a000000000000000003')
        self.generate_block()

        print('\n4. A1 canceles 10.00000000 TMSC for 0.1 BTC:')
        print(entity_a1.get_balance(TMSC))

        print('\nTraditional DEx orderbook:')
        print(entity_a1.node.getactivedexsells_MP())
        print('\nMeta DEx orderbook for TMSC:')
        print(entity_a1.node.getorderbook_MP(TMSC))
        print('\nMeta DEx orderbook for TDiv1:')
        print(entity_a1.node.getorderbook_MP(TDiv1))
        print('\nMeta DEx orderbook for TIndiv1:')
        print(entity_a1.node.getorderbook_MP(TIndiv1))

        print('\nFinal balance test:')
        print(entity_a1.get_balance(TMSC))
        self.check_balance(entity_a1.address, TMSC,   '60.00000000', '3.50000000')
        self.check_balance(entity_a1.address, TDiv1,   '0.00000000', '0.00000000')
        self.check_balance(entity_a1.address, TIndiv1, '0', '0')


if __name__ == '__main__':
    CancelMixedDexTradeTest().main()
