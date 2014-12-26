#!/usr/bin/env python2
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

from decimal import Decimal


class TestInfo(object):
    """Used to print additional information, if "--verbose" is enabled"""

    ENABLED = 1

    @staticmethod
    def send(source, destination, property_id, amount, redeemer):
        if not TestInfo.ENABLED: return
        print('Sending %s SP%d from %s to %s' % (
            Decimal(amount).quantize(Decimal('0.00000001')), property_id, source.address, destination,))

    @staticmethod
    def trade(source, amount_sale, property_sale, amount_desired, property_desired, action):
        if not TestInfo.ENABLED: return
        print('Offering (action: %d) %s SP%d from %s for %s SP%d' % (
            action, Decimal(amount_sale).quantize(Decimal('0.00000001')), property_sale, source.address,
            Decimal(amount_desired).quantize(Decimal('0.00000001')), property_desired,))

    @staticmethod
    def generate_block(source, count):
        if not TestInfo.ENABLED: return
        print('Generating %d block' % (count,))

    @staticmethod
    def get_balance(source, property_id):
        if not TestInfo.ENABLED: return
        print('Getting balance from %s for SP%d' % (source.address, property_id,))

    @staticmethod
    def send_bitcoins(source, destination, amount, fee, addr_filter, min_conf, max_conf):
        if not TestInfo.ENABLED: return
        print('Sending %s BTC from %s to %s with a fee of %s BTC' % (
            Decimal(amount).quantize(Decimal('0.00000001')), source.address, destination,
            Decimal(fee).quantize(Decimal('0.00000001')),))

    @staticmethod
    def purchase_mastercoins(source, amount, fee):
        if not TestInfo.ENABLED: return
        print('Purchasing Mastercoins from %s for %s BTC with a fee of %s BTC' % (
            source.address, Decimal(amount).quantize(Decimal('0.00000001')),
            Decimal(fee).quantize(Decimal('0.00000001')),))

    @staticmethod
    def check_balance_ok(source, expected_balance, propertyid, expected_reserved):
        if not TestInfo.ENABLED: return
        print('Balance of %s should be: %s SP%d (%s SP%d reserved)... OK' % (
        source, expected_balance, propertyid, expected_reserved, propertyid,))

    @staticmethod
    def check_orderbook_count_ok(expected_count, property_a, property_b):
        if not TestInfo.ENABLED: return
        print('Number of offers found by getorderbook_MP(SP%s, SP%s) should be: %d... OK' % (
            str(property_a), str(property_b), int(expected_count),))

    @staticmethod
    def check_active_dex_offers_count_ok(expected_count):
        if not TestInfo.ENABLED: return
        print('Number of active offers found by getactivedexsells_MP should be: %d... OK' % (int(expected_count),))

    @staticmethod
    def log(message):
        if not TestInfo.ENABLED: return
        print(str(message))
