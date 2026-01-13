#!/usr/bin/env python3
"""
Test script for libint2 wheel installation.

Run this after installing a libint2 wheel to verify it works correctly.
"""

import sys


def test_import():
    """Test that libint2 can be imported."""
    print("Testing import...", end=" ")
    import libint2
    print(f"OK (version: {libint2.__version__})")
    return libint2


def test_initialize_finalize(libint2):
    """Test initialization and finalization."""
    print("Testing initialize/finalize...", end=" ")
    libint2.initialize()
    assert libint2.initialized(), "libint2 should be initialized"
    libint2.finalize()
    print("OK")


def test_numpy_compatibility():
    """Test numpy compatibility."""
    print("Testing numpy compatibility...", end=" ")
    import numpy as np
    print(f"OK (numpy version: {np.__version__})")


def main():
    print("=" * 50)
    print("libint2 Wheel Test Suite")
    print("=" * 50)
    print()
    
    try:
        libint2 = test_import()
        test_initialize_finalize(libint2)
        test_numpy_compatibility()
        
        print()
        print("=" * 50)
        print("All tests passed!")
        print("=" * 50)
        return 0
        
    except Exception as e:
        print(f"\nFAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
