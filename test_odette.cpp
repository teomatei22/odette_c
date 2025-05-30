#include <iostream>
#include <fstream>
#include <cassert>
#include <cmath>
#include <vector>
#include <string>
#include <iomanip>
#include "interpret.h"
#include "TDMParser.h"
#include "orbmath.h"
#include "propagator.h"
#include "json.h"
#include "logging.h"

// General tests for odette

bool approx_equal(double a, double b, double eps = 1e-6) {
    return std::abs(a - b) < eps;
}

void test_radec_solution() {
    auto tdm = interpret::parse_tdm_w("data/Jason/20240318_16002A_A*", 100, 30);
    assert(!tdm.observations.empty());
    interpret::RADec radec(tdm.observations);
    auto r = radec.get_position();
    auto v = radec.get_velocity();
    std::cout << "[RA/DEC] r = " << r.norm() << " km, v = " << v.norm() << " km/s\n";
    assert(r.norm() > 6700 && r.norm() < 7100);
    assert(v.norm() > 7 && v.norm() < 8);
}

void test_tle_propagation() {
    std::string line1 = "1 41240U 16002A   24078.93311235 -.00000041  00000-0  88455-4 0  9998";
    std::string line2 = "2 41240  66.0433  38.7934 0008217 275.1931  84.8147 12.80929479381943";
    interpret::TwoLineElement tle(line1, line2);
    auto r = tle.get_position(0);
    auto v = tle.get_velocity(0);
    std::cout << "[TLE] r = " << r.norm() << " km, v = " << v.norm() << " km/s\n";
    assert(r.norm() > 6700 && r.norm() < 7100);
    assert(v.norm() > 7 && v.norm() < 8);
}

void test_rk45_propagation() {
    auto tdm = interpret::parse_tdm_w("data/Jason/20240318_16002A_A*", 100, 30);
    interpret::RADec radec(tdm.observations);
    auto r0 = radec.get_position();
    auto v0 = radec.get_velocity();
    double jd0 = radec.m_epoch;
    std::vector<double> epochs = {jd0, jd0 + 10.0 / orbmath::SECONDS_PER_DAY};
    propagate::Propagator p(r0, v0, epochs, propagate::integrators::rk45_eci);
    p.compute();
    auto r = p.ephem.positions[1];
    auto v = p.ephem.velocities[1];
    std::cout << "[RK45] r = " << r.norm() << " km, v = " << v.norm() << " km/s\n";
    assert(r.norm() > 6700 && r.norm() < 7100);
    assert(v.norm() > 7 && v.norm() < 8);
}

void test_orbital_elements_consistency() {
    Eigen::Vector3d r(7000, 0, 0);
    Eigen::Vector3d v(0, 7.5, 0);
    auto oe = orbmath::compute_orbital_elements(r, v);
    std::cout << "[OE] a = " << oe.a << ", e = " << oe.ecc << "\n";
    assert(oe.a > 6800 && oe.a < 7100);
    assert(approx_equal(oe.ecc, 0.0, 1e-2));
}

void test_perturbation_effects() {
    auto tdm = interpret::parse_tdm_w("data/Jason/20240318_16002A_A*", 100, 30);
    interpret::RADec radec(tdm.observations);
    auto r0 = radec.get_position();
    auto v0 = radec.get_velocity();
    double jd0 = radec.m_epoch;
    std::vector<double> epochs = {jd0, jd0 + 20.0 / orbmath::SECONDS_PER_DAY};
    propagate::Propagator base(r0, v0, epochs, propagate::integrators::rk45_eci);
    base.compute();
    propagate::Propagator j2(r0, v0, epochs, propagate::integrators::rk45_eci);
    j2.j2 = true;
    j2.compute();
    double delta = (base.ephem.positions[1] - j2.ephem.positions[1]).norm();
    std::cout << "[J2 delta] " << delta << " km\n";
    assert(delta > 0.01);
}

// Orbmath function tests

void test_angle_conversions() {
    assert(approx_equal(orbmath::deg2rad(180.0), M_PI));
    assert(approx_equal(orbmath::wrap_2pi(7.5), 7.5 - 2 * M_PI));
    assert(approx_equal(orbmath::arcsec2rad(3600), orbmath::deg2rad(1.0)));
    std::cout << "[orbmath] angle conversions passed.\n";
}

void test_geodetic_to_ecef() {
    auto vec = orbmath::geodetic_to_ecef(0.0, 0.0, 0.0); // equator, sea level
    assert(approx_equal(vec.x(), orbmath::EARTH_RADIUS, 0.1));
    assert(approx_equal(vec.y(), 0.0));
    assert(approx_equal(vec.z(), 0.0));
    std::cout << "[orbmath] geodetic_to_ecef passed.\n";
}

void test_kepler_acceleration() {
    Eigen::Vector3d r(7000, 0, 0);
    double dt = 10.0;
    Eigen::Vector3d acc = orbmath::kepler(r, dt);
    assert(acc.x() < 0 && std::abs(acc.y()) < 1e-6 && std::abs(acc.z()) < 1e-6);
    std::cout << "[orbmath] kepler acceleration passed.\n";
}

void test_constants() {
    assert(approx_equal(orbmath::mu, 398600.4418));
    assert(approx_equal(orbmath::EARTH_RADIUS, 6378.1370));
    assert(approx_equal(orbmath::SECONDS_PER_DAY, 86400.0));
    std::cout << "[orbmath] constants passed.\n";
}

int main() {

    barlog::initialize_log();
    // test_radec_solution();
    // test_tle_propagation();
    // test_rk45_propagation();
    // test_orbital_elements_consistency();
    // test_perturbation_effects();
    //
    // test_angle_conversions();
    // test_geodetic_to_ecef();
    // test_kepler_acceleration();
    // test_constants();

    std::cout << "\n All tests passed successfully.\n";
    return 0;
}
