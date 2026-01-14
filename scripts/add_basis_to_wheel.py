#!/usr/bin/env python3
"""
Add basis set files to a libint2 wheel.

This script unpacks a wheel, adds the basis set files from lib/basis,
and repacks the wheel.
"""

import argparse
import hashlib
import os
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path


def sha256_digest(path: Path) -> str:
    """Calculate SHA256 hash of a file."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def add_basis_to_wheel(wheel_path: Path, basis_dir: Path, output_dir: Path) -> Path:
    """Add basis set files to a wheel."""
    
    if not basis_dir.exists():
        print(f"Warning: Basis directory {basis_dir} does not exist")
        # Just copy the wheel as-is
        output_path = output_dir / wheel_path.name
        shutil.copy2(wheel_path, output_path)
        return output_path
    
    print(f"Adding basis sets from {basis_dir} to {wheel_path.name}")
    
    # Count basis files
    basis_files = list(basis_dir.rglob("*"))
    basis_file_count = sum(1 for f in basis_files if f.is_file())
    print(f"  Found {basis_file_count} basis set files")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        
        # Unpack the wheel
        unpack_dir = tmpdir / "wheel"
        with zipfile.ZipFile(wheel_path, "r") as zf:
            zf.extractall(unpack_dir)
        
        # Find the package directory (libint2)
        pkg_dir = unpack_dir / "libint2"
        if not pkg_dir.exists():
            # Try to find it
            for d in unpack_dir.iterdir():
                if d.is_dir() and not d.name.endswith(".dist-info"):
                    pkg_dir = d
                    break
        
        if not pkg_dir.exists():
            raise RuntimeError(f"Could not find package directory in wheel")
        
        # Copy basis files into the package
        basis_dest = pkg_dir / "share" / "libint" / "basis"
        basis_dest.mkdir(parents=True, exist_ok=True)
        
        for src_file in basis_dir.rglob("*"):
            if src_file.is_file():
                rel_path = src_file.relative_to(basis_dir)
                dst_file = basis_dest / rel_path
                dst_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src_file, dst_file)
        
        print(f"  Copied basis files to {basis_dest.relative_to(unpack_dir)}")
        
        # Add __init__.py to make the package importable
        # Set LIBINT_DATA_PATH so the library can find basis files at runtime
        init_path = pkg_dir / "__init__.py"
        if not init_path.exists():
            init_content = '''# Auto-generated __init__.py for libint2 package
import os as _os
from pathlib import Path as _Path

# Set LIBINT_DATA_PATH to the bundled basis files location
# This overrides the hardcoded build-time path
_pkg_dir = _Path(__file__).parent
_data_path = _pkg_dir / "share" / "libint"
if _data_path.exists():
    _os.environ.setdefault("LIBINT_DATA_PATH", str(_data_path))

# Re-export everything from the C++ extension module
from .libint2 import *
'''
            init_path.write_text(init_content)
            print(f"  Added __init__.py with LIBINT_DATA_PATH setup")
        
        # Update the RECORD file
        dist_info = None
        for d in unpack_dir.iterdir():
            if d.name.endswith(".dist-info"):
                dist_info = d
                break
        
        if dist_info:
            record_path = dist_info / "RECORD"
            record_lines = []
            
            # Read existing RECORD entries (except RECORD itself)
            if record_path.exists():
                with open(record_path, "r") as f:
                    for line in f:
                        line = line.strip()
                        if line and "RECORD" not in line:
                            record_lines.append(line)
            
            # Add new basis file entries
            for src_file in basis_dest.rglob("*"):
                if src_file.is_file():
                    rel_path = src_file.relative_to(unpack_dir)
                    digest = sha256_digest(src_file)
                    size = src_file.stat().st_size
                    record_lines.append(f"{rel_path},sha256={digest},{size}")
            
            # Add __init__.py entry if we created it
            if init_path.exists():
                rel_path = init_path.relative_to(unpack_dir)
                digest = sha256_digest(init_path)
                size = init_path.stat().st_size
                record_lines.append(f"{rel_path},sha256={digest},{size}")
            
            # Add RECORD entry (no hash)
            record_lines.append(f"{dist_info.name}/RECORD,,")
            
            # Write updated RECORD
            with open(record_path, "w") as f:
                f.write("\n".join(record_lines) + "\n")
        
        # Repack the wheel
        output_path = output_dir / wheel_path.name
        output_dir.mkdir(parents=True, exist_ok=True)
        
        with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for file_path in unpack_dir.rglob("*"):
                if file_path.is_file():
                    arcname = file_path.relative_to(unpack_dir)
                    zf.write(file_path, arcname)
        
        print(f"  Created {output_path}")
        return output_path


def main():
    parser = argparse.ArgumentParser(description="Add basis sets to libint2 wheel")
    parser.add_argument(
        "wheel",
        type=Path,
        help="Path to the wheel file",
    )
    parser.add_argument(
        "--basis-dir",
        type=Path,
        required=True,
        help="Path to the basis set directory (lib/basis)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("dist"),
        help="Output directory for modified wheel",
    )
    
    args = parser.parse_args()
    
    if not args.wheel.exists():
        print(f"Error: Wheel not found: {args.wheel}")
        return 1
    
    output = add_basis_to_wheel(args.wheel, args.basis_dir, args.output_dir)
    print(f"\nOutput wheel: {output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
