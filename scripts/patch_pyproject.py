#!/usr/bin/env python3
"""
Generate pyproject.toml for libint2 wheel packaging.

This script creates a pyproject.toml file with the correct version
and dependency constraints for building libint2 wheels.
"""

import argparse
import sys
from pathlib import Path


PYPROJECT_TEMPLATE = '''[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "libint2"
version = "{version}"
description = "Python bindings for Libint2 Gaussian integral library"
readme = "README.md"
license = {{text = "LGPL-3.0-or-later"}}
authors = [
    {{name = "Edward Valeev", email = "evaleev@vt.edu"}},
]
maintainers = [
    {{name = "libint2-python-wheels contributors"}},
]
keywords = [
    "quantum chemistry",
    "integrals",
    "gaussian",
    "molecular",
    "computational chemistry",
]
classifiers = [
    "Development Status :: 5 - Production/Stable",
    "Intended Audience :: Science/Research",
    "License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)",
    "Operating System :: MacOS :: MacOS X",
    "Operating System :: POSIX :: Linux",
    "Programming Language :: C++",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3.13",
    "Topic :: Scientific/Engineering :: Chemistry",
    "Topic :: Scientific/Engineering :: Physics",
]
requires-python = ">=3.9"
dependencies = [
    "numpy{numpy_constraint}",
]

[project.urls]
Homepage = "https://github.com/evaleev/libint"
Documentation = "https://github.com/evaleev/libint/wiki"
Repository = "https://github.com/evaleev/libint"
Issues = "https://github.com/evaleev/libint/issues"

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "pytest-cov",
]

[tool.setuptools]
packages = ["libint2"]
include-package-data = true

[tool.setuptools.package-data]
libint2 = [
    "*.so",
    "*.dylib",
    "*.pyd",
    "lib/*",
    "lib/**/*",
    "include/*",
    "include/**/*",
    "share/*",
    "share/**/*",
]
'''


def main():
    parser = argparse.ArgumentParser(
        description="Generate pyproject.toml for libint2 wheel"
    )
    parser.add_argument(
        "--version",
        required=True,
        help="libint2 version (e.g., 2.11.2)",
    )
    parser.add_argument(
        "--numpy-constraint",
        default="<2.4",
        help="Numpy version constraint (e.g., '<2.4', '>=1.20,<2.0')",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("pyproject.toml"),
        help="Output path for pyproject.toml",
    )
    
    args = parser.parse_args()
    
    # Generate pyproject.toml content
    content = PYPROJECT_TEMPLATE.format(
        version=args.version,
        numpy_constraint=args.numpy_constraint,
    )
    
    # Write output
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(content)
    
    print(f"Generated {args.output}")
    print(f"  Version: {args.version}")
    print(f"  Numpy constraint: {args.numpy_constraint}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
