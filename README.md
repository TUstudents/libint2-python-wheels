# libint2-python-wheels

[![Build Wheels](https://github.com/YOUR_USERNAME/libint2-python-wheels/actions/workflows/build-wheels.yml/badge.svg)](https://github.com/YOUR_USERNAME/libint2-python-wheels/actions/workflows/build-wheels.yml)

Pre-built Python wheels for [libint2](https://github.com/evaleev/libint) - a high-performance library for computing Gaussian integrals in quantum chemistry.

## Installation

### From GitHub Releases

Download the appropriate wheel for your platform and Python version from the [Releases page](https://github.com/YOUR_USERNAME/libint2-python-wheels/releases), then install:

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

# Initialize the library
libint2.initialize()

# Use libint2 for your calculations
# ... your code here ...

# Finalize when done
libint2.finalize()
```

### Example: Computing Overlap Integrals

```python
import libint2
import numpy as np

# Initialize
libint2.initialize()

# Create a basis set
# (Example - actual API depends on libint2 Python bindings)
basis = libint2.BasisSet.build(
    atoms=[("H", [0, 0, 0]), ("H", [0, 0, 1.4])],
    basis="sto-3g"
)

# Compute overlap integrals
engine = libint2.Engine(libint2.Operator.overlap, basis.max_nprim(), basis.max_l())
# ... compute integrals ...

libint2.finalize()
```

## Numpy Compatibility

These wheels are built with a specific numpy version constraint <2.4 to be compatible with numba.

If you need a different numpy constraint, you can:

1. Build your own wheels by forking this repository
2. Modify the `NUMPY_CONSTRAINT` input when triggering a manual build

## Building Your Own Wheels

### Fork and Customize

1. Fork this repository
2. Modify `config.yml` to change build settings
3. Push a tag like `v2.11.2` to trigger a release build

### Manual Trigger

You can manually trigger a build from the Actions tab with custom parameters:

- **libint_version**: Version of libint2 to build (e.g., `2.11.2`)
- **numpy_constraint**: Numpy version constraint (e.g., `<2.4`)
- **publish_pypi**: Whether to publish to PyPI (requires secrets)

## Build Configuration

The `config.yml` file contains build settings:

```yaml
libint:
  version: "2.11.2"
  build_options:
    max_am_eri: 6        # Maximum angular momentum for ERIs
    max_am_onebody: 6    # Maximum angular momentum for 1-body integrals
    eri_deriv_order: 2   # ERI derivative order
    
python:
  versions:
    linux: ["3.9", "3.10", "3.11", "3.12", "3.13"]
    macos: ["3.10", "3.11", "3.12", "3.13"]
  numpy_constraint: "<2.4"
```

## License

This repository (build scripts and workflows) is licensed under the MIT License.

libint2 itself is licensed under the [LGPL-3.0](https://github.com/evaleev/libint/blob/master/LICENSE) license. The wheels contain libint2 code and are therefore subject to LGPL-3.0.

## Credits

- [libint2](https://github.com/evaleev/libint) by Edward Valeev and contributors
- This wheel-building infrastructure is maintained by the community

## Related Projects

- [PySCF](https://github.com/pyscf/pyscf) - Python-based Simulations of Chemistry Framework
- [Psi4](https://github.com/psi4/psi4) - Open-Source Quantum Chemistry
- [libcint](https://github.com/sunqm/libcint) - Alternative integral library

## Troubleshooting

### Import Error

If you get an import error, ensure:

1. You have the correct wheel for your platform (check `uname -m` on Unix)
2. You're using a supported Python version
3. You have numpy installed with a compatible version

### Missing Basis Sets

If basis sets aren't found, you can set the `LIBINT_DATA_PATH` environment variable:

```python
import os
os.environ["LIBINT_DATA_PATH"] = "/path/to/basis/sets"
```

### Reporting Issues

Please report issues at: https://github.com/TUstudents/libint2-python-wheels/issues

Include:
- Your operating system and architecture
- Python version (`python --version`)
- Numpy version (`python -c "import numpy; print(numpy.__version__)"`)
- Full error traceback
