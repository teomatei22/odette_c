import os
import sys
from setuptools import setup, find_packages, Extension
from setuptools.command.build_ext import build_ext
import subprocess
import shutil

# Custom build_ext command to handle the CMake build process
class CMakeExtension(Extension):
    def __init__(self, name, sourcedir=''):
        sourcedir = os.path.abspath(os.path.dirname(__file__))  # Points to the current directory
        Extension.__init__(self, name, sources=[])
        self.sourcedir = os.path.abspath(sourcedir)

class CMakeBuild(build_ext):
    def run(self):
        for ext in self.extensions:
            self.build_extension(ext)

    def build_extension(self, ext):
        # Clean previous build directory
        shutil.rmtree(self.build_temp, ignore_errors=True)
        
        # Make sure we have a build directory
        build_temp = os.path.abspath(self.build_temp)
        if not os.path.exists(build_temp):
            os.makedirs(build_temp)
        
        print(f"Building in directory: {build_temp}")
        
        # Get the absolute path to the current directory (where setup.py is)
        extdir = os.path.abspath(os.path.dirname(self.get_ext_fullpath(ext.name)))
        
        # Ensure the output directory exists
        if not os.path.exists(extdir):
            os.makedirs(extdir)
        
        # Configure and build the extension
        cmake_args = [
            f'-DCMAKE_LIBRARY_OUTPUT_DIRECTORY={extdir}',
            f'-DPYTHON_EXECUTABLE={sys.executable}',
            f'-DCMAKE_PREFIX_PATH={sys.prefix}/lib/python{sys.version_info[0]}.{sys.version_info[1]}/site-packages'
        ]

        # Handle Debug vs Release build types
        cfg = 'Debug' if self.debug else 'Release'
        build_args = ['--config', cfg]
        cmake_args += [f'-DCMAKE_BUILD_TYPE={cfg}']

        # Multi-config generators (like Visual Studio) need this
        if sys.platform.startswith('win'):
            cmake_args += ['-A', 'x64' if sys.maxsize > 2**32 else 'Win32']
            build_args += ['--', '/m']
        else:
            build_args += ['--', '-j4']

        # Print debug information
        print(f"Source directory: {ext.sourcedir}")
        print(f"Build directory: {build_temp}")
        print(f"Library output directory: {extdir}")
        
        # Run CMake configure and build
        subprocess.check_call(['cmake', ext.sourcedir] + cmake_args, cwd=build_temp)
        subprocess.check_call(['cmake', '--build', '.'] + build_args, cwd=build_temp)

# Setup configuration
setup(
    name="odette-satellite-core",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Python bindings for ODETTE satellite propagation core",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/odette",
    packages=["odette"],  # Use a specific list instead of find_packages()
    python_requires=">=3.6",
    install_requires=[
        "numpy>=1.19.0",
    ],
    ext_modules=[CMakeExtension("odette.satellite_core")],
    cmdclass={"build_ext": CMakeBuild},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
