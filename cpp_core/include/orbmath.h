#ifndef ORBITAL_MATH_HPP
#define ORBITAL_MATH_HPP

#include <Eigen/Dense>  // Include Eigen library for vector and matrix operations.

namespace orbmath {

    // --------------------------------------------------------------------------
    // CONSTANTS
    // --------------------------------------------------------------------------
    // Total number of seconds in one day.
    constexpr double SECONDS_PER_DAY = 86400.0;
    // Earth's gravitational parameter in km^3/s^2.
    constexpr double mu = 398600.4418; // km^3/s^2
    // Earth's radius in kilometers as per the WGS-84 standard.
    constexpr double EARTH_RADIUS = 6378.1370; // km (WGS-84)
    // Eccentricity of Earth based on the WGS-84 ellipsoid.
    constexpr double EARTH_ECCENTRICITY = 0.08181919;
    // Earth's rotation rate in radians per second.
    constexpr double EARTH_ROTATION_RATE = 7.2921150e-5; // rad/s

    // --------------------------------------------------------------------------
    // ANGLE CONVERSION FUNCTIONS
    // --------------------------------------------------------------------------
    // Converts an angle from degrees to radians.
    double deg2rad(double deg);
    // Wraps an angle (in radians) into the [0, 2π) interval.
    double wrap_2pi(double rad);
    // Converts an angle from arcseconds to radians.
    double arcsec2rad(double arcsec);

    // --------------------------------------------------------------------------
    // COORDINATE CONVERSION FUNCTION
    // --------------------------------------------------------------------------
    // Converts geodetic coordinates (latitude in degrees, longitude in degrees,
    // and altitude in meters) into Earth-Centered Earth-Fixed (ECEF) coordinates.
    Eigen::Vector3d geodetic_to_ecef(double latDeg, double lonDeg, double alt_m);

    // --------------------------------------------------------------------------
    // STRUCTURE: OrbitalElements
    // --------------------------------------------------------------------------
    // Represents the classical orbital elements:
    //   a     - Semi-major axis,
    //   ecc   - Eccentricity,
    //   incl  - Inclination,
    //   omega - Argument of perigee,
    //   Omega - Right ascension of ascending node,
    //   nu    - True anomaly,
    //   m     - Mean anomaly.
    struct OrbitalElements {
        double a;      // Semi-major axis.
        double ecc;    // Eccentricity.
        double incl;   // Inclination.
        double omega;  // Argument of perigee.
        double Omega;  // Right ascension of ascending node.
        double nu;     // True anomaly.
        double m;      // Mean anomaly.
    };

    // --------------------------------------------------------------------------
    // ORBITAL ELEMENTS COMPUTATION FUNCTION
    // --------------------------------------------------------------------------
    // Computes the classical orbital elements given the state vectors.
    // Parameters:
    //   - r: Position vector (km)
    //   - v: Velocity vector (km/s)
    // Returns:
    //   - OrbitalElements structure containing the orbital parameters.
    OrbitalElements compute_orbital_elements(const Eigen::Vector3d& r, const Eigen::Vector3d& v);

    // --------------------------------------------------------------------------
    // KEPLERIAN ACCELERATION FUNCTION
    // --------------------------------------------------------------------------
    /// @brief Calculates acceleration using Kepler's law based on the state vector.
    /// @param r The current position vector.
    /// @param dt Time step in seconds over which the acceleration is computed.
    /// @return Velocity change vector computed from Keplerian dynamics.
    Eigen::Vector3d kepler(const Eigen::Vector3d &r, double dt);

} // namespace orbmath

#endif // ORBITAL_MATH_HPP
