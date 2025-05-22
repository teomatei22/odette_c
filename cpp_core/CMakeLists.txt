cmake_minimum_required(VERSION 3.20)
project(orbit_determination)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
set(CMAKE_CXX_STANDARD 23)
set(CMAKE_C_STANDARD 23)

include_directories(include)
include_directories(Eigen)

link_directories(lib)
link_libraries(libraylib.a)
link_libraries(libraylibdll.a)

add_executable(gauss_tle_tests gauss_tle_test.cpp
        src/TLE.cpp
        src/SGP4.cpp
        include/interpret.h
        include/orbmath.h
        include/propagator.h
        src/interpret.cpp
        src/RADec.cpp
        include/TDMParser.h
        src/TDMParser.cpp
        src/RADec.cpp
        src/orbmath.cpp
        include/orbmath_nutation.h
        include/logging.h
        include/orbmath_perturbation.h
        include/iers_coef.h
        include/atmosphere.h
        include/lunar_position.h
        include/solar_position.h
        src/propagator.cpp
        include/json.h
        include/json_fwd.h
        include/frame.h
        include/popl.h
)


add_executable(orbit_determination main.cpp
        src/TLE.cpp
        src/SGP4.cpp
        include/interpret.h
        include/orbmath.h
        include/propagator.h
        src/interpret.cpp
        src/RADec.cpp
        include/TDMParser.h
        src/TDMParser.cpp
        src/RADec.cpp
        src/orbmath.cpp
        include/orbmath_nutation.h
        include/logging.h
        include/orbmath_perturbation.h
        include/iers_coef.h
        src/propagator.cpp
        include/json.h
        include/json_fwd.h
        include/popl.h
)

target_link_libraries(gauss_tle_tests raylib winmm gdi32 opengl32)