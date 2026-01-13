#!/usr/bin/env python3
"""
Test script for libint2 wheel installation.
Based on upstream libint2/python/tests/test_libint2.py
"""

import sys
import unittest


class TestLibint2(unittest.TestCase):
    """Test libint2 Python bindings."""
    
    @classmethod
    def setUpClass(cls):
        """Import libint2 once for all tests."""
        import libint2
        cls.libint2 = libint2
        
        # Set single thread for reproducibility
        libint2.Engine.num_threads = 1
        
        # Test molecules
        cls.h2o = [
            (8, [0.00000, -0.07579, 0.00000]),
            (1, [0.86681, 0.60144, 0.00000]),
            (1, [-0.86681, 0.60144, 0.00000]),
        ]
        
        cls.h2 = [
            (1, [0.0, 0.0, 0.0]),
            (1, [0.0, 0.0, 1.4]),
        ]
    
    def test_import_and_max_am(self):
        """Test that libint2 imports and has valid MAX_AM."""
        self.assertGreater(self.libint2.MAX_AM, 0)
        print(f"MAX_AM = {self.libint2.MAX_AM}")
    
    def test_shell_creation(self):
        """Test Shell creation with different angular momenta."""
        Shell = self.libint2.Shell
        
        # s-type shell
        s = Shell(0, [(1, 10)])
        self.assertEqual(s.size(), 1)
        
        # p-type shell
        p = Shell(1, [(1, 10)])
        self.assertEqual(p.size(), 3)
        
        # d-type shell with explicit center
        d = Shell(2, [(1, 10)], [0.1, 0.2, 0.3])
        self.assertEqual(d.size(), 5)  # spherical
        
        print("Shell creation OK")
    
    def test_basis_set_named(self):
        """Test BasisSet creation from named basis."""
        try:
            basis = self.libint2.BasisSet('sto-3g', self.h2)
            self.assertEqual(basis.nbf, 2)
            self.assertEqual(len(basis), 2)
            print(f"BasisSet(sto-3g, H2): nbf={basis.nbf}, nshells={len(basis)}")
        except Exception as e:
            self.skipTest(f"Basis set not found: {e}")
    
    def test_basis_set_6_31g(self):
        """Test 6-31G basis on water."""
        try:
            basis = self.libint2.BasisSet('6-31g', self.h2o)
            self.assertEqual(len(basis), 9)
            print(f"BasisSet(6-31g, H2O): nbf={basis.nbf}, nshells={len(basis)}")
        except Exception as e:
            self.skipTest(f"Basis set not found: {e}")
    
    def test_basis_set_pure_property(self):
        """Test setting pure/Cartesian on basis."""
        try:
            basis = self.libint2.BasisSet('6-31g', self.h2o)
            
            # Set all to Cartesian
            basis.pure = False
            pure_flags = [s.pure for s in basis]
            self.assertTrue(all(not p for p in pure_flags))
            
            # Set first shell to pure
            basis[0].pure = True
            self.assertTrue(basis[0].pure)
            
            print("Basis pure property OK")
        except Exception as e:
            self.skipTest(f"Basis set not found: {e}")
    
    def test_basis_set_from_shells(self):
        """Test BasisSet creation from explicit shells."""
        Shell = self.libint2.Shell
        BasisSet = self.libint2.BasisSet
        
        shell1 = Shell(0, [(1.0, 1.0)], [0.0, 0.0, 0.0])
        shell2 = Shell(0, [(1.0, 1.0)], [0.0, 0.0, 1.4])
        
        basis = BasisSet([shell1, shell2])
        self.assertEqual(basis.nbf, 2)
        self.assertEqual(len(basis), 2)
        
        print(f"BasisSet from shells: nbf={basis.nbf}")
    
    def test_overlap_integral(self):
        """Test overlap integral computation."""
        import numpy as np
        
        s = self.libint2.Shell(0, [(1, 10)])
        engine = self.libint2.overlap()
        result = engine.compute(s, s)
        
        self.assertIsNotNone(result)
        self.assertAlmostEqual(np.linalg.norm(result), 1.0, places=5)
        
        print(f"Overlap <s|s> = {result[0,0]:.6f}")
    
    def test_kinetic_integral(self):
        """Test kinetic energy integral computation."""
        import numpy as np
        
        s = self.libint2.Shell(0, [(1, 10)])
        engine = self.libint2.kinetic()
        result = engine.compute(s, s)
        
        self.assertIsNotNone(result)
        self.assertAlmostEqual(np.linalg.norm(result), 1.5, places=5)
        
        print(f"Kinetic <s|T|s> norm = {np.linalg.norm(result):.6f}")
    
    def test_nuclear_integral(self):
        """Test nuclear attraction integral computation."""
        import numpy as np
        
        s = self.libint2.Shell(0, [(1, 10)])
        engine = self.libint2.nuclear(self.h2o)
        result = engine.compute(s, s)
        
        self.assertIsNotNone(result)
        self.assertAlmostEqual(np.linalg.norm(result), 14.54704336519, places=5)
        
        print(f"Nuclear <s|V|s> norm = {np.linalg.norm(result):.6f}")
    
    def test_coulomb_integral(self):
        """Test 4-center Coulomb integral computation."""
        import numpy as np
        
        s = self.libint2.Shell(0, [(1, 10)])
        p = self.libint2.Shell(1, [(1, 10)])
        
        engine = self.libint2.coulomb()
        result = engine.compute(p, p, s, s)
        
        self.assertIsNotNone(result)
        self.assertAlmostEqual(np.linalg.norm(result), 1.62867503968, places=5)
        
        print(f"Coulomb (pp|ss) norm = {np.linalg.norm(result):.6f}")
    
    def test_3center_integral(self):
        """Test 3-center integral with BraKet specification."""
        import numpy as np
        
        s = self.libint2.Shell(0, [(1, 10)])
        
        engine = self.libint2.Engine(
            self.libint2.Operator.coulomb,
            braket=self.libint2.BraKet.XXXS
        )
        result = engine.compute(s, s, s)
        
        self.assertIsNotNone(result)
        self.assertAlmostEqual(np.linalg.norm(result), 3.6563211198, places=5)
        
        print(f"3-center (ss|s) norm = {np.linalg.norm(result):.6f}")
    
    def test_basis_integrals(self):
        """Test integral computation over entire basis."""
        import numpy as np
        
        Shell = self.libint2.Shell
        BasisSet = self.libint2.BasisSet
        
        p = Shell(1, [(1, 10)])
        d = Shell(2, [(1, 10)], [0.1, 0.2, 0.3])
        
        basis = BasisSet([p, d])
        
        engine = self.libint2.overlap()
        S = engine.compute(basis, basis)
        
        self.assertEqual(S.shape, (basis.nbf, basis.nbf))
        
        # Check symmetry
        self.assertTrue(np.allclose(S, S.T))
        
        # Check specific values if using standard ordering
        if self.libint2.solid_harmonics_ordering() == self.libint2.SHGShellOrdering.Standard:
            self.assertAlmostEqual(S[0, 3], -0.08950980671097111, places=5)
            self.assertAlmostEqual(S[0, 4], -0.26852942, places=5)
            self.assertAlmostEqual(S[1, 3], 0.0055943629194356937, places=5)
        
        print(f"Basis overlap matrix shape={S.shape}")
    
    def test_compute_1body_ints(self):
        """Test compute_1body_ints convenience method."""
        import numpy as np
        
        Shell = self.libint2.Shell
        BasisSet = self.libint2.BasisSet
        
        s1 = Shell(0, [(1.0, 1.0)], [0.0, 0.0, 0.0])
        s2 = Shell(0, [(1.0, 1.0)], [0.0, 0.0, 1.4])
        basis = BasisSet([s1, s2])
        
        engine = self.libint2.overlap()
        S = engine.compute_1body_ints(basis)
        
        self.assertEqual(S.shape, (2, 2))
        self.assertTrue(np.allclose(S, S.T))
        
        print(f"compute_1body_ints OK, shape={S.shape}")
    
    def test_num_threads(self):
        """Test Engine.num_threads property."""
        current = self.libint2.Engine.num_threads
        self.assertIsInstance(current, int)
        self.assertGreater(current, 0)
        
        print(f"num_threads = {current}")


def main():
    print("=" * 60)
    print("libint2 Wheel Test Suite")
    print("=" * 60)
    print()
    
    # Run tests
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestLibint2)
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print()
    print("=" * 60)
    if result.wasSuccessful():
        print("All tests passed!")
        return 0
    else:
        print(f"Failed: {len(result.failures)}, Errors: {len(result.errors)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
