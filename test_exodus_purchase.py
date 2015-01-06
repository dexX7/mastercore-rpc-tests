#!/usr/bin/env python2
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

from framework_extension import MasterTestFramework
from framework_entity import TestEntity
from framework_info import TestInfo


class ExodusPurchaseTest(MasterTestFramework):

    def run_test(self):
        self.entities = [TestEntity(node) for node in self.nodes]

        self.test_purchases()
        self.test_simple_sends()
        self.test_overspents()

        self.success = TestInfo.Status()


    def test_purchases(self):
        entity_miner = self.entities[0]
        entity_a1 = self.entities[1]
        entity_a2 = self.entities[2]

        # Ensure this is a clean start with zero balances
        self.check_balance(entity_a1.address, 1, '0.00000000', '0.00000000')
        self.check_balance(entity_a1.address, 2, '0.00000000', '0.00000000')
        self.check_balance(entity_a2.address, 1, '0.00000000', '0.00000000')
        self.check_balance(entity_a2.address, 2, '0.00000000', '0.00000000')

        # The first node mines and the other nodes require explicit funding
        entity_miner.send_bitcoins(entity_a1.address, 25.0)
        entity_miner.send_bitcoins(entity_a2.address, 25.0)

        # Generating a new block synchronizes all nodes
        self.generate_block()

        # Send some bitcoins to "moneyqMan7uh8FqdCA2BV5yZ8qVrc9ikLP"
        entity_a1.purchase_mastercoins(0.00000001)
        entity_a2.purchase_mastercoins(1.23456789)

        # After confirmation ...
        self.generate_block()

        # ... the updated balances are compared against expected values
        self.check_balance(entity_a1.address, 1, '0.00000100', '0.00000000')
        self.check_balance(entity_a1.address, 2, '0.00000100', '0.00000000')
        self.check_balance(entity_a2.address, 1, '123.45678900', '0.00000000')
        self.check_balance(entity_a2.address, 2, '123.45678900', '0.00000000')


    def test_simple_sends(self):
        entity_a1 = self.entities[1]
        entity_a2 = self.entities[2]

        entity_a2.send(entity_a1.address, 1, '100.45678899')

        self.generate_block()
        self.check_balance(entity_a1.address, 1, '100.45678999')
        self.check_balance(entity_a2.address, 1, '23.00000001')

        entity_a2.send(entity_a1.address, 1, '0.00000001')
        entity_a1.send(entity_a2.address, 1, '5.0')
        entity_a2.send(entity_a1.address, 1, '2.00000002')
        entity_a2.send(entity_a1.address, 1, '3.00000003')
        entity_a1.send(entity_a2.address, 1, '7.50000005')

        self.generate_block()
        self.check_balance(entity_a1.address, 1, '92.95679000', '0.00000000')
        self.check_balance(entity_a1.address, 2, '0.00000100', '0.00000000')
        self.check_balance(entity_a2.address, 1, '30.50000000', '0.00000000')
        self.check_balance(entity_a2.address, 2, '123.45678900', '0.00000000')


    def test_overspents(self):
        entity_a1 = self.entities[1]
        entity_a2 = self.entities[2]

        TestInfo.ExpectFail()

        entity_a1.send(entity_a2.address, 1, '9000.0')
        entity_a2.send(entity_a1.address, 1, '90000.0')
        entity_a1.send(entity_a2.address, 5, '5.0')
        entity_a1.send(entity_a2.address, -555, '55.0')
        entity_a1.send(entity_a2.address, 1, '0.0')

        TestInfo.StopExpectation()

        self.generate_block()
        self.check_balance(entity_a1.address, 1, '92.95679000', '0.00000000')
        self.check_balance(entity_a1.address, 2, '0.00000100', '0.00000000')
        self.check_balance(entity_a2.address, 1, '30.50000000', '0.00000000')
        self.check_balance(entity_a2.address, 2, '123.45678900', '0.00000000')


if __name__ == '__main__':
    ExodusPurchaseTest().main()
