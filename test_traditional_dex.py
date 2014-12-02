#!/usr/bin/python
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
MDiv1 = 4
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


class TraditionalDexTest(MasterTestFramework):

    def run_test(self):
        self.entities = [TestEntity(node) for node in self.nodes]

        self.prepare_funding()
        self.initial_distribution()

        self.test_create_and_cancel_msc_offer()
        self.test_msc_offer_update()
        self.test_ignore_second_create_of_msc_offer()
        self.test_msc_offer_accept_timeout()
        self.test_msc_offer_accept_and_pay()
        self.test_msc_offer_accept_and_pay_multiple()
        self.test_msc_offer_accept_and_pay_multiple_with_update()


    def prepare_funding(self):
        """The miner (node 1) purchases 50000.0 MSC and 50000.0 TMSC."""
        entity_miner = self.entities[0]

        entity_miner.send_bitcoins(entity_miner.address)
        entity_miner.purchase_mastercoins(500.0)

        self.generate_block()
        self.check_balance(entity_miner.address, MSC,  '50000.00000000', '0.00000000')
        self.check_balance(entity_miner.address, TMSC, '50000.00000000', '0.00000000')


    def initial_distribution(self):
        """Tokens and bitcoins are sent from the miner (node 1) to A1 (node 2) and A2 (node 3).

        A1 (node 2) gets 50.0 BTC, 50.0 MSC and 50.0 TMSC.
        A2 (node 3) gets 50.0 BTC, 50.0 MSC and 50.0 TMSC.

        Final balances are tested."""
        entity_miner = self.entities[0]
        entity_a1 = self.entities[1]
        entity_a2 = self.entities[2]

        entity_miner.send_bitcoins(entity_a1.address, 50.0)
        entity_miner.send_bitcoins(entity_a2.address, 50.0)
        entity_miner.send(entity_a1.address, MSC,   '50.00000000')
        entity_miner.send(entity_a2.address, MSC,   '50.00000000')
        entity_miner.send(entity_a1.address, TMSC,  '50.00000000')
        entity_miner.send(entity_a2.address, TMSC,  '50.00000000')

        self.generate_block()
        self.check_balance(entity_a1.address, MSC,  '50.00000000', '0.00000000')
        self.check_balance(entity_a2.address, MSC,  '50.00000000', '0.00000000')
        self.check_balance(entity_a1.address, TMSC, '50.00000000', '0.00000000')
        self.check_balance(entity_a2.address, TMSC, '50.00000000', '0.00000000')


    def test_create_and_cancel_msc_offer(self):
        """
        1. A1 starts with 50.0 MSC, 50.0 TMSC
        2. A1 offers 10.0 MSC for 2.0 BTC (traditional)
        5. A1 cancels 10.0 MSC for 2.0 BTC (traditional)

        After this test A1 should have the same balance as at the beginning."""
        entity_a1 = self.entities[1]

        # 1. A1 starts with 50.0 MSC, 50.0 TMSC
        self.check_balance(entity_a1.address, MSC,  '50.00000000',  '0.00000000')  # SP 1
        self.check_balance(entity_a1.address, TMSC, '50.00000000',  '0.00000000')  # SP 2

        # 2. A1 offers 10.0 MSC for 2.0 BTC (traditional)
        TestInfo.log(entity_a1.address + ' offers 10.00000000 MSC for 2.0 BTC')
        entity_a1.node.sendrawtx_MP(entity_a1.address,
                                    '0001001400000001000000003b9aca00000000000bebc2000a000000000000271001')
        self.generate_block()
        self.check_balance(entity_a1.address, MSC,  '40.00000000', '10.00000000')  # SP 1
        self.check_balance(entity_a1.address, TMSC, '50.00000000',  '0.00000000')  # SP 2

        # 5. A1 cancels 10.0 MSC for 2.0 BTC (traditional)
        TestInfo.log(entity_a1.address + ' cancels 10.00000000 MSC for 2.0 BTC')
        entity_a1.node.sendrawtx_MP(entity_a1.address,
                                    '0001001400000001000000003b9aca00000000000000000000000000000000000003')

        self.generate_block()
        self.check_balance(entity_a1.address, MSC,  '50.00000000',  '0.00000000')  # SP 1
        self.check_balance(entity_a1.address, TMSC, '50.00000000',  '0.00000000')  # SP 2


    def test_msc_offer_update(self):
        """
        1. A1 starts with 50.0 MSC, 50.0 TMSC
        2. A1 offers 10.0 MSC for 2.0 BTC (traditional)
        2. A1 updates to 5.0 MSC for 1.0 BTC (traditional)
        5. A1 cancels 5.0 MSC for 1.0 BTC (traditional)
        6. A1 updates to 250.0 MSC for 2.0 BTC (traditional)
        7. A1 cancels MSC offer (traditional)

        After this test A1 should have the same balance as at the beginning."""
        entity_a1 = self.entities[1]

        # 1. A1 starts with 50.0 MSC, 50.0 TMSC
        self.check_balance(entity_a1.address, MSC,  '50.00000000',  '0.00000000')  # SP 1
        self.check_balance(entity_a1.address, TMSC, '50.00000000',  '0.00000000')  # SP 2

        # 2. A1 offers 10.0 MSC for 2.0 BTC (traditional)
        TestInfo.log(entity_a1.address + ' offers (action: 1) 10.00000000 MSC for 2.0 BTC')
        entity_a1.node.sendrawtx_MP(entity_a1.address,
                                    '0001001400000001000000003b9aca00000000000bebc2000a000000000000271001')

        self.generate_block()
        self.check_balance(entity_a1.address, MSC,  '40.00000000', '10.00000000')  # SP 1
        self.check_balance(entity_a1.address, TMSC, '50.00000000',  '0.00000000')  # SP 2


        # 3. A1 updates to 5.0 MSC for 1.0 BTC (traditional)
        TestInfo.log(entity_a1.address + ' updates (action: 2) to 5.00000000 MSC for 1.0 BTC')
        entity_a1.node.sendrawtx_MP(entity_a1.address,
                                    '0001001400000001000000001dcd65000000000005f5e1000a000000000000271002')
        self.generate_block()
        self.check_balance(entity_a1.address, MSC,  '45.00000000',  '5.00000000')  # SP 1
        self.check_balance(entity_a1.address, TMSC, '50.00000000',  '0.00000000')  # SP 2

        # 4. A1 updates to 5.0 MSC for 2.0 BTC (traditional)
        TestInfo.log(entity_a1.address + ' updates (action: 2) to 5.00000000 MSC for 2.0 BTC')
        entity_a1.node.sendrawtx_MP(entity_a1.address,
                                    '0001001400000001000000001dcd6500000000000bebc2000a000000000000271002')
        self.generate_block()
        self.check_balance(entity_a1.address, MSC,  '45.00000000',  '5.00000000')  # SP 1
        self.check_balance(entity_a1.address, TMSC, '50.00000000',  '0.00000000')  # SP 2


        # 5. A1 updates to 25.0 MSC for 2.0 BTC (traditional)
        TestInfo.log(entity_a1.address + ' updates (action: 2) to 25.00000000 MSC for 2.0 BTC')
        entity_a1.node.sendrawtx_MP(entity_a1.address,
                                    '0001001400000001000000009502f900000000000bebc2000a000000000000271002')
        self.generate_block()
        self.check_balance(entity_a1.address, MSC,  '25.00000000', '25.00000000')  # SP 1
        self.check_balance(entity_a1.address, TMSC, '50.00000000',  '0.00000000')  # SP 2


        # 6. A1 updates to 250.0 MSC for 2.0 BTC (traditional)
        TestInfo.log(entity_a1.address + ' updates (action: 2) to 250.00000000 MSC for 2.0 BTC')
        entity_a1.node.sendrawtx_MP(entity_a1.address,
                                    '000100140000000100000005d21dba00000000000bebc2000a000000000000271002')
        self.generate_block()
        self.check_balance(entity_a1.address, MSC,   '0.00000000', '50.00000000')  # SP 1
        self.check_balance(entity_a1.address, TMSC, '50.00000000',  '0.00000000')  # SP 2


        # 7. A1 cancels MSC offer (traditional)
        TestInfo.log(entity_a1.address + ' cancels (action: 3) an MSC offer')
        entity_a1.node.sendrawtx_MP(entity_a1.address,
                                    '0001001400000001000000003b9aca00000000000bebc2000a000000000000271003')

        self.generate_block()
        self.check_balance(entity_a1.address, MSC,  '50.00000000',  '0.00000000')  # SP 1
        self.check_balance(entity_a1.address, TMSC, '50.00000000',  '0.00000000')  # SP 2


    def test_ignore_second_create_of_msc_offer(self):
        """
        1. A1 starts with 50.0 MSC, 50.0 TMSC
        2. A1 offers 10.0 MSC for 2.0 BTC (traditional)
        3. A1 offers 5.0 MSC for 1.0 BTC (traditional)
        4. A1 cancels MSC offer (traditional)

        After this test A1 should have the same balance as at the beginning."""
        entity_miner = self.entities[0]
        entity_a1 = self.entities[1]

        # 1. A1 starts with 50.0 MSC, 50.0 TMSC
        self.check_balance(entity_a1.address, MSC,  '50.00000000',  '0.00000000')  # SP 1
        self.check_balance(entity_a1.address, TMSC, '50.00000000',  '0.00000000')  # SP 2

        # 2. A1 offers 10.0 MSC for 2.0 BTC (traditional)
        TestInfo.log(entity_a1.address + ' offers (action: 1) 10.00000000 MSC for 2.0 BTC')
        entity_a1.node.sendrawtx_MP(entity_a1.address,
                                    '0001001400000001000000003b9aca00000000000bebc2000a000000000000271001')
        self.generate_block()
        self.check_balance(entity_a1.address, MSC,  '40.00000000', '10.00000000')  # SP 1
        self.check_balance(entity_a1.address, TMSC, '50.00000000',  '0.00000000')  # SP 2

        # 3. A1 offers 5.0 MSC for 1.0 BTC (traditional)
        TestInfo.log(entity_a1.address + ' offfers (action: 1) 5.00000000 MSC for 1.0 BTC')
        entity_a1.node.sendrawtx_MP(entity_a1.address,
                                    '0001001400000001000000001dcd65000000000005f5e1000a000000000000271001')
        self.generate_block()
        self.check_balance(entity_a1.address, MSC,  '40.00000000', '10.00000000')  # SP 1
        self.check_balance(entity_a1.address, TMSC, '50.00000000',  '0.00000000')  # SP 2

        # 4. A1 cancels MSC offer (traditional)
        TestInfo.log(entity_a1.address + ' cancels (action: 3) an MSC offer')
        entity_a1.node.sendrawtx_MP(entity_a1.address,
                                    '0001001400000001000000003b9aca00000000000bebc2000a000000000000271003')
        self.generate_block()
        self.check_balance(entity_a1.address, MSC,  '50.00000000',  '0.00000000')  # SP 1
        self.check_balance(entity_a1.address, TMSC, '50.00000000',  '0.00000000')  # SP 2


    def test_msc_offer_accept_timeout(self):
        """
        1. A1 and A2 start with 50.0 MSC
        2. A1 offers 10.0 MSC for 2.0 BTC
        3. A2 accepts 10.0 MSC
        4. A1 cancels MSC offer
        5. A2 lets the order expire

        After this test A1 should have the same balance as at the beginning."""
        entity_a1 = self.entities[1]
        entity_a2 = self.entities[2]

        # 1. A1 and A2 start with 50.0 MSC
        self.check_balance(entity_a1.address, MSC, '50.00000000',  '0.00000000')  # SP 1
        self.check_balance(entity_a2.address, MSC, '50.00000000',  '0.00000000')  # SP 1

        # 2. A1 offers 10.0 MSC for 2.0 BTC
        TestInfo.log(entity_a1.address + ' offers (action: 1) 10.00000000 MSC for 2.0 BTC')
        entity_a1.node.sendrawtx_MP(entity_a1.address,
                                    '0001001400000001000000003b9aca00000000000bebc2000a000000000000271001')
        self.generate_block()
        self.check_balance(entity_a1.address, MSC, '40.00000000', '10.00000000')  # SP 1
        self.check_balance(entity_a2.address, MSC, '50.00000000',  '0.00000000')  # SP 1

        # 3. A2 accepts 10.0 MSC
        TestInfo.log(entity_a2.address + ' accepts 10.00000000 MSC')
        entity_a2.node.sendrawtx_MP(entity_a2.address, '0000001600000001000000003b9aca00', entity_a1.address)
        self.generate_block()
        self.check_balance(entity_a1.address, MSC, '40.00000000', '10.00000000')  # SP 1
        self.check_balance(entity_a2.address, MSC, '50.00000000',  '0.00000000')  # SP 1

        # 4. A1 cancels MSC offer
        TestInfo.log(entity_a1.address + ' cancels (action: 3) an MSC offer')
        entity_a1.node.sendrawtx_MP(entity_a1.address,
                                    '0001001400000001000000003b9aca00000000000bebc2000a000000000000271003')
        self.generate_block()
        self.check_balance(entity_a1.address, MSC, '40.00000000', '10.00000000')  # SP 1
        self.check_balance(entity_a2.address, MSC, '50.00000000',  '0.00000000')  # SP 1

        # 5. A2 lets the order expire
        self.generate_block(0, 10)
        self.check_balance(entity_a1.address, MSC, '50.00000000',  '0.00000000')  # SP 1
        self.check_balance(entity_a2.address, MSC, '50.00000000',  '0.00000000')  # SP 1


    def test_msc_offer_accept_and_pay(self):
        """
        1. A1 and A2 start with 50.0 MSC
        2. A1 offers 10.0 MSC for 2.0 BTC (traditional)
        3. A2 accepts 5.0 MSC
        4. A2 pays 0.5 BTC (for 2.5 MSC)
        5. A1 cancels MSC offer
        6. The offer expires
        7. Cleanup

        After this test A1 should have the same balance as at the beginning."""
        entity_miner = self.entities[0]
        entity_a1 = self.entities[1]
        entity_a2 = self.entities[2]

        # 1. A1 and A2 start with 50.0 MSC
        self.check_balance(entity_a1.address, MSC, '50.00000000',  '0.00000000')  # SP 1
        self.check_balance(entity_a2.address, MSC, '50.00000000',  '0.00000000')  # SP 1

        # 2. A1 offers 10.0 MSC for 2.0 BTC
        TestInfo.log(entity_a1.address + ' offers (action: 1) 10.00000000 MSC for 2.0 BTC')
        entity_a1.node.sendrawtx_MP(entity_a1.address,
                                    '0001001400000001000000003b9aca00000000000bebc2000a000000000000271001')
        self.generate_block()
        self.check_balance(entity_a1.address, MSC, '40.00000000', '10.00000000')  # SP 1
        self.check_balance(entity_a2.address, MSC, '50.00000000',  '0.00000000')  # SP 1

        # 3. A2 accepts 5.0 MSC
        TestInfo.log(entity_a2.address + ' accepts 5.00000000 MSC')
        entity_a2.node.sendrawtx_MP(entity_a2.address, '0000001600000001000000001dcd6500', entity_a1.address)
        self.generate_block()
        self.check_balance(entity_a1.address, MSC, '40.00000000', '10.00000000')  # SP 1
        self.check_balance(entity_a2.address, MSC, '50.00000000',  '0.00000000')  # SP 1

        # 4. A2 pays 0.5 BTC (for 2.5 MSC)
        TestInfo.log(entity_a2.address + ' pays 0.5 for 2.50000000 MSC')
        entity_a2.pay_for_offer(entity_a1.address, 0.5)
        self.generate_block()
        self.check_balance(entity_a1.address, MSC, '40.00000000',  '7.50000000')  # SP 1
        self.check_balance(entity_a2.address, MSC, '52.50000000',  '0.00000000')  # SP 1

        # 5. A1 cancels MSC offer
        TestInfo.log(entity_a1.address + ' cancels (action: 3) an MSC offer')
        entity_a1.node.sendrawtx_MP(entity_a1.address,
                                    '0001001400000001000000003b9aca00000000000bebc2000a000000000000271003')
        self.generate_block()
        self.check_balance(entity_a1.address, MSC, '45.00000000',  '2.50000000')  # SP 1
        self.check_balance(entity_a2.address, MSC, '52.50000000',  '0.00000000')  # SP 1

        # 6. The offer expires
        self.generate_block(0, 10)
        self.check_balance(entity_a1.address, MSC, '47.50000000',  '0.00000000')  # SP 1
        self.check_balance(entity_a2.address, MSC, '52.50000000',  '0.00000000')  # SP 1

        # 7. Cleanup
        entity_a2.send(entity_a1.address, MSC, '2.50000000')
        self.generate_block()


    def test_msc_offer_accept_and_pay_multiple(self):
        """
        1. A1 and A2 start with 50.0 MSC
        2. A1 offers 10.0 MSC for 2.0 BTC (traditional)
        3. A2 accepts 5.0 MSC
        ...

        After this test A1 should have the same balance as at the beginning."""
        entity_a1 = self.entities[1]
        entity_a2 = self.entities[2]

        # 1. A1 and A2 start with 50.0 MSC
        self.check_balance(entity_a1.address, MSC, '50.00000000',  '0.00000000')  # SP 1
        self.check_balance(entity_a2.address, MSC, '50.00000000',  '0.00000000')  # SP 1

        # 2. A1 offers 10.0 MSC for 2.0 BTC
        TestInfo.log(entity_a1.address + ' offers (action: 1) 10.00000000 MSC for 2.0 BTC')
        entity_a1.node.sendrawtx_MP(entity_a1.address,
                                    '0001001400000001000000003b9aca00000000000bebc2000a000000000000271001')
        self.generate_block()
        self.check_balance(entity_a1.address, MSC, '40.00000000', '10.00000000')  # SP 1
        self.check_balance(entity_a2.address, MSC, '50.00000000',  '0.00000000')  # SP 1

        # 3. A2 accepts 5.0 MSC
        TestInfo.log(entity_a2.address + ' accepts 5.00000000 MSC')
        entity_a2.node.sendrawtx_MP(entity_a2.address, '0000001600000001000000001dcd6500', entity_a1.address)
        self.generate_block()
        self.check_balance(entity_a1.address, MSC, '40.00000000', '10.00000000')  # SP 1
        self.check_balance(entity_a2.address, MSC, '50.00000000',  '0.00000000')  # SP 1

        # 4. A2 pays 0.5 BTC (for 2.5 MSC)
        TestInfo.log(entity_a2.address + ' pays 0.5 for 2.50000000 MSC')
        entity_a2.pay_for_offer(entity_a1.address, 0.5)
        self.generate_block()
        self.check_balance(entity_a1.address, MSC, '40.00000000',  '7.50000000')  # SP 1
        self.check_balance(entity_a2.address, MSC, '52.50000000',  '0.00000000')  # SP 1

        # 5. A1 cancels MSC offer
        TestInfo.log(entity_a1.address + ' cancels (action: 3) an MSC offer')
        entity_a1.node.sendrawtx_MP(entity_a1.address,
                                    '0001001400000001000000003b9aca00000000000bebc2000a000000000000271003')
        self.generate_block()
        self.check_balance(entity_a1.address, MSC, '45.00000000',  '2.50000000')  # SP 1
        self.check_balance(entity_a2.address, MSC, '52.50000000',  '0.00000000')  # SP 1

        # 6. A2 pays 0.25 BTC (for 1.25 MSC)
        TestInfo.log(entity_a2.address + ' pays 0.25 for 1.25000000 MSC')
        entity_a2.pay_for_offer(entity_a1.address, 0.25)
        self.generate_block()
        self.check_balance(entity_a1.address, MSC, '45.00000000',  '1.25000000')  # SP 1
        self.check_balance(entity_a2.address, MSC, '53.75000000',  '0.00000000')  # SP 1

        # 7. The offer times out
        self.generate_block(0, 10)
        self.check_balance(entity_a1.address, MSC, '46.25000000',  '0.00000000')  # SP 1
        self.check_balance(entity_a2.address, MSC, '53.75000000',  '0.00000000')  # SP 1

        # 8. Cleanup
        entity_a2.send(entity_a1.address, MSC, '3.75000000')
        self.generate_block()


    def test_msc_offer_accept_and_pay_multiple_with_update(self):
        """
        1. A1 and A2 start with 50.0 MSC
        2. A1 offers 10.0 MSC for 2.0 BTC (traditional)
        3. A2 accepts 5.0 MSC (1.0 BTC)
        4. A2 pays 0.25 BTC (for 1.25 MSC)
        5. A1 updates to 20.0 MSC for 10.0 BTC (traditional)
        6. A2 pays 0.5 BTC (for 2.5 MSC)
        7. A1 cancels MSC offer
        8. The offer times out
        9. Cleanup

        After this test A1 should have the same balance as at the beginning."""
        entity_a1 = self.entities[1]
        entity_a2 = self.entities[2]

        # 1. A1 and A2 start with 50.0 MSC
        self.check_balance(entity_a1.address, MSC, '50.00000000',  '0.00000000')  # SP 1
        self.check_balance(entity_a2.address, MSC, '50.00000000',  '0.00000000')  # SP 1

        # 2. A1 offers 10.0 MSC for 2.0 BTC
        TestInfo.log(entity_a1.address + ' offers (action: 1) 10.00000000 MSC for 2.0 BTC')
        entity_a1.node.sendrawtx_MP(entity_a1.address,
                                    '0001001400000001000000003b9aca00000000000bebc2000a000000000000271001')
        self.generate_block()
        self.check_balance(entity_a1.address, MSC, '40.00000000', '10.00000000')  # SP 1
        self.check_balance(entity_a2.address, MSC, '50.00000000',  '0.00000000')  # SP 1

        # 3. A2 accepts 5.0 MSC (1.0 BTC)
        TestInfo.log(entity_a2.address + ' accepts 5.00000000 MSC')
        entity_a2.node.sendrawtx_MP(entity_a2.address, '0000001600000001000000001dcd6500', entity_a1.address)
        self.generate_block()
        self.check_balance(entity_a1.address, MSC, '40.00000000', '10.00000000')  # SP 1
        self.check_balance(entity_a2.address, MSC, '50.00000000',  '0.00000000')  # SP 1

        # 4. A2 pays 0.25 BTC (for 1.25 MSC)
        TestInfo.log(entity_a2.address + ' pays 0.25 for 1.25000000 MSC')
        entity_a2.pay_for_offer(entity_a1.address, 0.25)
        self.generate_block()
        self.check_balance(entity_a1.address, MSC, '40.00000000',  '8.75000000')  # SP 1
        self.check_balance(entity_a2.address, MSC, '51.25000000',  '0.00000000')  # SP 1

        # 5. A1 updates to 20.0 MSC for 10.0 BTC (traditional)
        TestInfo.log(entity_a1.address + ' updates (action: 2) to 20.00000000 MSC for 10.0 BTC')
        entity_a1.node.sendrawtx_MP(entity_a1.address,
                                    '00010014000000010000000077359400000000003b9aca000a000000000000271002')
        self.generate_block()
        self.check_balance(entity_a1.address, MSC, '25.00000000', '23.75000000')  # SP 1
        self.check_balance(entity_a2.address, MSC, '51.25000000',  '0.00000000')  # SP 1

        # 6. A2 pays 0.5 BTC (for 2.5 MSC)
        TestInfo.log(entity_a2.address + ' pays 0.5 for 2.50000000 MSC')
        entity_a2.pay_for_offer(entity_a1.address, 0.5)
        self.generate_block()
        self.check_balance(entity_a1.address, MSC, '25.00000000', '21.25000000')  # SP 1
        self.check_balance(entity_a2.address, MSC, '53.75000000',  '0.00000000')  # SP 1

        # 7. A1 cancels MSC offer
        TestInfo.log(entity_a1.address + ' cancels (action: 3) an MSC offer')
        entity_a1.node.sendrawtx_MP(entity_a1.address,
                                    '0001001400000001000000003b9aca00000000000bebc2000a000000000000271003')
        self.generate_block()

        # 8. The offer times out
        self.generate_block(0, 10)
        self.check_balance(entity_a1.address, MSC, '46.25000000',  '0.00000000')  # SP 1
        self.check_balance(entity_a2.address, MSC, '53.75000000',  '0.00000000')  # SP 1

        # 9. Cleanup
        entity_a2.send(entity_a1.address, MSC, '3.75000000')
        self.generate_block()


if __name__ == '__main__':
    TraditionalDexTest().main()
