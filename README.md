#### Please note:

**All new tests will very likely be published as part of https://github.com/OmniLayer/OmniJ.**

Regression tests of RPC interface
=================================

Python based RPC tests for [Omni Core](https://github.com/OmniLayer/omnicore).

To run the tests, place this folder relative to the `omnicored` and `omnicore-cli` files,
or use the `--daemon` and `--cli` startup parameter to specify the binary files to use:

```bash
~/omnicore/qa/mastercore-rpc-tests$ python test_exodus_purchase.py
~/omnicore/qa/mastercore-rpc-tests$ python test_property_creation.py --tracerpc
~/omnicore/qa/mastercore-rpc-tests$ python test_meta_dex_plan.py --clearcache
~/omnicore/qa/mastercore-rpc-tests$ python run_tests.py
```

Potential setup route
=====================

```
git clone https://github.com/OmniLayer/omnicore.git
cd omnicore/
./autogen.sh
./configure
make
cd qa/
git clone https://github.com/dexX7/mastercore-rpc-tests.git
cd mastercore-rpc-tests/
python run_tests.py
```


Testing on Windows
==================

After cloning or [downloading](https://github.com/dexX7/mastercore-rpc-tests/archive/master.zip)
the test suite, all tests may be run on Windows in similar fashion, whereby the
file paths of `omnicored.exe` and `omnicore-cli.exe` must be provided:

```bash
C:\mastercore-rpc-tests> python test_meta_dex_plan.py --daemon=C:\omnicore-0.0.9.99-dev\bin\omnicored.exe --cli=C:\omnicore-0.0.9.99-dev\bin\omnicore-cli.exe
```

Notes
=====

A 200-block-regtest blockchain and wallets for four nodes
is created the first time a regression test is run and
is stored in the cache/ directory. Per default all blocks
are mined by the first node.

After the first run, the cache/blockchain and wallets are
copied into a temporary directory and used as the initial
test state. Temporary files are deleted afterwards, unless
explicitly chosen not to via `--nocleanup`.

The cache can be cleared on startup with `--clearcache`.
This might be required, when significant changes in the initial
parsing phase are made. Omni Core specific data stored in
`MP_persist`, `MP_spinfo`, `MP_tradelist` and `MP_txlist` is
generally not reused and created from the ground up.

Usage and new tests
===================

Four nodes are created to simulate and test behavior of Master
Core. Nodes are exposed as property of a descendant of
[framework_base.py](framework_base.py) and [framework_extension.py](framework_extension.py)
and can be used to interact with Omni Core on the RPC layer.

Starting point is generally `run_test` in an descendant of
`MasterTestFramework`. A very simple test could start like this:

```python
from framework_extension import MasterTestFramework

class VersionTest(MasterTestFramework):
    def run_test(self):
        info = self.nodes[0].getinfo()
        assert info['mastercoreversion'] >= 1111008

if __name__ == '__main__':
    VersionTest().main()
```

However, it might be helpful to encapsulate nodes in `TestEntity`
objects which aligns well with the "address-based" nature of
Mastercoin and due to shortcuts for commonly used calls. See
[framework_entity.py](framework_entity.py) for details. In
combination with `generate_block()` and `check_balance()`, as provided
by [framework_extension.py](framework_extension.py), a wide range of
tests can be constructed.

```python
from framework_extension import MasterTestFramework
from framework_entity import TestEntity

class MinimalExodusPurchaseTest(MasterTestFramework):
    def run_test(self):
        self.entities = [TestEntity(node) for node in self.nodes]
        entity_miner = self.entities[0]
        entity_test_user = self.entities[1]

        entity_miner.send_bitcoins(entity_test_user.address, 5.0)
        self.generate_block()
        entity_test_user.purchase_mastercoins(2.5)
        self.generate_block()

        self.check_balance(entity_test_user.address, 1, '250.00000000')
        self.check_balance(entity_test_user.address, 2, '250.00000000')

if __name__ == '__main__':
    MinimalExodusPurchaseTest().main()
```

Running this example would likely produce an output similar to:
```
Balance of mnSKDy53TD88SkmQaJVTLTSUg8apaPJJ3w should be: 250.00000000 SP1 ... OK
Balance of mnSKDy53TD88SkmQaJVTLTSUg8apaPJJ3w should be: 250.00000000 SP2 ... OK
Cleaning up
Tests successful
```

... a continuation of this can be found in [test_exodus_purchase.py](test_exodus_purchase.py).

Startup options
===============

```
Usage: run_tests.py [options]

Options:
  -h, --help          Show this help message and exit
  --clearcache        Clear cache on startup (default: False)
  --nocleanup         Leave omnicored's and test.* regtest datadir on exit
                      or error (default: False)
  --stdout            Show standard output of nodes, otherwise redirect to
                      /dev/null
  --daemon=DAEMONBIN  The daemon/server (default: ../../src/omnicored)
  --cli=CLIBIN        The RPC client (default: ../../src/omnicore-cli)
  --tmpdir=TMPDIR     Root directory for temporary datadirs
  --tracerpc          Print out all RPC calls as they are made (default:
                      False)
  --quiet             Hide verbose runtime information (default: False)
```

File overview
=============

### [python-bitcoinrpc](https://github.com/jgarzik/python-bitcoinrpc)
Git subtree of [https://github.com/jgarzik/python-bitcoinrpc](https://github.com/jgarzik/python-bitcoinrpc).
Changes to python-bitcoinrpc should be made upstream, and then
pulled here using git subtree.

### [test_exodus_purchase.py](test_exodus_purchase.py)
Simulates the initial redemption of Bitcoin to Mastercoin
as well as Simple Sends.
**This file shoud be used as template and starting point
for new tests.**

### [test_property_creation.py](test_property_creation.py)
Tests the creation of smart properties via the RPC call omni_sendrawtx.

### [test_p2sh.py](test_p2sh.py)
Tests sending and receiving tokens via script-hash destinations.

### [test_meta_dex_plan.py](test_meta_dex_plan.py)
Tests invalidation and rejection of invalid commands and transactions, creation of new orders with divisible
units, matching and execution of offers at the same unit price, matching and execution of offers at a better
unit price and execution of offers with three matches.

### [test_cancel_at_price.py](test_cancel_at_price.py)
Tests the command "cancel-at-price" of the token exchange and the valid cancellation of several offers.

### [test_cancel_pair_and_lookup.py](test_cancel_pair_and_lookup.py)
Tests creation of several offers and cancellation with the "cancel-pair" command as well as the appearance of
offers in the orderbook provided by RPC call omni_getorderbook.

### [test_cancel_everything.py](test_cancel_everything.py)
Tests the effects of valid "cancel-everything" commands of the token exchange within the same ecosystem.

### [test_cancel_everything_scope.py](test_cancel_everything_scope.py)
Tests the scope of the "cancel-everything" command of the token exchange and if it's effects are limited to
the ecosystem they are executed in.

### [test_dex_side_effects.py](test_dex_side_effects.py)
Tests side effects and interferences of the traditional and token exchange.

### [test_traditional_dex.py](test_traditional_dex.py)
Some basic tests for the traditional BTC-MSC exchange.

### [test_sto.py.py](test_sto.py.py)
Tests "send-to-owners" transaction.

### [run_old_tests.py](run_old_tests.py)
Executes tests that should be passed by [Omni Core (mscore-0.0.9)](https://github.com/mastercoin-MSC/mastercore/tree/mscore-0.0.9).

### [run_tests.py](run_tests.py)
Executes tests that are should be passed by [Omni Core (omnicore-0.0.10)](https://github.com/OmniLayer/omnicore/tree/omnicore-0.0.10).
