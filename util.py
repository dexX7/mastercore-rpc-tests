# Copyright (c) 2014 The Bitcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.
#
# Helpful routines for regression testing
#

# Add python-bitcoinrpc to module search path:
import os
import sys
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "python-bitcoinrpc"))

from decimal import Decimal, ROUND_DOWN
import json
import random
import shutil
import subprocess
import time
import re

from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from util import *

RPC_TIMEOUT = 120

def p2p_port(n):
    return 11000 + n + os.getpid() % 999


def rpc_port(n):
    return 12000 + n + os.getpid() % 999


def check_json_precision():
    """
    Make sure json library being used does not lose precision converting BTC values
    """
    n = Decimal("20000000.00000003")
    satoshis = int(json.loads(json.dumps(float(n))) * 1.0e8)
    if satoshis != 2000000000000003:
        raise RuntimeError("JSON encode/decode loses precision")


def sync_blocks(rpc_connections):
    """
    Wait until everybody has the same block count
    """
    while True:
        counts = [x.getblockcount() for x in rpc_connections]
        if counts == [counts[0]] * len(counts):
            return
        time.sleep(1)


def sync_mempools(rpc_connections):
    """
    Wait until everybody has the same transactions in their memory
    pools
    """
    while True:
        pool = set(rpc_connections[0].getrawmempool())
        num_match = 1
        for i in range(1, len(rpc_connections)):
            if set(rpc_connections[i].getrawmempool()) == pool:
                num_match += 1
        if num_match == len(rpc_connections):
            return
        time.sleep(1)


bitcoind_processes = {}


def initialize_datadir(path, n):
    datadir = os.path.join(path, "node" + str(n))
    if not os.path.isdir(datadir):
        os.makedirs(datadir)
    with open(os.path.join(datadir, "bitcoin.conf"), 'w') as f:
        f.write("regtest=1\n")
        f.write("rpcuser=rt\n")
        f.write("rpcpassword=rt\n")
        f.write("port=" + str(p2p_port(n)) + "\n")
        f.write("rpcport=" + str(rpc_port(n)) + "\n")
        f.write("txindedx=1\n")
    return datadir


def initialize_chain(bin_bitcoind, bin_bitcoincli, test_dir, showstdout=False):
    """
    Create (or copy from cache) a 200-block-long chain and
    4 wallets.
    """
    if not os.path.isdir(os.path.join("cache", "node0")):
        devnull = None
        if not showstdout:
            devnull = open("/dev/null", "w+")
        # Create cache directories, run mastercoreds:
        for i in range(4):
            datadir = initialize_datadir("cache", i)
            args = [bin_bitcoind, "-keypool=1", "-datadir=" + datadir, "-discover=0"]
            if i > 0:
                args.append("-connect=127.0.0.1:" + str(p2p_port(0)))
            bitcoind_processes[i] = subprocess.Popen(args, stdout=devnull)
            subprocess.check_call([bin_bitcoincli, "-datadir=" + datadir,
                                   "-rpcwait", "getblockcount"], stdout=devnull)
        if devnull is not None:
            devnull.close()
        rpcs = []
        for i in range(4):
            url = "http://rt:rt@127.0.0.1:%d" % (rpc_port(i),)
            try:
                rpcs.append(AuthServiceProxy(url, None, RPC_TIMEOUT))
            except:
                sys.stderr.write("Error connecting to " + url + "\n")
                sys.exit(1)

        # Create a 200-block-long chain and node 1 gets all
        rpcs[0].setgenerate(True, 200)
        sync_blocks(rpcs)

        # Shut them down, and clean up cache directories:
        stop_nodes(rpcs)
        wait_bitcoinds()
        for i in range(4):
            if not os.path.isdir("cache"):
                continue
            if os.path.isfile(log_filename("cache", i, "db.log")):
                os.remove(log_filename("cache", i, "db.log"))
            if os.path.isfile(log_filename("cache", i, "debug.log")):
                os.remove(log_filename("cache", i, "debug.log"))
            if os.path.isfile(log_filename("cache", i, "mastercore.log")):
                os.remove(log_filename("cache", i, "mastercore.log"))
            if os.path.isfile(log_filename("cache", i, "peers.dat")):
                os.remove(log_filename("cache", i, "peers.dat"))
            if os.path.isfile(log_filename("cache", i, "temp-ok-to-remove.log")):
                os.remove(log_filename("cache", i, "temp-ok-to-remove.log"))
            if os.path.isdir(log_filename("cache", i, "MP_persist")):
                shutil.rmtree(log_filename("cache", i, "MP_persist"))
            if os.path.isdir(log_filename("cache", i, "MP_spinfo")):
                shutil.rmtree(log_filename("cache", i, "MP_spinfo"))
            if os.path.isdir(log_filename("cache", i, "MP_tradelist")):
                shutil.rmtree(log_filename("cache", i, "MP_tradelist"))
            if os.path.isdir(log_filename("cache", i, "MP_txlist")):
                shutil.rmtree(log_filename("cache", i, "MP_txlist"))
            if os.path.isdir(log_filename("cache", i, "MP_stolist")):
                shutil.rmtree(log_filename("cache", i, "MP_stolist"))

    for i in range(4):
        from_dir = os.path.join("cache", "node" + str(i))
        to_dir = os.path.join(test_dir, "node" + str(i))
        shutil.copytree(from_dir, to_dir)
        initialize_datadir(test_dir, i)  # Overwrite port/rpcport in bitcoin.conf


def _rpchost_to_args(rpchost):
    """
    Convert optional IP:port spec to rpcconnect/rpcport args
    """
    if rpchost is None:
        return []

    match = re.match('(\[[0-9a-fA-f:]+\]|[^:]+)(?::([0-9]+))?$', rpchost)
    if not match:
        raise ValueError('Invalid RPC host spec ' + rpchost)

    rpcconnect = match.group(1)
    rpcport = match.group(2)

    if rpcconnect.startswith('['):  # remove IPv6 [...] wrapping
        rpcconnect = rpcconnect[1:-1]

    rv = ['-rpcconnect=' + rpcconnect]
    if rpcport:
        rv += ['-rpcport=' + rpcport]
    return rv


def start_node(i, bin_bitcoind, bin_bitcoincli, path, extra_args=None, rpchost=None, showstdout=False):
    """
    Start a mastercored and return RPC connection to it
    """
    datadir = os.path.join(path, "node" + str(i))
    args = [bin_bitcoind, "-datadir=" + datadir, "-keypool=1", "-discover=0"]
    if extra_args is not None:
        args.extend(extra_args)
    devnull = None
    if not showstdout:
        devnull = open("/dev/null", "w+")
    bitcoind_processes[i] = subprocess.Popen(args, stdout=devnull)
    subprocess.check_call([bin_bitcoincli, "-datadir=" + datadir] +
                          _rpchost_to_args(rpchost) +
                          ["-rpcwait", "getblockcount"], stdout=devnull)
    if devnull is not None:
        devnull.close()
    url = "http://rt:rt@%s:%d" % (rpchost or '127.0.0.1', rpc_port(i))
    proxy = AuthServiceProxy(url, None, RPC_TIMEOUT)
    proxy.url = url  # store URL on proxy for info
    return proxy


def start_nodes(num_nodes, bin_bitcoind, bin_bitcoincli, path, extra_args=None, rpchost=None, showstdout=False):
    """
    Start multiple mastercoreds, return RPC connections to them
    """
    if extra_args is None:
        extra_args = [None for i in range(num_nodes)]
    return [start_node(i, bin_bitcoind, bin_bitcoincli, path, extra_args[i], rpchost, showstdout) for i in range(num_nodes)]


def log_filename(path, n_node, logname):
    return os.path.join(path, "node" + str(n_node), "regtest", logname)


def stop_node(node, i):
    node.stop()
    bitcoind_processes[i].wait()
    del bitcoind_processes[i]


def stop_nodes(nodes):
    for i in range(len(nodes)):
        nodes[i].stop()
    del nodes[:]  # Emptying array closes connections as a side effect


def wait_bitcoinds():
    # Wait for all mastercoreds to cleanly exit
    for bitcoind in bitcoind_processes.values():
        bitcoind.wait()
    bitcoind_processes.clear()


def connect_nodes(from_connection, node_num):
    ip_port = "127.0.0.1:" + str(p2p_port(node_num))
    from_connection.addnode(ip_port, "onetry")
    # poll until version handshake complete to avoid race conditions
    # with transaction relaying
    while any(peer['version'] == 0 for peer in from_connection.getpeerinfo()):
        time.sleep(0.1)


def connect_nodes_bi(nodes, a, b):
    connect_nodes(nodes[a], b)
    connect_nodes(nodes[b], a)


def assert_equal(thing1, thing2, message='%s != %s'):
    if thing1 != thing2:
        raise AssertionError(message % (str(thing1), str(thing2)))


def check_array_result(object_array, to_match, expected):
    """
    Pass in array of JSON objects, a dictionary with key/value pairs
    to match against, and another dictionary with expected key/value
    pairs
    """
    num_matched = 0
    for item in object_array:
        all_match = True
        for key, value in to_match.items():
            if item[key] != value:
                all_match = False
        if not all_match:
            continue
        for key, value in expected.items():
            if item[key] != value:
                raise AssertionError("%s : expected %s=%s" % (str(item), str(key), str(value)))
            num_matched += 1
    if num_matched == 0:
        raise AssertionError("No objects matched %s" % (str(to_match)))
