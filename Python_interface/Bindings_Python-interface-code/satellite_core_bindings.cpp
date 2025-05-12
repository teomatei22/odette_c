// bindings/satellite_core_bindings.cpp

#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <pybind11/stl.h>
#include <pybind11/eigen.h>
#include <pybind11/functional.h>

// Include necessary headers
#include "../../cpp_core/include/TLE.h"
#include "../../cpp_core/include/SGP4.h"
#include "../../cpp_core/include/propagator.h"
#include "../../cpp_core/include/frame.h"
#include "../../cpp_core/include/iers_coef.h"
#include "../../cpp_core/include/interpret.h"
#include <memory>
#include "../../cpp_core/include/TDMParser.h"
#include "../../cpp_core/include/orbmath.h"
#include "../../cpp_core/include/orbmath_nutation.h"
#include "../../cpp_core/include/orbmath_perturbation.h"
#include "../../cpp_core/include/atmosphere.h"
#include "../../cpp_core/include/lunar_position.h"
#include "../../cpp_core/include/solar_position.h"

namespace py = pybind11;
using namespace interpret;

void parseLinesWrapper(TLE &tle, const std::string &line1, const std::string &line2) {
    parseLines(&tle, const_cast<char*>(line1.c_str()), const_cast<char*>(line2.c_str()));
}

PYBIND11_MODULE(satellite_core, m) {
    m.doc() = "ODETTE Project - Satellite Tracking Core Library";
    
    // TLE and SGP4 bindings
    py::class_<TLE>(m, "TLE")
        .def(py::init<>())
        .def_readwrite("objectNum", &TLE::objectNum)
        .def_readwrite("epoch", &TLE::epoch)
        .def_readwrite("ndot", &TLE::ndot)
        .def_readwrite("nddot", &TLE::nddot)
        .def_readwrite("bstar", &TLE::bstar)
        .def_readwrite("incDeg", &TLE::incDeg)
        .def_readwrite("raanDeg", &TLE::raanDeg)
        .def_readwrite("ecc", &TLE::ecc)
        .def_readwrite("argpDeg", &TLE::argpDeg)
        .def_readwrite("maDeg", &TLE::maDeg)
        .def_readwrite("n", &TLE::n)
        .def_readwrite("revnum", &TLE::revnum)
        ;
    
    // Expose TLE parsing functions
    m.def("parse_tle_lines", &parseLinesWrapper, "Parse TLE from two lines",
          py::arg("tle"), py::arg("line1"), py::arg("line2"));
    
    m.def("get_rv", &getRV, "Get position/velocity vectors for minutes after epoch",
          py::arg("tle"), py::arg("minutes_after_epoch"), py::arg("r"), py::arg("v"));
    
    m.def("get_rv_for_date", &getRVForDate, "Get position/velocity for specific date (milliseconds since 1970)",
          py::arg("tle"), py::arg("milliseconds_since_1970"), py::arg("r"), py::arg("v"));
    
    // Propagator module
    py::module_ prop = m.def_submodule("propagate", "Advanced orbit propagation");
    
    py::class_<propagate::Ephemeris>(prop, "Ephemeris")
        .def(py::init<>())
        .def_readwrite("positions", &propagate::Ephemeris::positions)
        .def_readwrite("velocities", &propagate::Ephemeris::velocities)
        .def_readwrite("epochs", &propagate::Ephemeris::epochs)
        ;
    
    py::class_<propagate::Propagator>(prop, "Propagator")
        .def(py::init<>())
        .def(py::init<const Eigen::Vector3d&, const Eigen::Vector3d&,
                     const std::vector<double>&,
                     const std::function<std::tuple<Eigen::Vector3d,Eigen::Vector3d>(propagate::Propagator&, std::size_t)>&,
                     std::size_t>())
        .def_readwrite("r", &propagate::Propagator::r)
        .def_readwrite("v", &propagate::Propagator::v)
        .def_readwrite("epochs", &propagate::Propagator::epochs)
        .def_readwrite("ephem", &propagate::Propagator::ephem)
        .def_readwrite("j2", &propagate::Propagator::j2)
        .def_readwrite("tb", &propagate::Propagator::tb)
        .def_readwrite("solar", &propagate::Propagator::solar)
        .def_readwrite("atm_exp", &propagate::Propagator::atm_exp)
        .def("compute", &propagate::Propagator::compute, "Perform propagation")
        ;
    
    // Bind integrators
    prop.def("verlet", &propagate::integrators::verlet, "Verlet integrator");
    prop.def("rk45_eci", &propagate::integrators::rk45_eci, "RK45 integrator in ECI frame");
    
    // Expose frame transformation functionality
    py::module_ frames = m.def_submodule("frames", "Handle ECEF <-> ECI frame transformations");

    // Bind get_constants from iers_coef.h
    frames.def("get_constants", &utils::get_constants, "Get IERS correction constants");

    // Bind to_eci and to_ecef from frame.h in the utils namespace
    frames.def("to_eci", &utils::to_eci, py::arg("r_ecef"), py::arg("epoch"),
               "Convert ECEF vector to ECI using astronomical corrections");

    frames.def("to_ecef", &utils::to_ecef, py::arg("r_eci"), py::arg("epoch"),
               "Convert ECI vector to ECEF using astronomical corrections");
    

    // Bind orbital math utilities
    py::module_ math = m.def_submodule("orbmath", "Orbital mathematics utilities");
    math.attr("mu") = orbmath::SECONDS_PER_DAY;
    math.attr("SECONDS_PER_DAY") = orbmath::mu;
    math.attr("EARTH_RADIUS") = orbmath::EARTH_RADIUS;
    math.attr("EARTH_ECCENTRICITY") = orbmath::EARTH_ECCENTRICITY;
    math.attr("EARTH_ROTATION_RATE") = orbmath::EARTH_ROTATION_RATE;
    math.def("kepler", &orbmath::kepler, "Compute Keplerian acceleration");
    
    // Bind functions from orbmath.h
    math.def("deg2rad", &orbmath::deg2rad, "Convert degrees to radians");
    math.def("wrap_2pi", &orbmath::wrap_2pi, "Wrap angle to [0, 2π) interval");
    math.def("arcsec2rad", &orbmath::arcsec2rad, "Convert arcseconds to radians");
    math.def("geodetic_to_ecef", &orbmath::geodetic_to_ecef,
             "Convert geodetic coordinates to ECEF coordinates",
             py::arg("latDeg"), py::arg("lonDeg"), py::arg("alt_m"));
    
    // Create a Python class for the OrbitalElements struct
    py::class_<orbmath::OrbitalElements>(math, "OrbitalElements")
        .def(py::init<>())
        .def_readwrite("a", &orbmath::OrbitalElements::a)
        .def_readwrite("ecc", &orbmath::OrbitalElements::ecc)
        .def_readwrite("incl", &orbmath::OrbitalElements::incl)
        .def_readwrite("omega", &orbmath::OrbitalElements::omega)
        .def_readwrite("Omega", &orbmath::OrbitalElements::Omega)
        .def_readwrite("nu", &orbmath::OrbitalElements::nu)
        .def_readwrite("m", &orbmath::OrbitalElements::m);
    
    math.def("compute_orbital_elements", &orbmath::compute_orbital_elements,
             "Compute orbital elements from position and velocity vectors",
             py::arg("r"), py::arg("v"));
    
    // Bind perturbation models
    py::module_ perturb = math.def_submodule("perturbation", "Perturbation models");
    
    // Export J2 constant
    perturb.attr("J2") = orbmath::perturbation::J2;
    perturb.attr("MU_MOON") = orbmath::perturbation::MU_MOON;
    
    // Export SRP parameters
    perturb.attr("CR") = py::float_(orbmath::perturbation::CR);
    perturb.attr("Am") = py::float_(orbmath::perturbation::Am);
    perturb.attr("Sc") = py::float_(orbmath::perturbation::Sc);
    perturb.attr("nu") = py::float_(orbmath::perturbation::nu);
    
    // Export atmospheric drag parameters
    perturb.attr("C_D") = py::float_(orbmath::perturbation::C_D);
    perturb.attr("H0") = py::float_(orbmath::perturbation::H0);
    perturb.attr("rho0") = py::float_(orbmath::perturbation::rho0);
    
    // Bind perturbation models
    perturb.def("j2_perturbation", &orbmath::perturbation::J2_perturbation,
                "Calculate J2 perturbation acceleration",
                py::arg("pos"));
                
    perturb.def("third_body", &orbmath::perturbation::third_body,
                "Calculate third body (Moon) perturbation",
                py::arg("pos"), py::arg("jd"));
                
    perturb.def("solar_radiation", &orbmath::perturbation::solar_radiation,
                "Calculate solar radiation pressure perturbation",
                py::arg("pos"), py::arg("jd"));
                
    perturb.def("atmospheric_drag_exponential", &orbmath::perturbation::atmospheric_drag_exponential,
                "Calculate atmospheric drag using exponential model",
                py::arg("pos"), py::arg("vel"));
    
    // Bind atmospheric model
    perturb.def("atmosphere", &orbmath::perturbation::atmosphere,
                "Calculate atmospheric density (kg/m³) for given altitude in km",
                py::arg("z_km"));
    
    perturb.def("lunar_position", &orbmath::perturbation::lunar_position,
                "Calculates the position of the Moon in Earth's equatorial coordinate system using a series of trigonometric functions based on the input Julian date (jd)",
                py::arg("jd"), py::arg("r_moon"));
    
    perturb.def("solar_position", &orbmath::perturbation::solar_position,
                "Calculates the geocentric position of the sun at a given epoch",
                py::arg("jd"), py::arg("lambda"), py::arg("eps"), py::arg("r_S"));
    
    // Bind nutation models
    py::module_ nutation = math.def_submodule("nutation", "Nutation models");
    
    // Define the NutationOutput struct for Python
    py::class_<orbmath::nutation::NutationOutput>(nutation, "NutationOutput")
        .def(py::init<>())
        .def_readwrite("nut_matrix", &orbmath::nutation::NutationOutput::nut_matrix)
        .def_readwrite("meaneps", &orbmath::nutation::NutationOutput::meaneps)
        .def_readwrite("omega", &orbmath::nutation::NutationOutput::omega)
        .def_readwrite("deltapsi", &orbmath::nutation::NutationOutput::deltapsi)
        .def_readwrite("deltaeps", &orbmath::nutation::NutationOutput::deltaeps);
    
    // Bind nutation functions
    nutation.def("cross", &orbmath::nutation::cross,
                "Compute cross product of two 3D vectors",
                py::arg("a"), py::arg("b"));
                
    nutation.def("polar_motion", &orbmath::nutation::polar_motion,
                "Compute polar motion matrix",
                py::arg("xp_arcsec"), py::arg("yp_arcsec"));
                
    nutation.def("precession", &orbmath::nutation::precession,
                "Compute precession matrix (IAU-76/FK5)",
                py::arg("ttt"));
                
    nutation.def("nutation", &orbmath::nutation::nutation,
                "Compute nutation matrix (IAU-1980)",
                py::arg("ttt"), py::arg("ddpsi_mas"), py::arg("ddeps_mas"));
                
    nutation.def("sidereal", &orbmath::nutation::sidereal,
                "Compute sidereal time matrix",
                py::arg("jdUT1"), py::arg("lod"), py::arg("deltapsiRad"),
                py::arg("meaneps"), py::arg("omega"), py::arg("eqeterms"));
    
    // Export nutation coefficient constants (optional)
    nutation.attr("NUT_TERMS") = orbmath::nutation::NUT_TERMS;
    
    // Create INTERPRET submodule - Bind the abstract base class
    
    // Bind Observation struct
    py::class_<interpret::Observation>(m, "Observation")
        .def(py::init<>())
        .def_readwrite("epoch", &interpret::Observation::epoch)
        .def_readwrite("ra", &interpret::Observation::ra)
        .def_readwrite("dec", &interpret::Observation::dec)
        .def_readwrite("stationECEF", &interpret::Observation::stationECEF);
        
    // Bind StateVectors struct
    py::class_<interpret::StateVectors>(m, "StateVectors")
        .def(py::init<>())
        .def_readwrite("epoch", &interpret::StateVectors::epoch)
        .def_readwrite("r", &interpret::StateVectors::r)
        .def_readwrite("v", &interpret::StateVectors::v);
        
//    // Bind solveRadecOrbit function
//    m.def("solve_radec_orbit", &interpret::solveRadecOrbit,
//            py::arg("observations"), py::arg("mu"));
        
    // Bind the abstract base class
    py::class_<interpret::InterpretationData, std::shared_ptr<interpret::InterpretationData>>(m, "InterpretationData")
        .def("get_position", &interpret::InterpretationData::get_position)
        .def("get_velocity", &interpret::InterpretationData::get_velocity);
        
    // Bind TwoLineElement (inherits from InterpretationData)
    py::class_<interpret::TwoLineElement, interpret::InterpretationData,
                std::shared_ptr<interpret::TwoLineElement>>(m, "TwoLineElement")
        .def(py::init<const std::string&, const std::string&>())
        .def(py::init<const std::string&, size_t>(), py::arg("path"), py::arg("index") = 0)
        .def("get_position", py::overload_cast<>(&interpret::TwoLineElement::get_position, py::const_))
        .def("get_position_at", py::overload_cast<double>(&interpret::TwoLineElement::get_position, py::const_),
            py::arg("minutes"))
        .def("get_velocity", py::overload_cast<>(&interpret::TwoLineElement::get_velocity, py::const_))
        .def("get_velocity_at", py::overload_cast<double>(&interpret::TwoLineElement::get_velocity, py::const_),
            py::arg("minutes"))
        .def("get_jd", &interpret::TwoLineElement::get_jd);
        
    // Bind RADec (inherits from InterpretationData)
    py::class_<interpret::RADec, interpret::InterpretationData,
                std::shared_ptr<interpret::RADec>>(m, "RADec")
        .def(py::init<const std::vector<interpret::Observation>&>())
        .def("get_position", &interpret::RADec::get_position)
        .def("get_velocity", &interpret::RADec::get_velocity)
        .def_readonly("epoch", &interpret::RADec::m_epoch);
    
    // TDM.h
    
    // Bind the MetaData struct
    py::class_<interpret::MetaData>(m, "MetaData")
        .def(py::init<>())
        .def_readwrite("time_system", &interpret::MetaData::time_system)
        .def_readwrite("reference_frame", &interpret::MetaData::reference_frame)
        .def_readwrite("start_time", &interpret::MetaData::start_time)
        .def_readwrite("stop_time", &interpret::MetaData::stop_time)
        .def_readwrite("station_longitude", &interpret::MetaData::station_longitude)
        .def_readwrite("station_latitude", &interpret::MetaData::station_latitude)
        .def_readwrite("station_altitude", &interpret::MetaData::station_altitude)
        .def("__repr__", [](const interpret::MetaData &md) {
            return "MetaData(time_system='" + md.time_system +
                   "', reference_frame='" + md.reference_frame +
                   "', start_time=" + std::to_string(md.start_time) +
                   ", stop_time=" + std::to_string(md.stop_time) +
                   ", station_longitude=" + std::to_string(md.station_longitude) +
                   ", station_latitude=" + std::to_string(md.station_latitude) +
                   ", station_altitude=" + std::to_string(md.station_altitude) + ")";
        });
    
    // Bind the TDMData struct
    py::class_<interpret::TDMData>(m, "TDMData")
        .def(py::init<>())
        .def_readwrite("meta", &interpret::TDMData::meta)
        .def_readwrite("observations", &interpret::TDMData::observations)
        .def("__repr__", [](const interpret::TDMData &td) {
            return "TDMData(meta=..., observations=[" +
                std::to_string(td.observations.size()) + " items])";
        });

    // Bind the parse_tdm function
    m.def("parse_tdm", &interpret::parse_tdm,
        "Parse a TDM file and return metadata and observations",
        py::arg("filename"));

    // Bind the parse_tdm_w function
    m.def("parse_tdm_w", &interpret::parse_tdm_w,
        "Parse TDM files matching a wildcard pattern with time correction",
        py::arg("wildcard"), py::arg("delta"), py::arg("delta_error"));
}
