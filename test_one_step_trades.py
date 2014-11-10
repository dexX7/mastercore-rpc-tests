#!/usr/bin/python
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

from framework_extension import MasterTestFramework
from framework_entity import TestEntity


class OneStepTradeTest(MasterTestFramework):

    def run_test(self):
        self.entities = [TestEntity(node) for node in self.nodes]

        self.prepare_funding()
        self.prepare_properties()
        self.test_indiv_tmsc_trade()
        self.test_indiv_indiv_trade()


    def prepare_funding(self):
        entity_miner = self.entities[0]
        entity_a1 = self.entities[1]
        entity_a2 = self.entities[2]

        entity_miner.send_bitcoins(entity_miner.address)
        entity_miner.send_bitcoins(entity_a1.address, 35.0)
        entity_miner.send_bitcoins(entity_a2.address, 15.0)

        self.generate_block()
        entity_a1.purchase_mastercoins(30.0)
        entity_a2.purchase_mastercoins(10.0)

        self.generate_block()
        self.check_balance(entity_a1.address, 1, '3000.00000000', '0.00000000')
        self.check_balance(entity_a1.address, 2, '3000.00000000', '0.00000000')
        self.check_balance(entity_a2.address, 1, '1000.00000000', '0.00000000')
        self.check_balance(entity_a2.address, 2, '1000.00000000', '0.00000000')


    def prepare_properties(self):
        node = self.entities[0].node
        addr = self.entities[0].address

        if len(node.listproperties_MP()) > 2:
            AssertionError('There should not be more than two properties, MSC and TMSC, after a clean start')

        # tx: 50, ecosystem: 2, 9223372036854775807 indivisible tokens, "TIndiv1"
        node.sendrawtx_MP(addr, '0000003202000100000000000054496e646976310000007fffffffffffffff')
        # tx: 50, ecosystem: 2, 9223372036854775807 indivisible tokens, "TIndiv2"
        node.sendrawtx_MP(addr, '0000003202000100000000000054496e646976320000007fffffffffffffff')
        # tx: 50, ecosystem: 2, 92233720368.54770000 divisible tokens, "TDiv1"
        node.sendrawtx_MP(addr, '0000003202000200000000000054446976310000007fffffffffffffff')
        # tx: 50, ecosystem: 2, 92233720368.54770000 divisible tokens, "TDiv2"
        node.sendrawtx_MP(addr, '0000003202000200000000000054446976320000007fffffffffffffff')

        self.generate_block()
        self.check_balance(addr, 2147483651, '9223372036854775807', '0')
        self.check_balance(addr, 2147483652, '9223372036854775807', '0')
        self.check_balance(addr, 2147483653, '92233720368.54775807', '0.00000000')
        self.check_balance(addr, 2147483654, '92233720368.54775807', '0.00000000')


    def test_indiv_tmsc_trade(self):
        entity_miner = self.entities[0]
        entity_a1 = self.entities[1]
        entity_a2 = self.entities[2]

        sp = {'TMSC': 2, 'TIndiv1': 2147483651, 'TIndiv2': 2147483652, 'TDiv1': 2147483653, 'TDiv2': 2147483654}

        entity_miner.send(entity_a1.address, sp['TIndiv1'], 5000)

        self.generate_block()
        self.check_balance(entity_a1.address, sp['TIndiv1'], '5000', '0')
        self.check_balance(entity_a1.address, sp['TMSC'], '3000.00000000', '0.00000000')
        self.check_balance(entity_a2.address, sp['TMSC'], '1000.00000000', '0.00000000')

        entity_a1.trade('1', sp['TIndiv1'], '0.00000001', sp['TMSC'])

        self.generate_block()
        self.check_balance(entity_a1.address, sp['TIndiv1'], '4999', '1')

        entity_a2.trade('0.00000001', sp['TMSC'], '1', sp['TIndiv1'])

        self.generate_block()
        self.check_balance(entity_a1.address, sp['TIndiv1'], '4999', '0')
        self.check_balance(entity_a2.address, sp['TIndiv1'], '1', '0')
        self.check_balance(entity_a1.address, sp['TMSC'], '3000.00000001', '0.00000000')
        self.check_balance(entity_a2.address, sp['TMSC'], '999.99999999', '0.00000000')

        entity_a2.trade('1', sp['TIndiv1'], '3000.00000001', sp['TMSC'])

        self.generate_block()
        self.check_balance(entity_a2.address, sp['TIndiv1'], '0', '1')

        entity_a1.trade('3000.00000001', sp['TMSC'], '1', sp['TIndiv1'])

        self.generate_block()
        self.check_balance(entity_a1.address, sp['TIndiv1'], '5000', '0')
        self.check_balance(entity_a2.address, sp['TIndiv1'], '0', '0')
        self.check_balance(entity_a1.address, sp['TMSC'], '0.00000000', '0.00000000')
        self.check_balance(entity_a2.address, sp['TMSC'], '4000.00000000', '0.00000000')

        entity_a1.trade('20', sp['TIndiv1'], '10.00000000', sp['TMSC'])
        self.generate_block()
        entity_a2.trade('10.00000000', sp['TMSC'], '10', sp['TIndiv1'])
        self.generate_block()
        entity_a2.trade('10.00000000', sp['TMSC'], '10', sp['TIndiv1'])
        self.generate_block()

        self.check_balance(entity_a1.address, sp['TIndiv1'], '4980', '0')
        self.check_balance(entity_a2.address, sp['TIndiv1'], '20', '0')
        self.check_balance(entity_a1.address, sp['TMSC'], '10.00000000', '0.00000000')
        self.check_balance(entity_a2.address, sp['TMSC'], '3980.00000000', '10.00000000')


    def test_indiv_indiv_trade(self):
        entity_miner = self.entities[0]
        entity_a1 = self.entities[1]
        entity_a2 = self.entities[2]

        sp = {'TMSC': 2, 'TIndiv1': 2147483651, 'TIndiv2': 2147483652, 'TDiv1': 2147483653, 'TDiv2': 2147483654}

        entity_miner.send(entity_a2.address, sp['TIndiv2'], '10')

        self.generate_block()
        self.check_balance(entity_a1.address, sp['TIndiv1'], '4980', '0')
        self.check_balance(entity_a1.address, sp['TIndiv2'], '0', '0')
        self.check_balance(entity_a2.address, sp['TIndiv1'], '20', '0')
        self.check_balance(entity_a2.address, sp['TIndiv2'], '10', '0')

        entity_a1.trade('10', sp['TIndiv1'], '10', sp['TIndiv2'])
        self.generate_block()

        # TODO: token for token trades do not work!
        # TODO: token for token trades do not work!
        # TODO: token for token trades do not work!

        entity_a2.trade('10', sp['TIndiv2'], '10', sp['TIndiv1'])
        self.generate_block()

        print(entity_a1.get_balance(sp['TIndiv1']))
        print(entity_a1.get_balance(sp['TIndiv2']))
        print(entity_a2.get_balance(sp['TIndiv1']))
        print(entity_a2.get_balance(sp['TIndiv2']))


if __name__ == '__main__':
    OneStepTradeTest().main()
