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
MIndiv2 = 4
MDiv1 = 5


class SendToOwnersTest(MasterTestFramework):

    def run_test(self):
        self.entities = [TestEntity(node) for node in self.nodes]

        self.prepare_funding()
        self.prepare_properties()

        self.test_send_tmsc_to_no_owner()
        self.test_send_tokens_to_no_owner()
        self.fund_entity_a1()
        self.test_send_tmsc_to_one_owner()
        self.test_send_tokens_to_one_owner()
        self.test_fee_check_before_send()
        self.test_send_too_few_tokens_to_owners()
        self.test_send_tokens_to_owners()

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
        """The miner (node 1) creates 3 new main properties with the maximum amounts possible.

        Final balances of miner (node 1) are tested to confirm correct property creation."""
        node = self.entities[0].node
        addr = self.entities[0].address

        if len(node.omni_listproperties()) > 2:
            AssertionError('There should not be more than two properties, MSC and TMSC, after a clean start')

        # tx: 50, ecosystem: 1, 9223372036854775807 indivisible tokens, "MIndiv1"
        node.omni_sendrawtx(addr, '000000320100010000000000004d496e646976310000007fffffffffffffff')
        # tx: 50, ecosystem: 1, 9223372036854775807 indivisible tokens, "MIndiv2"
        node.omni_sendrawtx(addr, '000000320100010000000000004d496e646976320000007fffffffffffffff')
        # tx: 50, ecosystem: 1, 92233720368.54770000 divisible tokens, "MDiv1"
        node.omni_sendrawtx(addr, '000000320100020000000000004d446976310000007fffffffffffffff')

        self.generate_block()
        self.check_balance(addr, MIndiv1, '9223372036854775807',  '0')
        self.check_balance(addr, MIndiv2, '9223372036854775807',  '0')
        self.check_balance(addr, MDiv1,   '92233720368.54775807', '0.00000000')


    def test_send_tmsc_to_no_owner(self):
        """Tests to send tokens to owners of TMSC while there is no other owner 
        and the sender is the only owner.

        1. The miner starts with 50000.0 TMSC, A1 with 0.0 MSC
        2. The miner sends 1.0 TMSC to all TMSC owners
        3. Because there is no other owner, no tokens should actually be moved
        """
        entity_miner = self.entities[0]
        entity_a1 = self.entities[1]

        # 1. The miner starts with 50000.0 TMSC, A1 with 0.0 MSC
        self.check_balance(entity_miner.address, TMSC, '50000.00000000', '0.00000000')
        self.check_balance(entity_a1.address,    TMSC,     '0.00000000', '0.00000000')

        # 2. The miner sends 1.0 TMSC to all TMSC owners
        entity_miner.send_to_owners(TMSC, '1.00000000')
        self.generate_block()

        # 3. Because there is no other owner, no tokens should actually be moved
        self.check_balance(entity_miner.address, TMSC, '50000.00000000', '0.00000000')
        self.check_balance(entity_a1.address,    TMSC,     '0.00000000', '0.00000000')


    def test_send_tokens_to_no_owner(self):
        """Tests to send tokens to owners of MIndiv1 while there is no other owner 
        and the sender is the only owner.

        1. The miner starts with 9223372036854775807 MIndiv1, A1 with 0 MIndiv1
        2. The miner sends 1 MIndiv1 to all MIndiv1 owners
        3. Because there is no other owner, no tokens should actually be moved
        """
        entity_miner = self.entities[0]
        entity_a1 = self.entities[1]

        # 1. The miner starts with 9223372036854775807 MIndiv1, A1 with 0 MIndiv1
        self.check_balance(entity_miner.address, MIndiv1, '9223372036854775807', '0')
        self.check_balance(entity_a1.address,    MIndiv1,                   '0', '0')

        # 2. The miner sends 1 MIndiv1 to all MIndiv1 owners
        entity_miner.send_to_owners(MIndiv1, '1')
        self.generate_block()

        # 3. Because there is no other owner, no tokens should actually be moved
        self.check_balance(entity_miner.address, MIndiv1, '9223372036854775807', '0')
        self.check_balance(entity_a1.address,    MIndiv1,                   '0', '0')


    def fund_entity_a1(self):
        """Tokens and bitcoins are sent from the miner (node 1) to A1 (node 2).
        
        A1 gets 1.00000000 MSC, 0.00000001 TMSC, 13 MIndiv1 and 50.0 BTC.
        
        Final balances are tested."""
        entity_miner = self.entities[0]
        entity_a1 = self.entities[1]

        # Check initial balances
        self.check_balance(entity_miner.address, MSC,           '50000.00000000', '0.00000000')
        self.check_balance(entity_miner.address, TMSC,          '50000.00000000', '0.00000000')
        self.check_balance(entity_miner.address, MIndiv1,  '9223372036854775807', '0')
        self.check_balance(entity_a1.address,    MSC,               '0.00000000', '0.00000000')
        self.check_balance(entity_a1.address,    TMSC,              '0.00000000', '0.00000000')
        self.check_balance(entity_a1.address,    MIndiv1,           '0',          '0')

        # Send tokens
        entity_miner.send(entity_a1.address,     MSC,               '1.00000000')
        entity_miner.send(entity_a1.address,     TMSC,              '0.00000001')
        entity_miner.send(entity_a1.address,     MIndiv1,          '13')

        # Send bitcoin
        entity_miner.send_bitcoins(entity_a1.address, 50.0)

        # Confirm balances
        self.generate_block()
        self.check_balance(entity_miner.address, MSC,           '49999.00000000', '0.00000000')
        self.check_balance(entity_miner.address, TMSC,          '49999.99999999', '0.00000000')
        self.check_balance(entity_miner.address, MIndiv1,  '9223372036854775794', '0')
        self.check_balance(entity_a1.address,    MSC,               '1.00000000', '0.00000000')
        self.check_balance(entity_a1.address,    TMSC,              '0.00000001', '0.00000000')
        self.check_balance(entity_a1.address,    MIndiv1,          '13',          '0')


    def test_send_tmsc_to_one_owner(self):
        """Tests to send TMSC to one other owner.

        1. The miner starts with 49999.99999999 TMSC, A1 with 0.00000001
        2. The miner sends 1.00000003 TMSC to all TMSC owners
        3. The miner should pay 0.00000001 TMSC for fees and end up with 49998.99999995 TMSC
        4. A1 should end up with 1.00000004 TMSC
        """
        entity_miner = self.entities[0]
        entity_a1 = self.entities[1]

        self.check_balance(entity_miner.address, TMSC, '49999.99999999', '0.00000000')
        self.check_balance(entity_a1.address,    TMSC,     '0.00000001', '0.00000000')

        entity_miner.send_to_owners(TMSC, '1.00000003')
        self.generate_block()

        self.check_balance(entity_miner.address, TMSC, '49998.99999995', '0.00000000')
        self.check_balance(entity_a1.address,    TMSC,     '1.00000004', '0.00000000')


    def test_send_tokens_to_one_owner(self):
        """Tests to send MIndiv1 to one other owner.
        """        
        entity_miner = self.entities[0]
        entity_a1 = self.entities[1]

        self.check_balance(entity_miner.address, MSC, '49999.00000000', '0.00000000')
        self.check_balance(entity_a1.address,    MSC,     '1.00000000', '0.00000000')
        self.check_balance(entity_miner.address, MIndiv1, '9223372036854775794', '0')
        self.check_balance(entity_a1.address,    MIndiv1,                  '13', '0')

        # Send 8 MIndiv to owners
        entity_miner.send_to_owners(MIndiv1, '8')
        self.generate_block()

        self.check_balance(entity_miner.address, MSC, '49998.99999999', '0.00000000')
        self.check_balance(entity_a1.address,    MSC,     '1.00000000', '0.00000000')
        self.check_balance(entity_miner.address, MIndiv1, '9223372036854775786', '0')
        self.check_balance(entity_a1.address,    MIndiv1,                  '21', '0')


    def test_fee_check_before_send(self):
        """Tests whether fees are subtracted before the actual transfer of tokens to owners.
        """
        entity_miner = self.entities[0]
        entity_a1 = self.entities[1]
        entity_a2 = self.entities[2]
        entity_a3 = self.entities[3]

        self.check_balance(entity_miner.address, TMSC, '49998.99999995', '0.00000000')
        self.check_balance(entity_a1.address,    TMSC,     '1.00000004', '0.00000000')
        self.check_balance(entity_a2.address,    TMSC,     '0.00000000', '0.00000000')
        self.check_balance(entity_a3.address,    TMSC,     '0.00000000', '0.00000000')

        entity_miner.send_to_owners(TMSC, '49998.99999993')
        self.generate_block()
        self.check_balance(entity_miner.address, TMSC,     '0.00000001', '0.00000000')
        self.check_balance(entity_a1.address,    TMSC, '49999.99999997', '0.00000000')
        self.check_balance(entity_a2.address,    TMSC,     '0.00000000', '0.00000000')
        self.check_balance(entity_a3.address,    TMSC,     '0.00000000', '0.00000000')

        entity_a1.send(entity_a2.address,        TMSC,     '0.00000001')
        entity_a1.send(entity_a3.address,        TMSC,     '0.00000001')

        self.generate_block()
        self.check_balance(entity_miner.address, TMSC,     '0.00000001', '0.00000000')
        self.check_balance(entity_a1.address,    TMSC, '49999.99999995', '0.00000000')
        self.check_balance(entity_a2.address,    TMSC,     '0.00000001', '0.00000000')
        self.check_balance(entity_a3.address,    TMSC,     '0.00000001', '0.00000000')

        # Send an amount where 0.00000001 TMSC of fees were missing
        entity_a1.send_to_owners(TMSC, '49999.99999993')
        self.generate_block()

        self.check_balance(entity_miner.address, TMSC,     '0.00000001', '0.00000000')
        self.check_balance(entity_a1.address,    TMSC, '49999.99999995', '0.00000000')
        self.check_balance(entity_a2.address,    TMSC,     '0.00000001', '0.00000000')
        self.check_balance(entity_a3.address,    TMSC,     '0.00000001', '0.00000000')


    def test_send_too_few_tokens_to_owners(self):
        """Tests whether no fee is paid for owners who receive nothing.
        
        1. The miner starts with 9223372036854775807 MIndiv2 and 49998.99999999 MSC
        2. A1 has 25 MIndiv2, A2 has 27 MIndiv2 and A3 has 23 MIndiv2
        3. 7 random recipients receive 1 MIndiv2 each from the miner
        4. The miner sends 2 MIndiv2 to all owners of MIndiv2
        5. A1 and A2 receive 1 MIndiv2 each, the other 8 owners receive nothing
        6. The miner should have paid 0.00000002 MSC fee and end up with a final 
           balance of 9223372036854775725 MIndiv2 and 49998.99999997 MSC
        
        There is no need to keep track of the 7 random recipients."""
        entity_miner = self.entities[0]
        entity_a1 = self.entities[1]
        entity_a2 = self.entities[2]
        entity_a3 = self.entities[3]

        self.check_balance(entity_miner.address, MIndiv2, '9223372036854775807', '0')
        self.check_balance(entity_a1.address,    MIndiv2,                   '0', '0')
        self.check_balance(entity_a2.address,    MIndiv2,                   '0', '0')
        self.check_balance(entity_a3.address,    MIndiv2,                   '0', '0')

        entity_miner.send(entity_a1.address, MIndiv2, '25')
        entity_miner.send(entity_a2.address, MIndiv2, '27')
        entity_miner.send(entity_a3.address, MIndiv2, '23')
        entity_miner.send(entity_miner.node.getnewaddress(), MIndiv2, '1')
        entity_miner.send(entity_miner.node.getnewaddress(), MIndiv2, '1')
        entity_miner.send(entity_miner.node.getnewaddress(), MIndiv2, '1')
        entity_miner.send(entity_miner.node.getnewaddress(), MIndiv2, '1')
        entity_miner.send(entity_miner.node.getnewaddress(), MIndiv2, '1')
        entity_miner.send(entity_miner.node.getnewaddress(), MIndiv2, '1')
        entity_miner.send(entity_miner.node.getnewaddress(), MIndiv2, '1')
        self.generate_block()

        self.check_balance(entity_miner.address, MSC, '49998.99999999', '0.00000000')
        self.check_balance(entity_miner.address, MIndiv2, '9223372036854775725', '0')
        self.check_balance(entity_a1.address,    MIndiv2,                  '25', '0')
        self.check_balance(entity_a2.address,    MIndiv2,                  '27', '0')
        self.check_balance(entity_a3.address,    MIndiv2,                  '23', '0')
        # + 7 other holders

        entity_miner.send_to_owners(MIndiv2, '2')
        self.generate_block()

        self.check_balance(entity_miner.address, MSC, '49998.99999997', '0.00000000')
        self.check_balance(entity_miner.address, MIndiv2, '9223372036854775723', '0')
        self.check_balance(entity_a1.address,    MIndiv2,                  '26', '0')
        self.check_balance(entity_a2.address,    MIndiv2,                  '28', '0')
        self.check_balance(entity_a3.address,    MIndiv2,                  '23', '0')


    def test_send_tokens_to_owners(self):
        """Tests multiple send-to-owner transactions to several recipients, rounding, 
        over-tax or overpayment of fees and priorization of owners by stack.
        """
        entity_miner = self.entities[0]
        entity_a1 = self.entities[1]
        entity_a2 = self.entities[2]
        entity_a3 = self.entities[3]

        entity_miner.send(entity_a2.address, MIndiv1, '20')
        self.generate_block()

        self.check_balance(entity_miner.address, MSC, '49998.99999997', '0.00000000')
        self.check_balance(entity_miner.address, MIndiv1, '9223372036854775766', '0')
        self.check_balance(entity_a1.address,    MIndiv1,                  '21', '0')
        self.check_balance(entity_a2.address,    MIndiv1,                  '20', '0')

        entity_miner.send_to_owners(MIndiv1, '1')
        self.generate_block()

        self.check_balance(entity_miner.address, MSC, '49998.99999996', '0.00000000')
        self.check_balance(entity_miner.address, MIndiv1, '9223372036854775765', '0')
        self.check_balance(entity_a1.address,    MIndiv1,                  '22', '0')
        self.check_balance(entity_a2.address,    MIndiv1,                  '20', '0')

        entity_miner.send(entity_a2.address, MIndiv1, '3')
        self.generate_block()

        self.check_balance(entity_miner.address, MSC, '49998.99999996', '0.00000000')
        self.check_balance(entity_miner.address, MIndiv1, '9223372036854775762', '0')
        self.check_balance(entity_a1.address,    MIndiv1,                  '22', '0')
        self.check_balance(entity_a2.address,    MIndiv1,                  '23', '0')

        entity_miner.send_to_owners(MIndiv1, '7')
        self.generate_block()

        self.check_balance(entity_miner.address, MSC, '49998.99999994', '0.00000000')
        self.check_balance(entity_miner.address, MIndiv1, '9223372036854775755', '0')
        self.check_balance(entity_a1.address,    MIndiv1,                  '25', '0')
        self.check_balance(entity_a2.address,    MIndiv1,                  '27', '0')

        self.check_balance(entity_miner.address, MDiv1, '92233720368.54775807', '0.00000000')
        self.check_balance(entity_a1.address,    MDiv1,           '0.00000000', '0.00000000')
        self.check_balance(entity_a2.address,    MDiv1,           '0.00000000', '0.00000000')
        self.check_balance(entity_a3.address,    MDiv1,           '0.00000000', '0.00000000')

        entity_miner.send(entity_a1.address,     MDiv1,         '300.0')
        entity_miner.send(entity_a2.address,     MDiv1,         '700.0')
        entity_miner.send(entity_a3.address,     MDiv1,        '1100.0')
        self.generate_block()

        self.check_balance(entity_miner.address, MDiv1, '92233718268.54775807', '0.00000000')
        self.check_balance(entity_a1.address,    MDiv1,         '300.00000000', '0.00000000')
        self.check_balance(entity_a2.address,    MDiv1,         '700.00000000', '0.00000000')
        self.check_balance(entity_a3.address,    MDiv1,        '1100.00000000', '0.00000000')

        entity_miner.send_to_owners(MDiv1, '1.00000000')
        self.generate_block()

        self.check_balance(entity_miner.address, MSC,         '49998.99999991', '0.00000000')
        self.check_balance(entity_miner.address, MDiv1, '92233718267.54775807', '0.00000000')
        self.check_balance(entity_a1.address,    MDiv1,         '300.14285713', '0.00000000')
        self.check_balance(entity_a2.address,    MDiv1,         '700.33333334', '0.00000000')
        self.check_balance(entity_a3.address,    MDiv1,        '1100.52380953', '0.00000000')


if __name__ == '__main__':
    SendToOwnersTest().main()
