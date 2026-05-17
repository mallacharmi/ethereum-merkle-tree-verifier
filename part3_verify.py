"""
Part 3 — Reconstruct and Verify Ethereum Transactions Root
Combines Part 1 (Merkle Tree) and Part 2 (block fetching)
to verify real Ethereum transaction inclusion.
"""

import hashlib
import sys

from part1_tree import (
    MerkleTree,
    sha256_leaf,
    sha256_pair,
)

from part2_fetch import (
    fetch_block,
    inspect_block,
    get_rpc_url,
)


# ============================================================
# Transaction Hashing
# ============================================================

def hash_transaction_simple(tx: dict) -> bytes:
    """
    Simplified transaction hashing:
    SHA-256 of transaction hash string.
    """
    return hashlib.sha256(
        tx["hash"].encode()
    ).digest()


def hash_transaction(tx: dict) -> bytes:
    """
    Main transaction hash dispatcher.
    """
    return hash_transaction_simple(tx)


# ============================================================
# Root Reconstruction
# ============================================================

def reconstruct_transactions_root(
    transactions: list[dict]
) -> bytes:
    """
    Reconstruct Merkle root from block transactions.
    """

    if not transactions:
        raise ValueError("No transactions found.")

    raw_leaves = [
        tx["hash"].encode()
        for tx in transactions
    ]

    tree = MerkleTree(raw_leaves)

    return tree.root


def verify_transactions_root(
    block: dict
) -> bool:
    """
    Compare reconstructed root against block header root.
    """

    transactions = block.get("transactions", [])

    if not transactions:
        print("No transactions found.")
        return False

    expected_root = block["transactionsRoot"]

    computed_root = reconstruct_transactions_root(
        transactions
    )

    computed_root_hex = "0x" + computed_root.hex()

    print(f"\n  Expected root (from block header) : {expected_root}")
    print(f"  Computed root (our Merkle tree)   : {computed_root_hex}")

    if computed_root_hex.lower() == expected_root.lower():

        print(
            "  ✓ Roots MATCH"
        )

        return True

    else:

        print(
            "  ✗ Roots do NOT match."
        )

        print(
            "    (Expected because Ethereum uses Merkle Patricia Trie + Keccak.)"
        )

        return False


# ============================================================
# Inclusion Proof Verification
# ============================================================

def prove_transaction_inclusion(
    block: dict,
    tx_index: int,
) -> bool:
    """
    Generate and verify inclusion proof.
    """

    transactions = block.get("transactions", [])

    if not transactions:
        print("No transactions found.")
        return False

    if tx_index >= len(transactions):
        raise IndexError("Invalid tx index.")

    print(f"\n{'='*60}")
    print(f"Transaction Inclusion Proof (index {tx_index})")
    print(f"{'='*60}")

    # Build tree from RAW tx hashes
    raw_leaves = [
        tx["hash"].encode()
        for tx in transactions
    ]

    tree = MerkleTree(raw_leaves)

    target_tx = transactions[tx_index]

    target_leaf_hash = sha256_leaf(
        target_tx["hash"].encode()
    )

    print(f"  Target tx hash : {target_tx['hash']}")
    print(f"  Leaf hash      : {target_leaf_hash.hex()}")
    print(f"  Tree root      : {tree.root.hex()}")

    # Generate proof
    proof = tree.get_proof(tx_index)

    print(f"\n  Proof path ({len(proof)} steps):")

    for i, step in enumerate(proof):

        print(
            f"    Step {i+1}: "
            f"position={step['position']}, "
            f"hash={step['hash'].hex()[:16]}..."
        )

    # Verify proof
    current = target_leaf_hash

    for step in proof:

        sibling_hash = step["hash"]

        if step["position"] == "right":

            current = sha256_pair(
                current,
                sibling_hash,
            )

        else:

            current = sha256_pair(
                sibling_hash,
                current,
            )

    verified = current == tree.root

    if verified:

        print("\n  ✓ Proof VERIFIED: True")

    else:

        print("\n  ✗ Proof VERIFIED: False")

    # Tampered proof test
    tampered_proof = [
        dict(step)
        for step in proof
    ]

    if tampered_proof:

        tampered_proof[0]["hash"] = b"\x00" * 32

        tampered_current = target_leaf_hash

        for step in tampered_proof:

            sibling_hash = step["hash"]

            if step["position"] == "right":

                tampered_current = sha256_pair(
                    tampered_current,
                    sibling_hash,
                )

            else:

                tampered_current = sha256_pair(
                    sibling_hash,
                    tampered_current,
                )

        tampered_verified = (
            tampered_current == tree.root
        )

        print(
            f"  ✓ Tampered proof rejected: "
            f"{not tampered_verified}"
        )

    return verified


# ============================================================
# Light Client Simulation
# ============================================================

def light_client_verify(
    tx_hash: str,
    proof: list[dict],
    expected_root: bytes,
) -> bool:
    """
    Simulate light client verification.
    """

    current = sha256_leaf(
        tx_hash.encode()
    )

    for step in proof:

        sibling_hash = step["hash"]

        if step["position"] == "right":

            current = sha256_pair(
                current,
                sibling_hash,
            )

        else:

            current = sha256_pair(
                sibling_hash,
                current,
            )

    return current == expected_root


# ============================================================
# Main
# ============================================================

def main():

    print("=" * 60)
    print("Part 3 — End-to-End Ethereum Transaction Verification")
    print("=" * 60)

    rpc_url = get_rpc_url()

    print("\nFetching latest Ethereum block...")

    block = fetch_block(
        rpc_url,
        "latest"
    )

    inspect_block(block)

    transactions = block.get(
        "transactions",
        []
    )

    if not transactions:

        print("No transactions found.")
        sys.exit(1)

    print(f"\n{'='*60}")
    print("Step 3.2 — Reconstruct Transactions Root")
    print(f"{'='*60}")

    verify_transactions_root(block)

    # First transaction proof
    proof_verified = prove_transaction_inclusion(
        block,
        0,
    )

    # Last transaction proof
    if len(transactions) > 1:

        prove_transaction_inclusion(
            block,
            len(transactions) - 1,
        )

    # ========================================================
    # Light Client Verification
    # ========================================================

    print(f"\n{'='*60}")
    print("Extension C — Light Client Simulation")
    print(f"{'='*60}")

    raw_leaves = [
        tx["hash"].encode()
        for tx in transactions
    ]

    tree = MerkleTree(raw_leaves)

    proof = tree.get_proof(0)

    target_tx_hash = transactions[0]["hash"]

    result = light_client_verify(
        tx_hash=target_tx_hash,
        proof=proof,
        expected_root=tree.root,
    )

    if result:

        print(
            "  ✓ Light client verification result: Verified"
        )

    else:

        print(
            "  ✗ Light client verification result: Failed"
        )

    print(
        "  (Using reconstructed root for demonstration)"
    )

    print(f"\n{'='*60}")
    print("All steps complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()