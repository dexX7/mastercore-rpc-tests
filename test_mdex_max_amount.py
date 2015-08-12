#!/usr/bin/env python2
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

from framework_extension import MasterTestFramework
from framework_entity import TestEntity
from framework_info import TestInfo

# Helper
MSC = 1
TMSC = 2
MDiv1 = 3

ADD_1 = 1

# TODO: remove debug output helper, once the issue is resolved!
def strip_json(msg):
    msg = str(msg)
    msg = msg.replace("u'", "'")
    msg = msg.replace("Decimal(", "")
    msg = msg.replace(")", "")
    return msg


class MetaDexMaxAmountTest(MasterTestFramework):

    def run_test(self):
        self.entities = [TestEntity(node) for node in self.nodes]

        self.prepare_funding()
        self.prepare_properties()
        self.initial_distribution()

        self.test_amount_rounding()

        self.success = TestInfo.Status()

    def prepare_funding(self):
        """The miner (node 1) furthermore purchases 500.0 MSC and 500.0 TMSC."""
        entity_miner = self.entities[0]

        entity_miner.send_bitcoins(entity_miner.address)
        entity_miner.purchase_mastercoins(5.0)

        self.generate_block()
        self.check_balance(entity_miner.address, MSC,  '500.00000000', '0.00000000')
        self.check_balance(entity_miner.address, TMSC, '500.00000000', '0.00000000')

    def prepare_properties(self):
        """The miner (node 1) creates a new property with the maximum amounts possible.

        The tokens are going to be distributed as needed.

        Final balances of miner (node 1) are tested to confirm correct property creation."""
        node = self.entities[0].node
        addr = self.entities[0].address

        if len(node.omni_listproperties()) > 2:
            AssertionError('There should not be more than two properties, MSC and TMSC, after a clean start')

        # tx: 50, ecosystem: 1, 92233720368.54770000 divisible tokens, "MDiv1"
        node.omni_sendrawtx(addr, '000000320100020000000000004d446976310000007fffffffffffffff')

        self.generate_block()
        self.check_balance(addr, MDiv1, '92233720368.54775807', '0.00000000')


    def initial_distribution(self):
        """Tokens and bitcoins are sent from the miner (node 1) to A1 (node 2),
        and A2 (node 3).

        Final balances are tested."""
        entity_miner = self.entities[0]
        entity_a1 = self.entities[1]
        entity_a2 = self.entities[2]

        entity_miner.send_bitcoins(entity_a1.address, 1.0)
        entity_miner.send_bitcoins(entity_a2.address, 1.0)

        entity_miner.send(entity_a1.address, MSC,   '0.00000020')
        entity_miner.send(entity_a2.address, MDiv1, '0.00000012')

        self.generate_block()
        self.check_balance(entity_a1.address, MSC,   '0.00000020', '0.00000000')
        self.check_balance(entity_a1.address, MDiv1, '0.00000000', '0.00000000')
        self.check_balance(entity_a2.address, MSC,   '0.00000000', '0.00000000')
        self.check_balance(entity_a2.address, MDiv1, '0.00000012', '0.00000000')

    def test_amount_rounding(self):
        """See:
        https://github.com/mastercoin-MSC/spec/issues/170#issuecomment-44072344"""
        entity_a1 = self.entities[1]
        entity_a2 = self.entities[2]

        txid1 = entity_a1.trade('0.00000020', MSC,   '0.00000010', MDiv1, ADD_1)
        self.generate_block()

        txid2 = entity_a2.trade('0.00000012', MDiv1, '0.00000017', MSC,   ADD_1)
        self.generate_block()

        trade1 = self.nodes[3].omni_gettrade(txid1)
        trade2 = self.nodes[3].omni_gettrade(txid2)

        # TODO: remove debug output, once the issue is resolved!
        TestInfo.log('Trade 1:')
        TestInfo.log(strip_json(trade1))
        TestInfo.log('Trade 2:')
        TestInfo.log(strip_json(trade2))

if __name__ == '__main__':
    MetaDexMaxAmountTest().main()
