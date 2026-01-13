# libint2-python-wheels

[![Build libint2 Python Wheels](https://github.com/TUstudents/libint2-python-wheels/actions/workflows/build-wheels.yml/badge.svg)](https://github.com/TUstudents/libint2-python-wheels/actions/workflows/build-wheels.yml)

Pre-built Python wheels for [libint2](https://github.com/evaleev/libint) - a high-performance library for computing Gaussian integrals in quantum chemistry.

## Installation

### From GitHub Releases

Download the appropriate wheel for your platform and Python version from the [Releases page](https://github.com/TUstudents/libint2-python-wheels/releases), then install:

```bash
pip install libint2-2.11.2-cp312-cp312-manylinux_2_28_x86_64.whl
```

Or install directly from URL:

```bash
# Linux x86_64, Python 3.12
pip install "libint2 @ https://github.com/TUstudents/libint2-python-wheels/releases/download/v2.11.2/libint2-2.11.2-cp312-cp312-manylinux_2_28_x86_64.whl"

# macOS ARM64, Python 3.12
pip install "libint2 @ https://github.com/TUstudents/libint2-python-wheels/releases/download/v2.11.2/libint2-2.11.2-cp312-cp312-macosx_14_0_arm64.whl"
```

### With uv

```bash
uv add "libint2 @ https://github.com/TUstudents/libint2-python-wheels/releases/download/v2.11.2/libint2-2.11.2-cp312-cp312-manylinux_2_28_x86_64.whl"
```

## Supported Platforms

| Platform | Architecture | Python Versions |
|----------|--------------|-----------------|
| Linux (manylinux_2_28) | x86_64 | 3.9, 3.10, 3.11, 3.12, 3.13 |
| macOS 15 | x86_64 (Intel) | 3.10, 3.11, 3.12, 3.13 |
| macOS 15 | ARM64 (Apple Silicon) | 3.10, 3.11, 3.12, 3.13 |

## Usage

```python
import libint2

# Library is automatically initialized on import
print(f"Maximum angular momentum: {libint2.MAX_AM}")

# Create atoms (Z, [x, y, z])
atoms = [
    libint2.Atom(1, [0.0, 0.0, 0.0]),      # H at origin
    libint2.Atom(1, [0.0, 0.0, 1.4]),      # H at 1.4 bohr
]

# Create basis set
basis = libint2.BasisSet("sto-3g", atoms)
print(f"Number of basis functions: {basis.nbf}")

# Create integral engines
overlap_engine = libint2.overlap()
kinetic_engine = libint2.kinetic()

# Compute overlap matrix for entire basis
S = overlap_engine.compute(basis, basis)
print(f"Overlap matrix shape: {S.shape}")

# Compute kinetic energy matrix
T = kinetic_engine.compute(basis, basis)

# For nuclear attraction, set the charges first
nuclear_engine = libint2.nuclear([(1.0, [0.0, 0.0, 0.0]), (1.0, [0.0, 0.0, 1.4])])
V = nuclear_engine.compute(basis, basis)

# Compute two-electron integrals
coulomb_engine = libint2.coulomb()
# For shell quartets:
# eri = coulomb_engine.compute(shell_a, shell_b, shell_c, shell_d)
# For full basis:
# eri = coulomb_engine.compute(basis, basis, basis, basis)
```

### Shell-by-Shell Computation

```python
import libint2
import numpy as np

atoms = [libint2.Atom(1, [0.0, 0.0, 0.0]), libint2.Atom(1, [0.0, 0.0, 1.4])]
basis = libint2.BasisSet("sto-3g", atoms)

engine = libint2.overlap()

# Iterate over shell pairs
for i, shell_i in enumerate(basis):
    for j, shell_j in enumerate(basis):
        result = engine.compute(shell_i, shell_j)
        if result is not None:
            print(f"Shell ({i},{j}): {result.shape}")
```

## Numpy Compatibility

These wheels are built with numpy version constraint `<2.4` to be compatible with numba.

If you need a different numpy constraint, you can:

1. Build your own wheels by forking this repository
2. Modify the `NUMPY_CONSTRAINT` input when triggering a manual build

## Building Your Own Wheels

### Fork and Customize

1. Fork this repository
2. Trigger a manual build from the Actions tab with custom parameters:
   - **libint_version**: Version of libint2 to build (e.g., `2.11.2`)
   - **numpy_constraint**: Numpy version constraint (e.g., `<2.4`)
3. Push a tag like `v2.11.2` to create a release

## How It Works

This repository uses the official libint2 Python bindings with [scikit-build-core](https://scikit-build-core.readthedocs.io/). The workflow:

1. Downloads the libint2 source tarball
2. Uses `python -m build` with scikit-build-core to build the wheel
3. Repairs the wheel with `auditwheel` (Linux) or `delocate` (macOS)
4. Tests the wheel by importing and running basic operations

## License

This repository (build scripts and workflows) is licensed under the MIT License.

libint2 itself is licensed under [LGPL-3.0](https://github.com/evaleev/libint/blob/master/LICENSE). The wheels contain libint2 code and are subject to LGPL-3.0.

## Credits

- [libint2](https://github.com/evaleev/libint) by Edward F. Valeev and contributors
- Python bindings included in libint2

## Related Projects

- [PySCF](https://github.com/pyscf/pyscf) - Python-based Simulations of Chemistry Framework
- [Psi4](https://github.com/psi4/psi4) - Open-Source Quantum Chemistry

## Troubleshooting

### Import Error

If you get an import error, ensure:

1. You have the correct wheel for your platform (`uname -m` on Unix)
2. You're using a supported Python version
3. You have numpy installed

### Missing Basis Sets

The basis set data may not be bundled in the wheel. You can:

1. Install basis sets separately
2. Set `LIBINT_DATA_PATH` environment variable
3. Use explicit shell definitions instead of named basis sets

### Reporting Issues

Please report issues at: https://github.com/TUstudents/libint2-python-wheels/issues

Include:
- Your operating system and architecture
- Python version (`python --version`)
- Numpy version (`python -c "import numpy; print(numpy.__version__)"`)
- Full error traceback
