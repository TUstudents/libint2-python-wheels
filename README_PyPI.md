# libint2-python

Python bindings for [libint2](https://github.com/evaleev/libint) - a high-performance library for computing molecular integrals.

## Installation

Install via pip:

```bash
pip install libint2
```

This installs the pre-compiled binary wheel which includes the libint2 library and standard basis sets.

## Usage

```python
import libint2
import numpy as np

# Initialize library
print(f"Using libint2 version: {libint2.LIBINT_VERSION}")
print(f"Max angular momentum: {libint2.MAX_AM}")

# Create a shell
# Shell(L, primitives, center)
s = libint2.Shell(0, [(1.0, 1.0)], [0.0, 0.0, 0.0])

# Compute overlap integrals
engine = libint2.overlap()
result = engine.compute(s, s)
print(f"Overlap: {result[0]}")

# Load a basis set
atoms = [
    libint2.Atom(8, [0.0, 0.0, 0.0]),       # O
    libint2.Atom(1, [0.0, -0.757, 0.587]),  # H
    libint2.Atom(1, [0.0, 0.757, 0.587])    # H
]
basis = libint2.BasisSet("sto-3g", atoms)
print(f"Number of basis functions: {basis.nbf}")
```

## Features

- **Pre-compiled Wheels**: Available for Linux (x86_64) and macOS (x86_64, ARM64)
- **Bundled Basis Sets**: Includes standard basis sets (STO-3G, cc-pVDZ, etc.)
- **NumPy Integration**: Returns integrals as NumPy arrays

## License

LGPL-3.0-or-later
