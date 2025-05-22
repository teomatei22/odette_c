cmake_minimum_required(VERSION 3.12)
set(Python_EXECUTABLE "/opt/anaconda3/bin/python" CACHE FILEPATH "Python interpreter" FORCE)
project(ODETTE_satellite_core)

# Set C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

# Find Python and pybind11
find_package(Python COMPONENTS Interpreter Development REQUIRED)
find_package(Eigen3 REQUIRED)

# Add pybind11 - support both system pybind11 or submodule
if(NOT TARGET pybind11::module)
    find_package(pybind11 REQUIRED)
endif()

# Define the path to the C++ core directory
set(CPP_CORE_DIR "${CMAKE_CURRENT_SOURCE_DIR}/../../cpp_core" CACHE PATH "Path to C++ core directory")

# Set include directories
include_directories(
    ${CPP_CORE_DIR}/include
    ${EIGEN3_INCLUDE_DIR}
)

# Log paths for debugging
message(STATUS "CMAKE_CURRENT_SOURCE_DIR: ${CMAKE_CURRENT_SOURCE_DIR}")
message(STATUS "CPP_CORE_DIR: ${CPP_CORE_DIR}")

# Collect all source files from the C++ core
file(GLOB CORE_SOURCES 
    "${CPP_CORE_DIR}/src/*.cpp"
)

# Python module - combine core sources with the bindings
pybind11_add_module(satellite_core
    "${CMAKE_CURRENT_SOURCE_DIR}/satellite_core_bindings.cpp"
    ${CORE_SOURCES}
)

# Set proper install location for the Python module
install(TARGETS satellite_core
        LIBRARY DESTINATION ${Python_SITEARCH}/odette)