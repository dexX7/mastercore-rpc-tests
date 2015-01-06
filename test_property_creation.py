#!/usr/bin/env python2
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

from framework_extension import MasterTestFramework
from framework_entity import TestEntity
from framework_info import TestInfo


class PropertyCreationTest(MasterTestFramework):

    def run_test(self):
        self.entities = [TestEntity(node) for node in self.nodes]

        self.test_rawtx_creation()
        self.test_invalid_rawtx_creation()


    def test_rawtx_creation(self):
        node = self.entities[0].node
        addr = self.entities[0].address
        self.entities[0].send_bitcoins(addr)

        property_count_old = len(node.listproperties_MP())

        node.sendrawtx_MP(addr, '0000003202000100000000000054496e646976310000007fffffffffffffff')  # TIndiv1
        node.sendrawtx_MP(addr, '0000003202000100000000000054496e646976320000007fffffffffffffff')  # TIndiv2
        node.sendrawtx_MP(addr, '0000003202000200000000000054446976310000007fffffffffffffff')  # TDiv1
        node.sendrawtx_MP(addr, '0000003202000200000000000054446976320000007fffffffffffffff')  # TDiv2

        self.generate_block()
        property_count_new = len(node.listproperties_MP())

        if property_count_new != property_count_old + 4:
            raise AssertionError('Number of properties should have increased after creating a new properties')


    def test_invalid_rawtx_creation(self):
        node = self.entities[0].node
        addr = self.entities[0].address

        property_count_old = len(node.listproperties_MP())

        TestInfo.ExpectFail()

        # Number of divisible tokens is zero
        try: node.sendrawtx_MP(addr, '000000320100020000000000005a65726f4469760000000000000000000000')  # ZeroDiv
        except: pass

        # Ecosystem is 0
        try: node.sendrawtx_MP(addr, '0000003200000200000000000045636f737973300000000000000000000064')  # Ecosys0
        except: pass

        # Ecosystem is 3
        try: node.sendrawtx_MP(addr, '0000003200000200000000000045636f737973330000000000000000000064')  # Ecosys0
        except: pass

        TestInfo.StopExpectation()

        self.generate_block()
        property_count_new = len(node.listproperties_MP())

        if property_count_new != property_count_old:
            raise AssertionError(
                'Number of properties should not have increased after creating a property with zero amount')

        self.success = TestInfo.Status()


if __name__ == '__main__':
    PropertyCreationTest().main()
