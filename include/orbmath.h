#ifndef ORBITAL_MATH_HPP
#define ORBITAL_MATH_HPP

#include <Dense>  // Include Eigen library for vector and matrix operations.

namespace orbmath {

    // --------------------------------------------------------------------------
    // CONSTANTS
    // --------------------------------------------------------------------------
    /// @brief Number of seconds in one day.
    constexpr double SECONDS_PER_DAY = 86400.0;
    /// @brief Earth's gravitational parameter (mu) in km³/s².
    constexpr double mu = 398600.4418;
    /// @brief Earth's equatorial radius (WGS-84) in kilometers.
    constexpr double EARTH_RADIUS = 6378.1370;
    /// @brief Earth's first eccentricity (WGS-84).
    constexpr double EARTH_ECCENTRICITY = 0.08181919;
    /// @brief Earth's rotation rate in radians per second.
    constexpr double EARTH_ROTATION_RATE = 7.2921150e-5;

    // --------------------------------------------------------------------------
    // ANGLE CONVERSION FUNCTIONS
    // --------------------------------------------------------------------------

    /**
     * @brief Convert an angle from degrees to radians.
     *
     * Given an angle in degrees, this function returns the corresponding
     * angle in radians using the formula:
     *   radians = degrees × (pi / 180).
     *
     * @param deg Angle in degrees.
     * @return double Angle in radians.
     */
    double deg2rad(double deg);

    /**
     * @brief Wrap an angle (in radians) into the interval [0, 2pi).
     *
     * Reduces any real‐valued angle to its principal value within the range
     * [0, 2pi). Useful for normalizing angles after arithmetic operations.
     *
     * @param rad Angle in radians (may be < 0 or ≥ 2pi).
     * @return double Equivalent angle in [0, 2pi).
     */
    double wrap_2pi(double rad);

    /**
     * @brief Convert an angle from arcseconds to radians.
     *
     * Given an angle in arcseconds, this function returns the corresponding
     * angle in radians using the conversion:
     *   1 arcsecond = (pi / 180) / 3600 radians.
     *
     * @param arcsec Angle in arcseconds.
     * @return double Angle in radians.
     */
    double arcsec2rad(double arcsec);

    // --------------------------------------------------------------------------
    // COORDINATE CONVERSION FUNCTION
    // --------------------------------------------------------------------------

    /**
     * @brief Convert geodetic coordinates to Earth-Centered Earth-Fixed (ECEF).
     *
     * Uses the WGS-84 ellipsoidal model to transform geodetic latitude,
     * longitude, and altitude into ECEF Cartesian coordinates.
     *
     * @param latDeg Geodetic latitude in degrees.
     * @param lonDeg Geodetic longitude in degrees.
     * @param alt_m Altitude above the WGS-84 reference ellipsoid in meters.
     * @return Eigen::Vector3d Position vector [x, y, z] in kilometers (ECEF frame).
     */
    Eigen::Vector3d geodetic_to_ecef(double latDeg, double lonDeg, double alt_m);

    // --------------------------------------------------------------------------
    // STRUCTURE: OrbitalElements
    // --------------------------------------------------------------------------

    /**
     * @struct OrbitalElements
     * @brief Classical orbital elements of an orbiting body.
     *
     * Contains the standard set of orbital parameters:
     *   - a     : Semi-major axis (km)
     *   - ecc   : Eccentricity (unitless)
     *   - incl  : Inclination (degrees)
     *   - omega : Argument of perigee (degrees)
     *   - Omega : Right ascension of ascending node (degrees)
     *   - nu    : True anomaly (degrees)
     *   - m     : Mean anomaly (degrees)
     */
    struct OrbitalElements {
        double a;      ///< Semi-major axis (kilometers).
        double ecc;    ///< Eccentricity (unitless).
        double incl;   ///< Inclination (degrees).
        double omega;  ///< Argument of perigee (degrees).
        double Omega;  ///< Right ascension of ascending node (degrees).
        double nu;     ///< True anomaly (degrees).
        double m;      ///< Mean anomaly (degrees).
    };

    // --------------------------------------------------------------------------
    // ORBITAL ELEMENTS COMPUTATION FUNCTION
    // --------------------------------------------------------------------------

    /**
     * @brief Compute classical orbital elements from state vectors.
     *
     * Given a position vector \p r (km) and velocity vector \p v (km/s)
     * in an inertial frame, this function computes the classical orbital
     * elements: semi-major axis (a), eccentricity (ecc), inclination (incl),
     * argument of perigee (omega), right ascension of ascending node (Omega),
     * true anomaly (nu), and mean anomaly (m). All returned angles are in degrees.
     *
     * @param r Position vector [x, y, z] in kilometers.
     * @param v Velocity vector [vx, vy, vz] in kilometers per second.
     * @return OrbitalElements Struct containing the computed orbital elements.
     */
    OrbitalElements compute_orbital_elements(const Eigen::Vector3d& r, const Eigen::Vector3d& v);

    // --------------------------------------------------------------------------
    // KEPLERIAN ACCELERATION FUNCTION
    // --------------------------------------------------------------------------

    /**
     * @brief Compute two-body (Keplerian) acceleration from a state vector.
     *
     * Calculates the gravitational acceleration vector based on Kepler's law
     * using the formula:
     *   a = −mu / |r|³ * r
     * where mu is Earth's gravitational parameter, and r is the position vector.
     *
     * @param r Position vector [x, y, z] in kilometers.
     * @param dt Time step in seconds (not used in this central‐force model).
     * @return Eigen::Vector3d Acceleration vector [ax, ay, az] in km/s².
     */
    Eigen::Vector3d kepler(const Eigen::Vector3d &r, double dt);

} // namespace orbmath

#endif // ORBITAL_MATH_HPP
