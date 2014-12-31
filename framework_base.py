#!/usr/bin/env python2
# Copyright (c) 2014 The Bitcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

# Base class for RPC testing

# Add python-bitcoinrpc to module search path:
import os
import sys
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "python-bitcoinrpc"))

import shutil
import tempfile
import traceback

from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from util import *


class BitcoinTestFramework(object):
    # These may be over-ridden by subclasses:
    def run_test(self):
        for node in self.nodes:
            assert_equal(node.getblockcount(), 200)
        if not self.options.distinctminer:
            assert_equal(self.nodes[0].getbalance(), 100 * 50)
            return
        for node in self.nodes:
            assert_equal(node.getbalance(), 25 * 50)

    def add_options(self, parser):
        pass

    def setup_chain(self):
        print("Initializing test directory " + self.options.tmpdir)
        initialize_chain(self.options.tmpdir, self.options.showstdout)

    def setup_network(self, split=False):
        self.nodes = start_nodes(4, self.options.tmpdir, showstdout=self.options.showstdout)

        # Connect the nodes as a "chain".  This allows us
        # to split the network between nodes 1 and 2 to get
        # two halves that can work on competing chains.

        # If we joined network halves, connect the nodes from the joint
        # on outward.  This ensures that chains are properly reorganised.
        if not split:
            connect_nodes_bi(self.nodes, 1, 2)
            sync_blocks(self.nodes[1:3])
            sync_mempools(self.nodes[1:3])

        connect_nodes_bi(self.nodes, 0, 1)
        connect_nodes_bi(self.nodes, 2, 3)
        self.is_network_split = split
        self.sync_all()

    def split_network(self):
        """
        Split the network of four nodes into nodes 0/1 and 2/3.
        """
        assert not self.is_network_split
        stop_nodes(self.nodes)
        wait_bitcoinds()
        self.setup_network(True)

    def sync_all(self):
        if self.is_network_split:
            sync_blocks(self.nodes[:2])
            sync_blocks(self.nodes[2:])
            sync_mempools(self.nodes[:2])
            sync_mempools(self.nodes[2:])
        else:
            sync_blocks(self.nodes)
            sync_mempools(self.nodes)

    def join_network(self):
        """
        Join the (previously split) network halves together.
        """
        assert self.is_network_split
        stop_nodes(self.nodes)
        wait_bitcoinds()
        self.setup_network(False)

    def main(self):        
        # during runtime change dir to the dir of the framework,
        # because most calls assume it's executed from within the
        # same dir
        initial_working_dir = os.getcwd()
        os.chdir(sys.path[0])

        import optparse
        parser = optparse.OptionParser(usage="%prog [options]")
        parser.add_option("--clearcache", dest="clearcache", default=False, action="store_true",
                          help="Clear cache on startup (default: %default)")
        parser.add_option("--nocleanup", dest="nocleanup", default=False, action="store_true",
                          help="Leave mastercored's and test.* regtest datadir on exit or error (default: %default)")
        parser.add_option("--stdout", dest="showstdout", default=False, action="store_true",
                          help="Show standard output of nodes, otherwise redirect to /dev/null")
        parser.add_option("--bindir", dest="bindir", default="../../src",
                          help="Directory containing daemon and cli binaries (default: %default)")
        parser.add_option("--tmpdir", dest="tmpdir", default=tempfile.mkdtemp(prefix="test"),
                          help="Root directory for temporary datadirs")
        parser.add_option("--tracerpc", dest="trace_rpc", default=False, action="store_true",
                          help="Print out all RPC calls as they are made (default: %default)")
        parser.add_option("--quiet", dest="quiet", default=False, action="store_true",
                          help="Hide verbose runtime information (default: %default)")
        self.add_options(parser)
        (self.options, self.args) = parser.parse_args()

        if self.options.trace_rpc:
            import logging
            logging.basicConfig(level=logging.DEBUG)

        if self.options.quiet:
            from framework_info import TestInfo
            TestInfo.ENABLED = 0

        if self.options.bindir:
            os.environ['PATH'] = self.options.bindir + ":" + os.environ['PATH']

        check_json_precision()

        self.success = False
        try:
            if self.options.clearcache and os.path.isdir("cache"):
                print("Clear cache")
                shutil.rmtree("cache")
            if not os.path.isdir(self.options.tmpdir):
                os.makedirs(self.options.tmpdir)
            self.setup_chain()

            self.setup_network()

            self.run_test()

            self.success = True

        except JSONRPCException as e:
            print("JSONRPC error: " + e.error['message'])
            traceback.print_tb(sys.exc_info()[2])
        except AssertionError as e:
            print("Assertion failed: " + e.message)
            traceback.print_tb(sys.exc_info()[2])
        except Exception as e:
            print("Unexpected exception caught during testing: " + str(e))
            traceback.print_tb(sys.exc_info()[2])

        if not self.options.nocleanup:
            print("Cleaning up")
            stop_nodes(self.nodes)
            wait_bitcoinds()
            shutil.rmtree(self.options.tmpdir)

        # restore initial working dir
        os.chdir(initial_working_dir)

        test_name = self.__class__.__name__
        if self.success:
            print(test_name + " ... successful")
            return 0
        else:
            print(test_name + " ... failed")
            return 1
