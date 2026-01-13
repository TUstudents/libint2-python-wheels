# Contributing to libint2-python-wheels

Thank you for your interest in contributing!

## Ways to Contribute

### Reporting Issues

If you encounter problems with the wheels:

1. Check existing [issues](https://github.com/YOUR_USERNAME/libint2-python-wheels/issues)
2. Open a new issue with:
   - Operating system and architecture
   - Python version
   - Numpy version
   - Full error traceback

### Improving Build Scripts

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-improvement`
3. Make your changes
4. Test locally if possible
5. Submit a pull request

### Adding Platform Support

Want to add support for a new platform (e.g., Windows, ARM Linux)?

1. Open an issue to discuss the approach
2. Add the necessary workflow jobs and build scripts
3. Test thoroughly before submitting PR

## Development Setup

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/libint2-python-wheels.git
cd libint2-python-wheels

# Test the build script locally (Linux/macOS)
export PYTHON=$(which python3)
export LIBINT_VERSION=2.11.2
export INSTALL_PREFIX=/tmp/libint2-test
./scripts/build_libint2.sh
```

## Testing Locally

Before pushing changes, test locally:

```bash
# Test pyproject generation
python scripts/patch_pyproject.py --version 2.11.2 --numpy-constraint "<2.4" --output /tmp/test-pyproject.toml
cat /tmp/test-pyproject.toml

# If you have a built wheel
pip install /path/to/wheel.whl
python scripts/test_wheel.py
```

## Workflow Triggers

- **Push tag** (`v*`): Creates a release with all wheels
- **Manual dispatch**: Build with custom parameters
- **Scheduled**: Weekly builds (Sundays 2 AM UTC)

## Code Style

- Shell scripts: Follow [Google Shell Style Guide](https://google.github.io/styleguide/shellguide.html)
- Python: Follow PEP 8, use type hints where helpful
- YAML: 2-space indentation

## License

By contributing, you agree that your contributions will be licensed under the MIT License (for build infrastructure) and that the resulting wheels will be LGPL-3.0 (as they contain libint2 code).
