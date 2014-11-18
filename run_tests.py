#!/usr/bin/python
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

from test_exodus_purchase import ExodusPurchaseTest
from test_meta_dex_plan import MetaDexPlanTest
from test_property_creation import PropertyCreationTest
from test_p2sh import P2SHTest
from test_one_step_trades import OneStepTradeTest


if __name__ == '__main__':
    ExodusPurchaseTest().main()
    PropertyCreationTest().main()
    P2SHTest().main()
    MetaDexPlanTest().main
    OneStepTradeTest().main()
