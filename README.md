# libint2-python-wheels

[![Build libint2 Python Wheels](https://github.com/TUstudents/libint2-python-wheels/actions/workflows/build-wheels.yml/badge.svg)](https://github.com/TUstudents/libint2-python-wheels/actions/workflows/build-wheels.yml)

Pre-built Python wheels for [libint2](https://github.com/evaleev/libint) - a high-performance library for computing Gaussian integrals in quantum chemistry.

**Automatically builds from the latest precompiled libint2 release.**

## Installation

### From GitHub Releases

Download the appropriate wheel for your platform from the [Releases page](https://github.com/TUstudents/libint2-python-wheels/releases), then:

```bash
pip install libint2-<version>-<platform>.whl
```

Or install directly from URL (replace version and platform):

```bash
# Example for Linux x86_64, Python 3.12
pip install "libint2 @ https://github.com/TUstudents/libint2-python-wheels/releases/download/v<version>/libint2-<version>-cp312-cp312-manylinux_2_28_x86_64.whl"
```

### With uv

```bash
uv add "libint2 @ https://github.com/TUstudents/libint2-python-wheels/releases/download/v<version>/libint2-<version>-cp312-cp312-manylinux_2_28_x86_64.whl"
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
import numpy as np

# Library is automatically initialized on import
print(f"Maximum angular momentum: {libint2.MAX_AM}")

# Create atoms (Z, [x, y, z] in Bohr)
h2o = [
    (8, [0.00000, -0.07579, 0.00000]),
    (1, [0.86681,  0.60144, 0.00000]),
    (1, [-0.86681, 0.60144, 0.00000]),
]

# Create basis set
basis = libint2.BasisSet("sto-3g", h2o)
print(f"Number of basis functions: {basis.nbf}")

# Compute integrals
S = libint2.overlap().compute(basis, basis)   # Overlap
T = libint2.kinetic().compute(basis, basis)   # Kinetic energy
V = libint2.nuclear(h2o).compute(basis, basis)  # Nuclear attraction

# Two-electron integrals
eri = libint2.coulomb().compute(basis, basis, basis, basis)
```

### Shell-by-Shell Computation

```python
import libint2

# Create shells directly
s = libint2.Shell(0, [(1.0, 1.0)], [0.0, 0.0, 0.0])  # s-type
p = libint2.Shell(1, [(1.0, 1.0)], [0.0, 0.0, 0.0])  # p-type

# Compute overlap between shells
engine = libint2.overlap()
result = engine.compute(s, p)
```

## Numpy Compatibility

These wheels require `numpy<2.4` for compatibility with numba.

## Building Your Own Wheels

### Automatic Builds

The workflow automatically detects and uses the latest libint2 release that has a precompiled tarball.

### Manual Trigger

Trigger a build from the Actions tab with optional parameters:
- **libint_version**: Specific version (leave empty for latest)
- **numpy_constraint**: Numpy version constraint (default: `<2.4`)

### Create a Release

Push a tag to create a GitHub release with all wheels:
```bash
git tag v2.12.0
git push --tags
```

## How It Works

1. **Detect version**: Queries GitHub API for latest release with `libint-X.Y.Z.tgz`
2. **Download**: Fetches the precompiled tarball
3. **Build**: Configures with `-DLIBINT2_PYTHON=ON` and builds Python bindings
4. **Package**: Creates wheel, adds basis sets, repairs with auditwheel/delocate
5. **Test**: Verifies import and basic integrals work

## License

This repository (build infrastructure) is MIT licensed.

libint2 itself is [LGPL-3.0](https://github.com/evaleev/libint/blob/master/LICENSE). Wheels contain libint2 code and are subject to LGPL-3.0.

## Credits

- [libint2](https://github.com/evaleev/libint) by Edward F. Valeev and contributors

## Troubleshooting

### Import Error

Ensure you have the correct wheel for your platform (`uname -m`) and Python version.

### Missing Basis Sets

Basis sets are bundled in the wheel. If not found, set `LIBINT_DATA_PATH` environment variable.

### Reporting Issues

https://github.com/TUstudents/libint2-python-wheels/issues
