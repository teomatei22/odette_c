# Windows Build Guide for Satellite Core Module

This document provides step-by-step instructions for building and installing the satellite_core module on Windows using pybind11.

## Prerequisites

### 1. Install Python (3.8 or later)
- Download from [python.org](https://python.org)
- **Important**: Check "Add Python to PATH" during installation
- Verify installation by opening Command Prompt and typing: `python --version`

### 2. Install Microsoft Visual C++ Build Tools
- Download "Microsoft C++ Build Tools" from [Microsoft's website](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
- **Alternative**: Install Visual Studio Community Edition
- During installation, select:
  - "C++ build tools"
  - "Windows 10/11 SDK"
  - "CMake tools for C++"

### 3. Install Required Python Packages
Open Command Prompt and run:
```bash
pip install pybind11
pip install setuptools
pip install wheel
```

## Build Instructions

### Step 1: Navigate to the Project Directory
Open Command Prompt and navigate to whichever folder contains `setup.py`:

```bash
# Either navigate to cpp_core folder:
cd path/to/ODETTE/cpp_core

# Or navigate to Python_interface folder:
cd path/to/ODETTE/Python_interface
```

### Step 2: Build the Extension Module
Run the following command to build the extension in-place:

```bash
python setup.py build_ext --inplace
```

This command will:
- Compile the C++ code using pybind11
- Create the Python extension module (`.pyd` file on Windows)
- Place the compiled module directly in the source directory

### Step 3: Verify the Build
After successful compilation, you should see a new file in the directory such as:
- `satellite_core.cp39-win_amd64.pyd` (filename varies based on Python version and architecture)

### Step 4: Test the Module
Test that the module loads correctly:

```bash
python -c "import satellite_core; print('Module loaded successfully!')"
```

## Alternative Installation Methods

### System-wide Installation
If you want to install the module system-wide after building:

```bash
# First build in-place
python setup.py build_ext --inplace

# Then install system-wide
python setup.py install
```

### Using pip for Installation
```bash
pip install .
```

## Troubleshooting Common Issues

### 1. "Microsoft Visual C++ 14.0 is required" Error
**Solution**: Install Visual Studio Build Tools as mentioned in prerequisites, then restart Command Prompt and try again.

### 2. "Python.h not found" Error
**Solution**: Ensure Python development headers are available:
```bash
pip install --upgrade setuptools
```

### 3. CMake Issues (if your setup.py uses CMake)
**Solution**: 
- Install CMake from [cmake.org](https://cmake.org/download/)
- Select "Add CMake to PATH" during installation
- Restart Command Prompt

### 4. Permission Errors
**Solution**: Either run Command Prompt as Administrator, or use the `--user` flag:
```bash
python setup.py build_ext --inplace --user
```

### 5. Path Issues
**Solution**: Ensure all paths in your `setup.py` use forward slashes `/` or raw strings, as Windows path separators can cause issues.

### 6. "error: command 'cl.exe' failed"
**Solution**: Make sure Visual Studio Build Tools are properly installed and try running from "Developer Command Prompt for VS" instead of regular Command Prompt.

## Final Verification Steps

1. Ensure the `.pyd` file is created in your project directory
2. Test importing the module in Python
3. Verify all functions work as expected
4. Test integration with your Java GUI application

## Important Notes

- The `.pyd` file is the compiled extension that enables Python-Java interaction
- Keep the `.pyd` file in the same directory as your Python scripts
- The working directory must contain the `.pyd` file when running Python scripts that import the module
- Test the module thoroughly before integrating it into the Java GUI

## Getting Help

If you encounter issues not covered in this guide:
1. Check that all prerequisites are properly installed
2. Verify Python and pip are working correctly
3. Ensure Visual Studio Build Tools are complete
4. Try building in a fresh Command Prompt session

For specific error messages, search for the exact error text online or consult the pybind11 documentation.
