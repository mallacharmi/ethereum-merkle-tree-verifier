"""
Part 2 — Fetch Real Ethereum Data via JSON-RPC
Fetches block data and transaction info from an Ethereum node.
"""

import os
import json
import requests
from typing import Union


def _rpc_call(rpc_url: str, method: str, params: list) -> dict:
    """Generic JSON-RPC call helper."""
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": method,
        "params": params,
    }
    response = requests.post(rpc_url, json=payload, timeout=30)
    response.raise_for_status()
    data = response.json()
    if "error" in data:
        raise RuntimeError(f"RPC error: {data['error']}")
    return data["result"]


def fetch_block(rpc_url: str, block_number: Union[int, str] = "latest") -> dict:
    """
    Fetch a full block (with transactions) from an Ethereum JSON-RPC endpoint.
    Returns the raw block dict including transactionsRoot and the transactions list.
    block_number can be an integer or "latest".
    """
    if isinstance(block_number, int):
        block_param = hex(block_number)
    else:
        block_param = block_number  # "latest", "earliest", etc.

    block = _rpc_call(rpc_url, "eth_getBlockByNumber", [block_param, True])
    if block is None:
        raise ValueError(f"Block {block_number} not found.")
    return block


def fetch_transaction(rpc_url: str, tx_hash: str) -> dict:
    """
    Fetch a single transaction by its hash.
    Returns the transaction dict including blockNumber, blockHash, transactionIndex.
    """
    tx = _rpc_call(rpc_url, "eth_getTransactionByHash", [tx_hash])
    if tx is None:
        raise ValueError(f"Transaction {tx_hash} not found.")
    return tx


def fetch_transaction_receipt(rpc_url: str, tx_hash: str) -> dict:
    """
    Fetch the receipt for a transaction.
    """
    receipt = _rpc_call(rpc_url, "eth_getTransactionReceipt", [tx_hash])
    if receipt is None:
        raise ValueError(f"Receipt for {tx_hash} not found.")
    return receipt


def inspect_block(block: dict) -> None:
    """
    Print the block number, timestamp, transaction count,
    and most importantly the transactionsRoot.
    """
    number = int(block["number"], 16) if isinstance(block["number"], str) else block["number"]
    timestamp = int(block["timestamp"], 16) if isinstance(block["timestamp"], str) else block["timestamp"]
    tx_count = len(block.get("transactions", []))
    
    print("=" * 60)
    print("Block Information")
    print("=" * 60)
    print(f"  Block Number     : {number}")
    print(f"  Timestamp        : {timestamp}")
    print(f"  Miner/Validator  : {block.get('miner', 'N/A')}")
    print(f"  Gas Used         : {int(block['gasUsed'], 16):,}")
    print(f"  Gas Limit        : {int(block['gasLimit'], 16):,}")
    print(f"  Transaction Count: {tx_count}")
    print(f"  Transactions Root: {block['transactionsRoot']}")
    print(f"  State Root       : {block.get('stateRoot', 'N/A')}")
    print(f"  Block Hash       : {block.get('hash', 'N/A')}")
    print("=" * 60)

    if tx_count > 0:
        print(f"\nFirst transaction hash : {block['transactions'][0]['hash']}")
        if tx_count > 1:
            print(f"Last transaction hash  : {block['transactions'][-1]['hash']}")


def get_rpc_url() -> str:
    """Read RPC URL from environment variable or .env file."""
    rpc_url = os.environ.get("ETH_RPC_URL")
    if not rpc_url:
        # Try reading from .env manually
        env_path = os.path.join(os.path.dirname(__file__), ".env")
        if os.path.exists(env_path):
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("ETH_RPC_URL="):
                        rpc_url = line.split("=", 1)[1].strip().strip('"').strip("'")
                        break
    if not rpc_url:
        raise EnvironmentError(
            "ETH_RPC_URL not set. Please set it in your environment or .env file.\n"
            "Get a free key at https://www.alchemy.com or https://infura.io"
        )
    return rpc_url


if __name__ == "__main__":
    rpc_url = get_rpc_url()
    print(f"Connecting to Ethereum node...")
    
    block = fetch_block(rpc_url, "latest")
    inspect_block(block)
    
    txs = block.get("transactions", [])
    if txs:
        print(f"\nSample transaction (index 0):")
        tx = txs[0]
        print(f"  Hash  : {tx['hash']}")
        print(f"  From  : {tx['from']}")
        print(f"  To    : {tx.get('to', 'Contract Creation')}")
        print(f"  Value : {int(tx['value'], 16) / 1e18:.6f} ETH")
        print(f"  Nonce : {int(tx['nonce'], 16)}")
