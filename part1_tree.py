"""
Part 1 — Merkle Tree Implementation in Python
Implements MerkleNode, MerkleTree, proof generation, and verification.
"""

import hashlib
from dataclasses import dataclass, field


def sha256_pair(left: bytes, right: bytes) -> bytes:
    """Hash two child digests together to produce a parent node hash."""
    return hashlib.sha256(left + right).digest()


def sha256_leaf(data: bytes) -> bytes:
    """Hash raw data to produce a leaf node hash."""
    return hashlib.sha256(data).digest()


@dataclass
class MerkleNode:
    hash: bytes
    left: "MerkleNode | None" = field(default=None, repr=False)
    right: "MerkleNode | None" = field(default=None, repr=False)


class MerkleTree:
    def __init__(self, leaves: list[bytes]):
        """
        Build a Merkle tree from raw data items.
        Each item is hashed internally to form a leaf node.
        """
        if not leaves:
            raise ValueError("Cannot build a Merkle tree with no leaves.")

        self._leaves_data = leaves

        # Hash raw leaves internally
        leaf_nodes = [MerkleNode(hash=sha256_leaf(item)) for item in leaves]

        self._root_node = self._build(leaf_nodes)

    def _build(self, nodes: list[MerkleNode]) -> MerkleNode:
        """
        Recursively pair up nodes and hash each pair until one root remains.
        """
        if len(nodes) == 1:
            return nodes[0]

        # Duplicate last node if odd
        if len(nodes) % 2 == 1:
            nodes = nodes + [nodes[-1]]

        next_level = []

        for i in range(0, len(nodes), 2):
            left = nodes[i]
            right = nodes[i + 1]

            parent_hash = sha256_pair(left.hash, right.hash)

            parent = MerkleNode(
                hash=parent_hash,
                left=left,
                right=right,
            )

            next_level.append(parent)

        return self._build(next_level)

    @property
    def root(self) -> bytes:
        """Return the Merkle root hash."""
        return self._root_node.hash

    def get_proof(self, index: int) -> list[dict]:
        """
        Generate a Merkle proof for the leaf at the given index.
        """
        n = len(self._leaves_data)

        if index < 0 or index >= n:
            raise IndexError(f"Index {index} out of range.")

        proof = []

        current_level = [
            sha256_leaf(item)
            for item in self._leaves_data
        ]

        current_index = index

        while len(current_level) > 1:

            level = current_level[:]

            # Duplicate odd node
            if len(level) % 2 == 1:
                level.append(level[-1])

            if current_index % 2 == 0:
                sibling_index = current_index + 1

                proof.append({
                    "hash": level[sibling_index],
                    "position": "right",
                })

            else:
                sibling_index = current_index - 1

                proof.append({
                    "hash": level[sibling_index],
                    "position": "left",
                })

            # Build next level
            next_level = []

            for i in range(0, len(level), 2):
                next_hash = sha256_pair(
                    level[i],
                    level[i + 1],
                )

                next_level.append(next_hash)

            current_level = next_level
            current_index = current_index // 2

        return proof


def verify_proof(
    leaf_data: bytes,
    proof: list[dict],
    expected_root: bytes,
) -> bool:
    """
    Verify a Merkle proof without access to the full tree.
    """

    current_hash = sha256_leaf(leaf_data)

    for step in proof:

        sibling_hash = step["hash"]
        position = step["position"]

        if position == "right":
            current_hash = sha256_pair(
                current_hash,
                sibling_hash,
            )

        else:
            current_hash = sha256_pair(
                sibling_hash,
                current_hash,
            )

    return current_hash == expected_root


# ============================================================
# LOCAL TESTS
# ============================================================

def run_tests():

    print("=" * 60)
    print("Part 1 — Merkle Tree Tests")
    print("=" * 60)

    # Test 1
    items = [b"alice", b"bob", b"carol", b"dave"]

    tree = MerkleTree(items)

    print(f"Root (4 leaves): {tree.root.hex()}")

    proof = tree.get_proof(2)

    assert verify_proof(
        b"carol",
        proof,
        tree.root,
    ), "✗ Valid proof failed!"

    print("✓ Valid proof for 'carol' verified successfully.")

    # Tampered leaf
    assert not verify_proof(
        b"mallory",
        proof,
        tree.root,
    ), "✗ Tampered leaf should fail!"

    print("✓ Tampered leaf data correctly rejected.")

    # Tampered proof
    tampered_proof = [dict(step) for step in proof]

    tampered_proof[0]["hash"] = b"\x00" * 32

    assert not verify_proof(
        b"carol",
        tampered_proof,
        tree.root,
    ), "✗ Tampered proof should fail!"

    print("✓ Tampered proof hash correctly rejected.")

    # Test 2 — odd leaves
    odd_items = [b"a", b"b", b"c"]

    odd_tree = MerkleTree(odd_items)

    print(f"\nRoot (3 leaves, odd): {odd_tree.root.hex()}")

    for i, item in enumerate(odd_items):

        pf = odd_tree.get_proof(i)

        assert verify_proof(
            item,
            pf,
            odd_tree.root,
        )

    print("✓ All proofs verified for odd-leaf tree.")

    # Test 3 — single leaf
    single_tree = MerkleTree([b"only"])

    pf = single_tree.get_proof(0)

    assert verify_proof(
        b"only",
        pf,
        single_tree.root,
    )

    print("✓ Single-leaf tree verified.")

    # Test 4 — all leaves
    for i, item in enumerate(items):

        pf = tree.get_proof(i)

        assert verify_proof(
            item,
            pf,
            tree.root,
        )

    print("✓ All proofs verified for all 4 leaves.")

    print("\nAll Part 1 tests passed! ✓")
    print("=" * 60)


if __name__ == "__main__":
    run_tests()