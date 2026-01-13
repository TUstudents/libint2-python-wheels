"""
libint2 - Python bindings for the Libint2 Gaussian integral library.

Libint2 is a high-performance library for computing Gaussian integrals
commonly used in quantum chemistry calculations.

Example usage:
    >>> import libint2
    >>> libint2.initialize()
    >>> # ... perform calculations ...
    >>> libint2.finalize()

For more information, see:
    https://github.com/evaleev/libint
"""

import os
import sys
from pathlib import Path

# Version is set during wheel build
__version__ = "2.11.2"

# Find and configure library paths
_package_dir = Path(__file__).parent.resolve()
_lib_dir = _package_dir / "lib"
_share_dir = _package_dir / "share"

# Set environment variables for libint2 to find its data files
if _share_dir.exists():
    os.environ.setdefault("LIBINT_DATA_PATH", str(_share_dir))

# Add library directory to path for finding shared libraries
if _lib_dir.exists():
    if sys.platform == "darwin":
        # macOS: Update DYLD_LIBRARY_PATH
        dyld_path = os.environ.get("DYLD_LIBRARY_PATH", "")
        if str(_lib_dir) not in dyld_path:
            os.environ["DYLD_LIBRARY_PATH"] = f"{_lib_dir}:{dyld_path}" if dyld_path else str(_lib_dir)
    else:
        # Linux: Update LD_LIBRARY_PATH
        ld_path = os.environ.get("LD_LIBRARY_PATH", "")
        if str(_lib_dir) not in ld_path:
            os.environ["LD_LIBRARY_PATH"] = f"{_lib_dir}:{ld_path}" if ld_path else str(_lib_dir)

# Import the compiled extension module
# The actual module name depends on how libint2 was built
try:
    from . import _libint2 as _core
except ImportError:
    try:
        # Alternative import path
        from .lib import libint2 as _core
    except ImportError:
        # Try to find the module dynamically
        _found = False
        for _ext_suffix in [".so", ".pyd", ".dylib"]:
            for _candidate in _package_dir.rglob(f"*libint2*{_ext_suffix}"):
                try:
                    import importlib.util
                    spec = importlib.util.spec_from_file_location("_core", _candidate)
                    _core = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(_core)
                    _found = True
                    break
                except Exception:
                    continue
            if _found:
                break
        
        if not _found:
            raise ImportError(
                "Could not import libint2 extension module. "
                "This may indicate a missing dependency or an incompatible platform. "
                f"Package directory: {_package_dir}"
            )

# Re-export commonly used functions and classes from the core module
def initialize():
    """Initialize the libint2 library. Must be called before using any other functions."""
    return _core.initialize()

def finalize():
    """Finalize the libint2 library. Should be called when done with calculations."""
    return _core.finalize()

def initialized():
    """Check if libint2 has been initialized."""
    return _core.initialized()

# Export additional symbols from core module
def __getattr__(name):
    """Forward attribute access to the core module."""
    return getattr(_core, name)

def __dir__():
    """List available attributes."""
    core_attrs = dir(_core) if "_core" in globals() else []
    return sorted(set([
        "__version__",
        "initialize",
        "finalize", 
        "initialized",
    ] + core_attrs))
