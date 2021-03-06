#!/usr/bin/env python2
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
    """Test framework extension for Omni Core"""

    def generate_block(self, node=0, num=1):
        """Generates a new block and synchronizes all nodes"""
        TestInfo.log('Generating %d blocks..' % (num,))
        self.sync_all()
        self.nodes[node].setgenerate(True, num)
        self.sync_all()

    def check_balance(self, address, propertyid=1, expected_balance='0.00000000', expected_reserved=None):
        """Tests whether the address has sufficient balance of a property

        NOTE: A balance of zero is assumed, if the property doesn't exist."""
        TestInfo.check_balance(address, expected_balance, propertyid, expected_reserved)
        try:
            for node in self.nodes:
                self.check_balance_from(node, address, propertyid, expected_balance, expected_reserved)
            TestInfo.OK()
        except AssertionError as e:
            TestInfo.Fail('Assertion failed: ' + e.message)

    def check_balance_from(self, from_node, address, propertyid, expected_balance='0.00000000', expected_reserved=None):
        """Tests whether the address has sufficient balance of a property

        NOTE: A balance of zero is assumed, if the property doesn't exist"""
        try:
            balance = from_node.omni_getbalance(address, propertyid)
        except JSONRPCException as e:
            if e.error['code'] == -8:  # "Property identifier does not exist"
                balance = {'balance': '0.00000000', 'reserved': '0.00000000'}
            else: raise e
        if expected_balance != balance['balance']:
            raise AssertionError('balance returned by omni_getbalance for SP%d: %s, expected: %s' % (
                propertyid, balance['balance'], expected_balance), )
        if expected_reserved != balance['reserved'] and expected_reserved is not None:
            raise AssertionError('reserved balance returned by omni_getbalance for SP%d: %s, expected: %s' % (
                propertyid, balance['reserved'], expected_reserved), )

    def check_orderbook_count(self, expected_count, property_a, property_b = None):
        """Tests whether the number of offers of the provided currency-pair is in the orderbook"""
        if property_b is None:
            getorderbook_response = self.nodes[0].omni_getorderbook(property_a)
        else:
            getorderbook_response = self.nodes[0].omni_getorderbook(property_a, property_b)
        offers_count = len(getorderbook_response)
        if expected_count != offers_count:
            TestInfo.log(getorderbook_response)
            raise AssertionError('number of offers found by omni_getorderbook(SP%s, SP%s): %d, expected: %d' % (
            str(property_a), str(property_b), int(offers_count), int(expected_count),))
        TestInfo.check_orderbook_count_ok(expected_count, property_a, property_b)

    def check_active_dex_offers_count(self, expected_count):
        """Tests whether the number of offers on the traditional MSC/TMSC-BTC exchange can be found in the orderbook"""
        activeoffers_response = self.nodes[0].omni_getactivedexsells()
        offers_count = len(activeoffers_response)
        if expected_count != offers_count:
            TestInfo.log(activeoffers_response)
            raise AssertionError('number of active offers found by omni_getactivedexsells: %d, expected: %d' % (
            int(offers_count), int(expected_count),))
        TestInfo.check_active_dex_offers_count_ok(expected_count)
