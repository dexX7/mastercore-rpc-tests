#!/usr/bin/env python2
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

import random

from framework_extension import MasterTestFramework
from framework_entity import TestEntity

# Helper

MSC = 1
TMSC = 2

class SimpleSendTest(MasterTestFramework):

    def run_test(self):
        self.entities = [TestEntity(node) for node in self.nodes]

        self.prepare_funding()
        self.initial_distribution()

        self.test_simple_sends()


    def prepare_funding(self):
        """The miner (node 1) purchases 50000.0 MSC."""
        entity_miner = self.entities[0]

        entity_miner.send_bitcoins(entity_miner.address)
        entity_miner.purchase_mastercoins(500.0)

        self.generate_block()
        self.check_balance(entity_miner.address, MSC,  '50000.00000000', '0.00000000')
        self.check_balance(entity_miner.address, TMSC, '50000.00000000', '0.00000000')


    def initial_distribution(self):
        """Tokens and bitcoins are sent from the miner (node 1) to A1 (node 2).

        A1 (node 2) gets 50.0 BTC, 250.0 MSC and 250.0 TMSC.

        Final balances are tested."""
        entity_miner = self.entities[0]
        entity_a1 = self.entities[1]

        entity_miner.send_bitcoins(entity_a1.address, 50.0)
        entity_miner.send(entity_a1.address, MSC,  '250.00000000')
        entity_miner.send(entity_a1.address, TMSC, '250.00000000')

        self.generate_block()
        self.check_balance(entity_a1.address, MSC,  '250.00000000', '0.00000000')
        self.check_balance(entity_a1.address, TMSC, '250.00000000', '0.00000000')


    def send_many_random(self, entity_source, entity_destination, property_id, amount, rounds_min, max_rounds):
        """Sends a random number of Simple Send transactions, and creates a block afterwards."""
        rounds = random.randint(rounds_min, max_rounds)
        rounds_left = rounds
        while rounds_left > 0:
            entity_source.send(entity_destination.address, property_id, amount)
            rounds_left -= 1
        self.generate_block()
        return rounds


    def send_many(self, amount_per_step = '1.00000000', property_id = TMSC, total_rounds = 5, rounds_min = 1, rounds_max = 1):
        """Sends a random number of Simple Send transactions in multiple batches."""
        entity_a1 = self.entities[1]
        entity_a2 = self.entities[2]

        rounds_left = total_rounds

        while rounds_left > 0:            
            current_min = min(rounds_min, rounds_left)
            current_max = min(rounds_max, rounds_left)
            rounds_made = self.send_many_random(entity_a1, entity_a2, property_id, amount_per_step, current_min, current_max)
            rounds_left = rounds_left - rounds_made


    def test_simple_sends(self):
        """Tests the RPC call send_MP.

        1. A1 starts with 50.0 BTC, 250.0 MSC and 250.0 TMSC
        2. 2. A1 sends 245.0 MSC and TMSC to A2 in random batches"""
        entity_a1 = self.entities[1]
        entity_a2 = self.entities[2]

        # 1. 1. A1 starts with 50.0 BTC, 250.0 MSC and 250.0 TMSC
        self.check_balance(entity_a1.address, MSC,  '250.00000000', '0.00000000')
        self.check_balance(entity_a1.address, TMSC, '250.00000000', '0.00000000')
        self.check_balance(entity_a2.address, MSC,    '0.00000000', '0.00000000')
        self.check_balance(entity_a2.address, TMSC,   '0.00000000', '0.00000000')

        # 2. A1 sends 245.0 MSC and TMSC to A2 in random batches
        self.send_many('5.00000000', TMSC,  49, 0, 15)
        self.check_balance(entity_a1.address, TMSC,   '5.00000000', '0.00000000')
        self.check_balance(entity_a2.address, TMSC, '245.00000000', '0.00000000')

        self.send_many('5.00000000',  MSC,  49, 0, 25)
        self.check_balance(entity_a1.address, MSC,    '5.00000000', '0.00000000')
        self.check_balance(entity_a2.address, MSC,  '245.00000000', '0.00000000')


if __name__ == '__main__':
    SimpleSendTest().main()
