#!/bin/bash
# Build libint2 with Python bindings
# 
# Environment variables:
#   PYTHON          - Python executable path
#   LIBINT_VERSION  - libint2 version to build
#   INSTALL_PREFIX  - Installation prefix
#   NPROC           - Number of parallel jobs (default: nproc)

set -euo pipefail

# Configuration
PYTHON="${PYTHON:-python3}"
LIBINT_VERSION="${LIBINT_VERSION:-2.11.2}"
INSTALL_PREFIX="${INSTALL_PREFIX:-/tmp/libint2-install}"
NPROC="${NPROC:-$(nproc 2>/dev/null || sysctl -n hw.ncpu 2>/dev/null || echo 4)}"

# Build directory
BUILD_DIR="/tmp/libint2-build"
DOWNLOAD_URL="https://github.com/evaleev/libint/releases/download/v${LIBINT_VERSION}/libint-${LIBINT_VERSION}.tgz"

echo "=============================================="
echo "Building libint2 ${LIBINT_VERSION}"
echo "=============================================="
echo "Python: ${PYTHON}"
echo "Install prefix: ${INSTALL_PREFIX}"
echo "Parallel jobs: ${NPROC}"
echo ""

# Get Python include and library paths
PYTHON_INCLUDE=$("${PYTHON}" -c "import sysconfig; print(sysconfig.get_path('include'))")
PYTHON_LIBRARY=$("${PYTHON}" -c "import sysconfig; print(sysconfig.get_config_var('LIBDIR'))")
PYTHON_VERSION=$("${PYTHON}" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")

echo "Python include: ${PYTHON_INCLUDE}"
echo "Python library: ${PYTHON_LIBRARY}"
echo "Python version: ${PYTHON_VERSION}"
echo ""

# Install Python dependencies
echo "Installing Python dependencies..."
"${PYTHON}" -m pip install --quiet pybind11 numpy

# Get pybind11 CMake directory
PYBIND11_CMAKE=$("${PYTHON}" -c "import pybind11; print(pybind11.get_cmake_dir())")
echo "pybind11 CMake dir: ${PYBIND11_CMAKE}"
echo ""

# Create build directory
rm -rf "${BUILD_DIR}"
mkdir -p "${BUILD_DIR}"
cd "${BUILD_DIR}"

# Download libint2 source
echo "Downloading libint2 ${LIBINT_VERSION}..."
if command -v wget &>/dev/null; then
    wget -q "${DOWNLOAD_URL}" -O libint.tgz
elif command -v curl &>/dev/null; then
    curl -sL "${DOWNLOAD_URL}" -o libint.tgz
else
    echo "Error: Neither wget nor curl found"
    exit 1
fi

# Extract
echo "Extracting..."
tar xzf libint.tgz
cd libint-${LIBINT_VERSION}

# Create build directory
mkdir -p build
cd build

# Configure with CMake
echo "Configuring with CMake..."
cmake .. \
    -DCMAKE_INSTALL_PREFIX="${INSTALL_PREFIX}" \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_POSITION_INDEPENDENT_CODE=ON \
    -DENABLE_FORTRAN=OFF \
    -DLIBINT2_ENABLE_PYTHON=ON \
    -Dpybind11_DIR="${PYBIND11_CMAKE}" \
    -DPython_EXECUTABLE="${PYTHON}" \
    -DPython_INCLUDE_DIRS="${PYTHON_INCLUDE}" \
    -DENABLE_XHOST=OFF \
    -DBUILD_SHARED_LIBS=ON \
    -DLIBINT2_BUILD_SHARED_AND_STATIC_LIBS=OFF

# Build
echo "Building with ${NPROC} parallel jobs..."
cmake --build . --parallel "${NPROC}"

# Install
echo "Installing to ${INSTALL_PREFIX}..."
cmake --install .

# Copy basis sets
echo "Copying basis sets..."
LIBINT_BASIS_DIR="${INSTALL_PREFIX}/share/libint/${LIBINT_VERSION}/basis"
mkdir -p "${LIBINT_BASIS_DIR}"
if [ -d "../lib/basis" ]; then
    cp -r ../lib/basis/* "${LIBINT_BASIS_DIR}/" 2>/dev/null || true
fi

# Verify installation
echo ""
echo "=============================================="
echo "Installation complete!"
echo "=============================================="
echo ""
echo "Installed files:"
ls -la "${INSTALL_PREFIX}/"

if [ -d "${INSTALL_PREFIX}/lib" ]; then
    echo ""
    echo "Libraries:"
    ls -la "${INSTALL_PREFIX}/lib/"
fi

if [ -d "${INSTALL_PREFIX}/lib/python${PYTHON_VERSION}" ]; then
    echo ""
    echo "Python bindings:"
    find "${INSTALL_PREFIX}/lib/python${PYTHON_VERSION}" -name "*.so" -o -name "*.dylib" 2>/dev/null || true
fi

# Test import
echo ""
echo "Testing Python import..."
export PYTHONPATH="${INSTALL_PREFIX}/lib/python${PYTHON_VERSION}/site-packages:${PYTHONPATH:-}"
"${PYTHON}" -c "import libint2; print(f'libint2 imported successfully')" && echo "SUCCESS!" || echo "FAILED - will fix during wheel packaging"

echo ""
echo "Build completed successfully!"
