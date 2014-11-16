#!/usr/bin/python
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

# Add python-bitcoinrpc to module search path:
import os
import sys
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "python-bitcoinrpc"))

from bitcoinrpc.authproxy import JSONRPCException
from framework_base import BitcoinTestFramework
from framework_info import TestInfo


class MasterTestFramework(BitcoinTestFramework):
    """Test framework extension for Master Core"""

    def generate_block(self, node=0):
        """Generates a new block and synchronizes all nodes"""
        self.sync_all()
        self.nodes[node].setgenerate(True, 1)
        self.sync_all()

    def check_balance(self, address, propertyid=1, expected_balance='0.00000000', expected_reserved=None):
        """Tests whether the address has sufficient balance of a property

        NOTE: A balance of zero is assumed, if the property doesn't exist."""
        for node in self.nodes:
            self.check_balance_from(node, address, propertyid, expected_balance, expected_reserved)
        TestInfo.check_balance_ok(address, expected_balance, propertyid)

    def check_balance_from(self, from_node, address, propertyid, expected_balance='0.00000000', expected_reserved=None):
        """Tests whether the address has sufficient balance of a property

        NOTE: A balance of zero is assumed, if the property doesn't exist"""
        try:
            balance = from_node.getbalance_MP(address, propertyid)
        except JSONRPCException as e:
            if e.error['code'] == -8:  # "Property identifier does not exist"
                balance = {'balance': '0.00000000', 'reserved': '0.00000000'}
            else: raise e
        if expected_balance != balance['balance']:
            raise AssertionError('balance returned by getbalance_MP for SP%d: %s, expected: %s' % (
                propertyid, balance['balance'], expected_balance), )
        if expected_reserved != balance['reserved'] and expected_reserved is not None:
            raise AssertionError('reserved balance returned by getbalance_MP for SP%d: %s, expected: %s' % (
                propertyid, balance['reserved'], expected_reserved), )
