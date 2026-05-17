"""
Main entry point — runs all three parts in sequence.
Usage: python main.py
"""

import sys

def main():
    print("\n" + "█" * 60)
    print("  Ethereum Merkle Tree Verifier")
    print("  Part 1 → Part 2 → Part 3")
    print("█" * 60 + "\n")

    # Part 1
    print(">>> Running Part 1: Merkle Tree Tests\n")
    from part1_tree import run_tests
    run_tests()

    # Part 2
    print("\n>>> Running Part 2: Ethereum Block Fetch\n")
    try:
        from part2_fetch import fetch_block, inspect_block, get_rpc_url
        rpc_url = get_rpc_url()
        block = fetch_block(rpc_url, "latest")
        inspect_block(block)
        print("\nPart 2 complete ✓")
    except EnvironmentError as e:
        print(f"ERROR: {e}")
        print("Skipping Parts 2 & 3 — set ETH_RPC_URL and retry.")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR fetching block: {e}")
        sys.exit(1)

    # Part 3
    print("\n>>> Running Part 3: End-to-End Verification\n")
    from part3_verify import main as part3_main
    part3_main()


if __name__ == "__main__":
    main()
