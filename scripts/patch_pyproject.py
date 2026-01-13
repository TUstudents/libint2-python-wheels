#!/usr/bin/env python3
"""
Patch libint2's pyproject.toml template to:
1. Replace @LIBINT_VERSION@ placeholder
2. Add numpy dependency with constraint
"""

import argparse
import re
import sys
from pathlib import Path


def patch_pyproject(input_path: Path, output_path: Path, version: str, numpy_constraint: str):
    """Patch pyproject.toml with version and numpy dependency."""
    
    content = input_path.read_text()
    
    # Replace version placeholder
    content = content.replace("@LIBINT_VERSION@", version)
    
    # Add numpy dependency if not present
    if "numpy" not in content:
        # Find the classifiers section end and add dependencies after project section
        # Look for requires-python line and add dependencies after it
        if "requires-python" in content:
            # Add dependencies section after requires-python
            content = re.sub(
                r'(requires-python\s*=\s*"[^"]*")',
                f'\\1\ndependencies = [\n    "numpy{numpy_constraint}",\n]',
                content
            )
        else:
            # Fallback: add before classifiers
            content = re.sub(
                r'(\nclassifiers\s*=)',
                f'\ndependencies = [\n    "numpy{numpy_constraint}",\n]\n\\1',
                content
            )
    else:
        # numpy already present, update constraint if needed
        content = re.sub(
            r'"numpy[^"]*"',
            f'"numpy{numpy_constraint}"',
            content
        )
    
    # Write output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content)
    
    print(f"Patched {input_path} -> {output_path}")
    print(f"  Version: {version}")
    print(f"  Numpy: numpy{numpy_constraint}")


def main():
    parser = argparse.ArgumentParser(description="Patch libint2 pyproject.toml")
    parser.add_argument("input", type=Path, help="Input pyproject.toml path")
    parser.add_argument("--output", type=Path, help="Output path (default: overwrite input)")
    parser.add_argument("--version", required=True, help="libint2 version")
    parser.add_argument("--numpy-constraint", default="<2.4", help="Numpy version constraint")
    
    args = parser.parse_args()
    
    output = args.output or args.input
    patch_pyproject(args.input, output, args.version, args.numpy_constraint)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
