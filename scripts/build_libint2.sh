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

# Get Python info
PYTHON_VERSION=$("${PYTHON}" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
PYTHON_IMPL=$("${PYTHON}" -c "import sys; print(sys.implementation.name)")
PYTHON_SOABI=$("${PYTHON}" -c "import sysconfig; print(sysconfig.get_config_var('SOABI') or '')")

echo "Python version: ${PYTHON_VERSION}"
echo "Python implementation: ${PYTHON_IMPL}"
echo "Python SOABI: ${PYTHON_SOABI}"
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
    -DENABLE_XHOST=OFF \
    -DBUILD_SHARED_LIBS=ON \
    -DLIBINT2_BUILD_SHARED_AND_STATIC_LIBS=OFF

# Build
echo "Building with ${NPROC} parallel jobs..."
cmake --build . --parallel "${NPROC}"

# Install
echo "Installing to ${INSTALL_PREFIX}..."
cmake --install .

# Find the Python extension module
echo ""
echo "=============================================="
echo "Locating Python extension module..."
echo "=============================================="

# The Python module is typically installed to lib/pythonX.Y/site-packages/
SITE_PACKAGES="${INSTALL_PREFIX}/lib/python${PYTHON_VERSION}/site-packages"
PYTHON_MODULE_DIR="${INSTALL_PREFIX}/python_module"
mkdir -p "${PYTHON_MODULE_DIR}"

# Find the .so file (could be libint2.cpython-XXX.so or similar)
echo "Searching for Python extension..."
find "${INSTALL_PREFIX}" -name "*.so" -type f 2>/dev/null | while read -r so_file; do
    echo "  Found: ${so_file}"
done

# Copy the Python extension to our module directory
if [ -d "${SITE_PACKAGES}" ]; then
    echo "Copying from site-packages..."
    cp -r "${SITE_PACKAGES}"/* "${PYTHON_MODULE_DIR}/" 2>/dev/null || true
fi

# Also check lib directory directly
find "${INSTALL_PREFIX}/lib" -maxdepth 1 -name "*libint2*.so" -type f 2>/dev/null | while read -r so_file; do
    cp "${so_file}" "${PYTHON_MODULE_DIR}/" 2>/dev/null || true
done

# Look for the pybind11 module specifically
find "${INSTALL_PREFIX}" -name "*libint2*${PYTHON_SOABI}*.so" -type f 2>/dev/null | head -1 | while read -r so_file; do
    if [ -n "${so_file}" ]; then
        echo "Found pybind11 module: ${so_file}"
        cp "${so_file}" "${PYTHON_MODULE_DIR}/"
    fi
done

# Copy basis sets
echo ""
echo "Copying basis sets..."
LIBINT_BASIS_DIR="${PYTHON_MODULE_DIR}/share/libint/${LIBINT_VERSION}/basis"
mkdir -p "${LIBINT_BASIS_DIR}"
if [ -d "../lib/basis" ]; then
    cp -r ../lib/basis/* "${LIBINT_BASIS_DIR}/" 2>/dev/null || true
fi

# Also copy from installed share directory
if [ -d "${INSTALL_PREFIX}/share/libint" ]; then
    cp -r "${INSTALL_PREFIX}/share/libint"/* "${PYTHON_MODULE_DIR}/share/libint/" 2>/dev/null || true
fi

# Copy the core library (.so) that the Python module links against
echo ""
echo "Copying shared libraries..."
mkdir -p "${PYTHON_MODULE_DIR}/lib"
find "${INSTALL_PREFIX}/lib" -maxdepth 1 -name "libint2*.so*" -type f 2>/dev/null | while read -r lib; do
    echo "  Copying: ${lib}"
    cp -P "${lib}" "${PYTHON_MODULE_DIR}/lib/" 2>/dev/null || true
done

# Also handle symlinks
find "${INSTALL_PREFIX}/lib" -maxdepth 1 -name "libint2*.so*" -type l 2>/dev/null | while read -r lib; do
    echo "  Copying symlink: ${lib}"
    cp -P "${lib}" "${PYTHON_MODULE_DIR}/lib/" 2>/dev/null || true
done

# Verify installation
echo ""
echo "=============================================="
echo "Installation complete!"
echo "=============================================="
echo ""
echo "Python module directory contents:"
find "${PYTHON_MODULE_DIR}" -type f | head -30

echo ""
echo "Looking for .so files:"
find "${PYTHON_MODULE_DIR}" -name "*.so*" -type f

# Save the module location for the wheel build step
echo "${PYTHON_MODULE_DIR}" > "${INSTALL_PREFIX}/python_module_path.txt"

echo ""
echo "Build completed successfully!"
echo "Python module directory: ${PYTHON_MODULE_DIR}"
