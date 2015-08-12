#!/usr/bin/env python2
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

# Add python-bitcoinrpc to module search path:
import os
import sys
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "python-bitcoinrpc"))

from bitcoinrpc.authproxy import JSONRPCException
from decimal import Decimal
from framework_info import TestInfo


class TestEntity(object):

    def __init__(self, node, address=None):
        if address is None:
            address = node.getnewaddress()
        self.node = node
        self.address = address

    def generate_block(self, count=1):
        TestInfo.generate_block(self, count)
        try:
            self.node.setgenerate(True, count)
            TestInfo.OK()
        except JSONRPCException as e:
            TestInfo.Fail(e.error['message'])

    def get_balance(self, property_id):
        TestInfo.get_balance(self, property_id)
        balance = {}
        try:
            balance = self.node.omni_getbalance(self.address, property_id)
            TestInfo.OK()
        except JSONRPCException as e:
            TestInfo.Fail(e.error['message'])
        return balance

    def purchase_mastercoins(self, amount, fee=0.0001):
        TestInfo.purchase_mastercoins(self, amount, fee)
        txid, raw = '0000000000000000000000000000000000000000000000000000000000000000', '00'
        try:
            txid, raw = self.send_bitcoins('moneyqMan7uh8FqdCA2BV5yZ8qVrc9ikLP', amount, fee, [self.address])
            TestInfo.OK()
        except RuntimeError as e:
            TestInfo.Fail(e)
        return txid, raw

    def send(self, destination, property_id, amount, redeemer=''):
        TestInfo.send(self, destination, property_id, amount, redeemer)
        txid = '0000000000000000000000000000000000000000000000000000000000000000'
        try:
            txid = self.node.omni_send(self.address, destination, property_id, str(amount), redeemer)
            TestInfo.OK()
        except JSONRPCException as e:
            TestInfo.Fail(e.error['message'])
        return txid

    def send_to_owners(self, property_id, amount, redeemer=''):
        TestInfo.send_to_owners(self, property_id, amount, redeemer)
        txid = '0000000000000000000000000000000000000000000000000000000000000000'
        try:
            txid = self.node.omni_sendsto(self.address, property_id, str(amount), redeemer)
            TestInfo.OK()
        except JSONRPCException as e:
            TestInfo.Fail(e.error['message'])
        return txid

    def send_bitcoins(self, destination=None, amount=0.0, fee=0.0001, addr_filter=[], min_conf=0, max_conf=999999):
        TestInfo.send_bitcoins(self, destination, amount, fee, addr_filter, min_conf, max_conf)
        utxo = self.node.listunspent(min_conf, max_conf, addr_filter)
        inputs = []
        outputs = {}
        total_in = Decimal('0.00000000')
        while len(utxo) > 0:
            t = utxo.pop()
            total_in += t['amount']
            inputs.append({'txid': t['txid'], 'vout': t['vout'], 'address': t['address']})
        total_out = Decimal(amount + fee)
        if total_in < total_out:
            raise RuntimeError('Insufficient funds: need %d, have %d' % (total_out, total_in))
        change = Decimal(total_in - total_out)
        if destination is not None and amount > 0.0:
            outputs[destination] = Decimal(amount).quantize(Decimal('0.00000001'))
        if change > 0.0:
            outputs[self.address] = Decimal(change).quantize(Decimal('0.00000001'))
        rawtx = self.node.createrawtransaction(inputs, outputs)
        signresult = self.node.signrawtransaction(rawtx)
        txid = self.node.sendrawtransaction(signresult['hex'], True)
        return txid, signresult['hex']

    def pay_for_offer(self, destination=None, amount=0.0, fee=0.0001, addr_filter=[], min_conf=0, max_conf=999999):
        TestInfo.send_bitcoins(self, 'mpexoDuSkGGqvqrkrjiFng38QPkJQVFyqv', fee, fee, addr_filter, min_conf, max_conf)
        TestInfo.send_bitcoins(self, destination, amount, fee, addr_filter, min_conf, max_conf)
        utxo = self.node.listunspent(min_conf, max_conf, addr_filter)
        inputs = []
        outputs = {}
        total_in = Decimal('0.00000000')
        while len(utxo) > 0:
            t = utxo.pop()
            total_in += t['amount']
            inputs.append({'txid': t['txid'], 'vout': t['vout'], 'address': t['address']})
        total_out = Decimal(amount + fee + fee)
        if total_in < total_out:
            raise RuntimeError('Insufficient funds: need %d, have %d' % (total_out, total_in))
        change = Decimal(total_in - total_out)
        if destination is not None and amount > 0.0:
            outputs['mpexoDuSkGGqvqrkrjiFng38QPkJQVFyqv'] = Decimal(fee).quantize(Decimal('0.00000001'))
            outputs[destination] = Decimal(amount).quantize(Decimal('0.00000001'))
        if change > 0.0:
            outputs[self.address] = Decimal(change).quantize(Decimal('0.00000001'))
        rawtx = self.node.createrawtransaction(inputs, outputs)
        signresult = self.node.signrawtransaction(rawtx)
        txid = self.node.sendrawtransaction(signresult['hex'], True)
        return txid, signresult['hex']

    def trade(self, amount_sale, property_sale, amount_desired, property_desired, action=1):
        TestInfo.trade(self, amount_sale, property_sale, amount_desired, property_desired, action)
        txid = '0000000000000000000000000000000000000000000000000000000000000000'
        try:
            txid = self.node.trade_MP(self.address, property_sale, amount_sale, property_desired, amount_desired, action)
            TestInfo.OK()
        except JSONRPCException as e:
            TestInfo.Fail(e.error['message'])
        return txid
