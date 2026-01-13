#!/usr/bin/env python3
"""
Build a wheel from the installed libint2 files.

This script creates a proper platform wheel by:
1. Finding the compiled extension module
2. Bundling shared libraries
3. Creating proper wheel metadata
"""

import argparse
import hashlib
import os
import re
import shutil
import subprocess
import sys
import sysconfig
from pathlib import Path
from email.message import Message


def get_wheel_tag():
    """Get the wheel tag for the current platform."""
    # Python tag: cp39, cp310, etc.
    impl = sys.implementation.name[:2]  # 'cp' for cpython
    version = f"{sys.version_info.major}{sys.version_info.minor}"
    python_tag = f"{impl}{version}"
    
    # ABI tag
    soabi = sysconfig.get_config_var('SOABI')
    if soabi:
        # e.g., cpython-312-x86_64-linux-gnu -> cp312
        abi_tag = python_tag
    else:
        abi_tag = "none"
    
    # Platform tag
    if sys.platform == "linux":
        # Will be fixed by auditwheel later
        platform_tag = "linux_x86_64"
    elif sys.platform == "darwin":
        import platform
        machine = platform.machine()
        if machine == "arm64":
            platform_tag = "macosx_14_0_arm64"
        else:
            platform_tag = "macosx_13_0_x86_64"
    else:
        platform_tag = sysconfig.get_platform().replace("-", "_").replace(".", "_")
    
    return python_tag, abi_tag, platform_tag


def find_extension_module(install_prefix: Path) -> Path | None:
    """Find the libint2 Python extension module (.so file)."""
    soabi = sysconfig.get_config_var('SOABI') or ""
    
    # Patterns to search for
    patterns = [
        f"*libint2*{soabi}*.so",
        "*libint2*.cpython*.so",
        "libint2*.so",
    ]
    
    # Search locations
    search_dirs = [
        install_prefix / "lib",
        install_prefix / f"lib/python{sys.version_info.major}.{sys.version_info.minor}/site-packages",
        install_prefix / "python_module",
        install_prefix,
    ]
    
    for search_dir in search_dirs:
        if not search_dir.exists():
            continue
        for pattern in patterns:
            matches = list(search_dir.rglob(pattern))
            for match in matches:
                # Skip the C++ library itself (libint2.so.X.Y.Z)
                if re.match(r"libint2\.so\.\d+", match.name):
                    continue
                # Skip symlinks to versioned libraries
                if match.is_symlink():
                    continue
                # Found a Python extension
                print(f"Found extension module: {match}")
                return match
    
    return None


def find_shared_libraries(install_prefix: Path) -> list[Path]:
    """Find libint2 shared libraries."""
    libs = []
    lib_dir = install_prefix / "lib"
    
    if lib_dir.exists():
        for lib in lib_dir.glob("libint2*.so*"):
            if lib.is_file() and not lib.is_symlink():
                libs.append(lib)
        # Also include symlinks for proper linking
        for lib in lib_dir.glob("libint2*.so*"):
            if lib.is_symlink():
                libs.append(lib)
    
    return libs


def sha256_digest(path: Path) -> str:
    """Calculate SHA256 hash of a file."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def build_wheel(
    install_prefix: Path,
    output_dir: Path,
    version: str,
    numpy_constraint: str,
) -> Path:
    """Build a wheel from the installed files."""
    
    python_tag, abi_tag, platform_tag = get_wheel_tag()
    wheel_name = f"libint2-{version}-{python_tag}-{abi_tag}-{platform_tag}"
    
    print(f"Building wheel: {wheel_name}")
    print(f"  Python tag: {python_tag}")
    print(f"  ABI tag: {abi_tag}")
    print(f"  Platform tag: {platform_tag}")
    
    # Create wheel directory structure
    wheel_dir = output_dir / "wheel_build"
    if wheel_dir.exists():
        shutil.rmtree(wheel_dir)
    wheel_dir.mkdir(parents=True)
    
    pkg_dir = wheel_dir / "libint2"
    pkg_dir.mkdir()
    
    # Find extension module
    ext_module = find_extension_module(install_prefix)
    if ext_module is None:
        print("ERROR: Could not find libint2 Python extension module!")
        print("Searching in:", install_prefix)
        print("Contents:")
        for p in install_prefix.rglob("*"):
            if p.is_file():
                print(f"  {p}")
        sys.exit(1)
    
    # Copy extension module with correct name
    # The extension should be named libint2.cpython-XXX.so for proper import
    soabi = sysconfig.get_config_var('SOABI')
    if soabi:
        ext_name = f"_libint2.{soabi}.so"
    else:
        ext_name = "_libint2.so"
    
    print(f"Copying extension as: {ext_name}")
    shutil.copy2(ext_module, pkg_dir / ext_name)
    
    # Copy shared libraries
    libs_dir = pkg_dir / ".libs"
    libs_dir.mkdir()
    
    for lib in find_shared_libraries(install_prefix):
        print(f"Copying library: {lib.name}")
        if lib.is_symlink():
            # Recreate symlink
            link_target = os.readlink(lib)
            (libs_dir / lib.name).symlink_to(link_target)
        else:
            shutil.copy2(lib, libs_dir / lib.name)
    
    # Copy basis sets
    basis_src = install_prefix / "share" / "libint"
    if basis_src.exists():
        basis_dst = pkg_dir / "share" / "libint"
        print(f"Copying basis sets from {basis_src}")
        shutil.copytree(basis_src, basis_dst)
    
    # Create __init__.py
    init_content = f'''"""
libint2 - Python bindings for the Libint2 Gaussian integral library.
"""

__version__ = "{version}"

import os
import sys
from pathlib import Path

# Set up library path for the bundled shared libraries
_pkg_dir = Path(__file__).parent.resolve()
_libs_dir = _pkg_dir / ".libs"

if _libs_dir.exists():
    if sys.platform == "darwin":
        _env_var = "DYLD_LIBRARY_PATH"
    else:
        _env_var = "LD_LIBRARY_PATH"
    
    _current = os.environ.get(_env_var, "")
    if str(_libs_dir) not in _current:
        os.environ[_env_var] = f"{{_libs_dir}}:{{_current}}" if _current else str(_libs_dir)

# Set basis set path
_share_dir = _pkg_dir / "share" / "libint"
if _share_dir.exists():
    os.environ.setdefault("LIBINT_DATA_PATH", str(_share_dir))

# Import the extension module
from ._libint2 import *
'''
    
    (pkg_dir / "__init__.py").write_text(init_content)
    
    # Create METADATA
    metadata = f'''Metadata-Version: 2.1
Name: libint2
Version: {version}
Summary: Python bindings for Libint2 Gaussian integral library
Home-page: https://github.com/evaleev/libint
License: LGPL-3.0-or-later
Classifier: Development Status :: 5 - Production/Stable
Classifier: Intended Audience :: Science/Research
Classifier: License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)
Classifier: Operating System :: MacOS :: MacOS X
Classifier: Operating System :: POSIX :: Linux
Classifier: Programming Language :: C++
Classifier: Programming Language :: Python :: 3
Classifier: Topic :: Scientific/Engineering :: Chemistry
Requires-Python: >=3.9
Requires-Dist: numpy{numpy_constraint}
'''
    
    # Create dist-info directory
    dist_info = wheel_dir / f"libint2-{version}.dist-info"
    dist_info.mkdir()
    
    (dist_info / "METADATA").write_text(metadata)
    
    # Create WHEEL file
    wheel_content = f'''Wheel-Version: 1.0
Generator: libint2-python-wheels
Root-Is-Purelib: false
Tag: {python_tag}-{abi_tag}-{platform_tag}
'''
    (dist_info / "WHEEL").write_text(wheel_content)
    
    # Create top_level.txt
    (dist_info / "top_level.txt").write_text("libint2\n")
    
    # Create RECORD
    record_lines = []
    for path in wheel_dir.rglob("*"):
        if path.is_file():
            rel_path = path.relative_to(wheel_dir)
            if "RECORD" in str(rel_path):
                record_lines.append(f"{rel_path},,")
            else:
                digest = sha256_digest(path)
                size = path.stat().st_size
                record_lines.append(f"{rel_path},sha256={digest},{size}")
    
    (dist_info / "RECORD").write_text("\n".join(record_lines) + "\n")
    
    # Create the wheel file
    output_dir.mkdir(parents=True, exist_ok=True)
    wheel_path = output_dir / f"{wheel_name}.whl"
    
    # Use zipfile to create the wheel
    import zipfile
    with zipfile.ZipFile(wheel_path, "w", zipfile.ZIP_DEFLATED) as whl:
        for path in wheel_dir.rglob("*"):
            if path.is_file():
                whl.write(path, path.relative_to(wheel_dir))
            elif path.is_symlink():
                # Handle symlinks
                info = zipfile.ZipInfo(str(path.relative_to(wheel_dir)))
                info.create_system = 3  # Unix
                info.external_attr = (0o120777 << 16)  # symlink
                whl.writestr(info, os.readlink(path))
    
    print(f"Created wheel: {wheel_path}")
    return wheel_path


def main():
    parser = argparse.ArgumentParser(description="Build libint2 wheel")
    parser.add_argument(
        "--install-prefix",
        type=Path,
        required=True,
        help="Path to libint2 installation",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("dist"),
        help="Output directory for wheel",
    )
    parser.add_argument(
        "--version",
        required=True,
        help="Package version",
    )
    parser.add_argument(
        "--numpy-constraint",
        default="<2.4",
        help="Numpy version constraint",
    )
    
    args = parser.parse_args()
    
    wheel_path = build_wheel(
        args.install_prefix,
        args.output_dir,
        args.version,
        args.numpy_constraint,
    )
    
    print(f"\nWheel built successfully: {wheel_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
