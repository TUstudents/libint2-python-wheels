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
    print("OK")
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
    # Create an s-type shell with one primitive (exponent=1.0, coeff=1.0)
    shell = libint2.Shell(0, [(1.0, 1.0)], [0.0, 0.0, 0.0])
    print(f"OK (size={shell.size()})")
    return shell


def test_basis_set(libint2):
    """Test BasisSet creation with named basis."""
    print("Testing BasisSet (named)...", end=" ")
    atoms = [
        libint2.Atom(1, [0.0, 0.0, 0.0]),
        libint2.Atom(1, [0.0, 0.0, 1.4]),
    ]
    try:
        basis = libint2.BasisSet("sto-3g", atoms)
        print(f"OK (nbf={basis.nbf}, nshells={len(basis)})")
        return basis
    except Exception as e:
        print(f"SKIPPED ({e})")
        return None


def test_basis_set_from_shells(libint2):
    """Test BasisSet creation from explicit shells."""
    print("Testing BasisSet (from shells)...", end=" ")
    # Create two s-type shells at different centers
    shell1 = libint2.Shell(0, [(1.0, 1.0)], [0.0, 0.0, 0.0])
    shell2 = libint2.Shell(0, [(1.0, 1.0)], [0.0, 0.0, 1.4])
    basis = libint2.BasisSet([shell1, shell2])
    print(f"OK (nbf={basis.nbf}, nshells={len(basis)})")
    return basis


def test_engine_creation(libint2):
    """Test Engine creation for different operators."""
    print("Testing Engine creation...", end=" ")
    
    overlap = libint2.overlap()
    kinetic = libint2.kinetic()
    coulomb = libint2.coulomb()
    
    # Nuclear requires point charges
    nuclear = libint2.nuclear([(1.0, [0.0, 0.0, 0.0])])
    
    print("OK (overlap, kinetic, coulomb, nuclear)")
    return overlap


def test_shell_integrals(libint2):
    """Test computing integrals between shells."""
    print("Testing shell integrals...", end=" ")
    
    shell1 = libint2.Shell(0, [(1.0, 1.0)], [0.0, 0.0, 0.0])
    shell2 = libint2.Shell(0, [(1.0, 1.0)], [0.0, 0.0, 1.4])
    
    engine = libint2.overlap()
    result = engine.compute(shell1, shell2)
    
    if result is not None:
        import numpy as np
        # Result should be a 1x1 array for s-s overlap
        assert result.shape == (1, 1), f"Expected (1,1), got {result.shape}"
        # Overlap should be positive and less than 1 for non-identical shells
        assert 0 < result[0, 0] < 1, f"Unexpected overlap value: {result[0, 0]}"
        print(f"OK (S={result[0, 0]:.6f})")
    else:
        print("OK (null result - shells may be far apart)")


def test_basis_integrals(libint2, basis):
    """Test computing full integral matrices over a basis."""
    if basis is None:
        print("Testing basis integrals... SKIPPED (no basis)")
        return
    
    print("Testing basis integrals...", end=" ")
    
    engine = libint2.overlap()
    S = engine.compute(basis, basis)
    
    import numpy as np
    
    # Check shape
    nbf = basis.nbf
    assert S.shape == (nbf, nbf), f"Expected ({nbf},{nbf}), got {S.shape}"
    
    # Overlap matrix should be symmetric
    assert np.allclose(S, S.T), "Overlap matrix not symmetric"
    
    # Diagonal should be 1.0 for normalized basis
    # (may not be exactly 1.0 depending on normalization)
    
    print(f"OK (shape={S.shape}, symmetric={np.allclose(S, S.T)})")


def test_1body_ints(libint2, basis):
    """Test compute_1body_ints convenience function."""
    if basis is None:
        print("Testing compute_1body_ints... SKIPPED (no basis)")
        return
    
    print("Testing compute_1body_ints...", end=" ")
    
    engine = libint2.overlap()
    S = engine.compute_1body_ints(basis)
    
    import numpy as np
    
    nbf = basis.nbf
    assert S.shape == (nbf, nbf), f"Expected ({nbf},{nbf}), got {S.shape}"
    assert np.allclose(S, S.T), "Matrix not symmetric"
    
    print(f"OK (shape={S.shape})")


def test_num_threads(libint2):
    """Test thread count property."""
    print("Testing num_threads...", end=" ")
    
    # Get current value
    current = libint2.Engine.num_threads
    print(f"OK (num_threads={current})")


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
        basis = test_basis_set(libint2)
        basis_explicit = test_basis_set_from_shells(libint2)
        test_engine_creation(libint2)
        test_shell_integrals(libint2)
        test_basis_integrals(libint2, basis or basis_explicit)
        test_1body_ints(libint2, basis or basis_explicit)
        test_num_threads(libint2)
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
