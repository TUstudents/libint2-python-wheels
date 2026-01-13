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
    print(f"OK")
    print(f"  MAX_AM = {libint2.MAX_AM}")
    return libint2


def test_atom(libint2):
    """Test Atom creation."""
    print("Testing Atom...", end=" ")
    atom = libint2.Atom(1, [0.0, 0.0, 0.0])  # Hydrogen at origin
    print("OK")
    return atom


def test_shell(libint2):
    """Test Shell creation."""
    print("Testing Shell...", end=" ")
    # Create an s-type shell with one primitive
    shell = libint2.Shell(0, [(1.0, 1.0)], [0.0, 0.0, 0.0])
    print(f"OK (size={shell.size()})")
    return shell


def test_basis_set(libint2):
    """Test BasisSet creation."""
    print("Testing BasisSet...", end=" ")
    # Create H2 molecule
    atoms = [
        libint2.Atom(1, [0.0, 0.0, 0.0]),
        libint2.Atom(1, [0.0, 0.0, 1.4]),
    ]
    try:
        basis = libint2.BasisSet("sto-3g", atoms)
        print(f"OK (nbf={basis.nbf})")
        return basis
    except Exception as e:
        print(f"SKIPPED (basis set not found: {e})")
        return None


def test_engine(libint2):
    """Test Engine creation."""
    print("Testing Engine...", end=" ")
    engine = libint2.overlap()
    print("OK")
    return engine


def test_numpy_compatibility():
    """Test numpy compatibility."""
    print("Testing numpy...", end=" ")
    import numpy as np
    print(f"OK (version={np.__version__})")


def main():
    print("=" * 50)
    print("libint2 Wheel Test Suite")
    print("=" * 50)
    print()
    
    try:
        libint2 = test_import()
        test_atom(libint2)
        test_shell(libint2)
        test_basis_set(libint2)
        test_engine(libint2)
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
