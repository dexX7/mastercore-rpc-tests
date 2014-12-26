#!/usr/bin/env python2
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

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
        self.node.setgenerate(True, count)

    def get_balance(self, property_id):
        TestInfo.get_balance(self, property_id)
        return self.node.getbalance_MP(self.address, property_id)

    def purchase_mastercoins(self, amount, fee=0.0001):
        TestInfo.purchase_mastercoins(self, amount, fee)
        return self.send_bitcoins('moneyqMan7uh8FqdCA2BV5yZ8qVrc9ikLP', amount, fee, [self.address])

    def send(self, destination, property_id, amount, redeemer=''):
        TestInfo.send(self, destination, property_id, amount, redeemer)
        txid = self.node.send_MP(self.address, destination, property_id, str(amount), redeemer)
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
        return self.node.trade_MP(self.address, amount_sale, property_sale, amount_desired, property_desired, action)
