Regression tests of RPC interface
=================================

To run the tests, place this folder relative to the
`mastercored` and `mastercore-cli` files or use `--srcdir`
as startup parameter, pointing to [Master Core](https://github.com/mastercoin-MSC/mastercore):

```bash
python test_exodus_purchase.py --srcdir=~/mastercore/
python test_property_creation.py --tracerpc --nocleanup
python test_one_step_trades.py --clearcache
python run_tests.py
```

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
Tests the creation of smart properties via the RPC call 
`sendrawtx_MP`.

### [test_p2sh.py](test_p2sh.py)
Tests sending and receiving tokens via script-hash destinations.

### [test_one_step_trades.py](test_one_step_trades.py)
Tests the distributed exchange.

### [run_tests.py](run_tests.py)
Executes all tests that are currently available.

Usage and new tests
===================

Four nodes are created to simulate and test behavior of Master
Core. Nodes are exposed as property of a descendant of 
[framework_base.py](framework_base.py) and [framework_extension.py](framework_extension.py)
and can be used to interact with Master Core on the RPC layer.

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

In fact, this example could be saved as `test_purchase.py` and then tested 
by `python test_purchase.py --srcdir=/path-to-src-dir-with-mastercored`.

... a continuation of this can be found in [test_exodus_purchase.py](test_exodus_purchase.py).

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
parsing phase are made. Master Core specific data stored in 
`MP_persist`, `MP_spinfo`, `MP_tradelist` and `MP_txlist` is
generally not reused and created from the ground up.

Startup options
===============

```
Usage: run_tests.py [options]

Options:
  -h, --help       show this help message and exit
  --clearcache     clear cache on startup
  --distinctminer  if enabled, mine only with first node, otherwise use all
  --nocleanup      leave mastercored's and test.* regtest datadir on exit or
                   error
  --srcdir=SRCDIR  source directory containing mastercored/mastercore-cli
                   (default: ../../src)
  --tmpdir=TMPDIR  root directory for temporary datadirs
  --tracerpc       print out all RPC calls as they are made
  --verbose        provide additional runtime information of common calls

```

Potential setup route
=====================

```
git clone https://github.com/mastercoin-MSC/mastercore.git
cd mastercore/
git checkout mscore-0.0.9
./autogen.sh
./configure
make
cd qa/
git clone https://github.com/dexX7/mastercore-rpc-tests.git
cd mastercore-rpc-tests/
python run_tests.py
```
