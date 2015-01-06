#!/usr/bin/env python2
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

from framework_extension import MasterTestFramework
from framework_entity import TestEntity
from framework_info import TestInfo


class P2SHTest(MasterTestFramework):

    def run_test(self):
        self.entities = [TestEntity(node) for node in self.nodes]
        entity_miner = self.entities[0]
        entity_a1 = self.entities[1]
        entity_a2 = self.entities[2]

        # Create a 2-of-3 script-hash address
        script_destination = entity_a1.node.addmultisigaddress(2, [entity_a1.address, entity_a1.node.getnewaddress(),
                                                                   entity_a1.node.getnewaddress()])
        entity_p2sh = TestEntity(entity_a1.node, script_destination)
        entity_miner.send_bitcoins(script_destination, 2.0)
        entity_miner.send_bitcoins(entity_a2.address, 2.0)
        self.generate_block()

        # Purchase some Mastercoins
        entity_p2sh.purchase_mastercoins(1.0)
        entity_a2.purchase_mastercoins(1.0)
        
        # Then check, if target was funded as expected
        self.generate_block()
        self.check_balance(entity_p2sh.address, 1, '100.00000000')
        self.check_balance(entity_p2sh.address, 2, '100.00000000')
        self.check_balance(entity_a2.address, 1, '100.00000000')
        self.check_balance(entity_a2.address, 2, '100.00000000')

        # Make sure a send from script-hash is possible as well
        entity_p2sh.send(entity_a2.address, 1, '100.0', entity_a1.address)
        self.generate_block()
        self.check_balance(entity_p2sh.address, 1, '0.00000000')
        self.check_balance(entity_a2.address, 1, '200.00000000')

        # Send the tokens back to test, if it's also a viable destination
        entity_a2.send(entity_p2sh.address, 1, '200.0')
        self.generate_block()
        self.check_balance(entity_p2sh.address, 1, '200.00000000')
        self.check_balance(entity_a2.address, 1, '0.00000000')

        self.success = TestInfo.Status()


if __name__ == '__main__':
    P2SHTest().main()
