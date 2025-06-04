#include <Dense>
#include <iostream>
#include <cmath>
#include <vector>
#include "orbmath.h"

#include "logging.h"

namespace orbmath {

    /**
     * @brief Convert degrees to radians.
     *
     * Given an angle in degrees, returns the equivalent angle in radians.
     *
     * @param deg Angle in degrees.
     * @return double Angle in radians.
     */
    double deg2rad(double deg) {
        return (M_PI / 180.0) * deg;
    }

    /**
     * @brief Convert arcseconds to radians.
     *
     * Given an angle in arcseconds, returns the equivalent angle in radians.
     * Note: 1 arcsecond = 1/3600 degree.
     *
     * @param arcsec Angle in arcseconds.
     * @return double Angle in radians.
     */
    double arcsec2rad(double arcsec) {
        // 1 arcsecond = 1/3600 deg = (PI/180)/3600 rad
        return arcsec * (M_PI / (180.0 * 3600.0));
    }

    /**
     * @brief Wrap an angle to the range [0, 2pi).
     *
     * Reduces any real-valued angle x to the principal value in the range [0, 2pi).
     *
     * @param x Angle in radians (may be outside [0, 2pi) interval).
     * @return double Wrapped angle in [0, 2pi).
     */
    double wrap_2pi(double x) {
        x = fmod(x, 2 * M_PI);
        return (x < 0) ? x + 2 * M_PI : x;
    }

    /**
     * @brief Clamp a value to a specified range.
     *
     * Ensures that x lies within the closed interval [low, high]. This is
     * particularly useful for guarding against domain errors in functions like acos.
     *
     * @param x Value to clamp.
     * @param low Lower bound (default: -1.0).
     * @param high Upper bound (default: 1.0).
     * @return double Clamped value in [low, high].
     */
    double clamp(double x, double low = -1.0, double high = 1.0) {
        return std::max(low, std::min(high, x));
    }

    /**
     * @brief Convert geodetic coordinates to Earth-Centered Earth-Fixed (ECEF).
     *
     * Uses the WGS-84 ellipsoid model to convert latitude, longitude, and altitude
     * into an ECEF position vector in kilometers.
     *
     * @param latDeg Geodetic latitude in degrees.
     * @param lonDeg Geodetic longitude in degrees.
     * @param alt_m Altitude above the WGS-84 ellipsoid in meters.
     * @return Eigen::Vector3d Position vector [x, y, z] in kilometers (ECEF).
     */
    Eigen::Vector3d geodetic_to_ecef(double latDeg, double lonDeg, double alt_m) {
        double phi_gd = deg2rad(latDeg);
        double lam = deg2rad(lonDeg);
        double h = alt_m / 1000.0; // convert meters to kilometers

        double e2 = EARTH_ECCENTRICITY * EARTH_ECCENTRICITY;

        // Compute prime vertical radius of curvature (C_e) and second eccentricity factor (S_e)
        double C_e = EARTH_RADIUS / std::sqrt(1.0 - e2 * std::pow(std::sin(phi_gd), 2));
        double S_e = C_e * (1.0 - e2);

        // Compute coordinates in kilometers
        double r_delta = (C_e + h) * std::cos(phi_gd);
        double r_K = (S_e + h) * std::sin(phi_gd);

        double x = r_delta * std::cos(lam);
        double y = r_delta * std::sin(lam);
        double z = r_K;

        return Eigen::Vector3d(x, y, z);
    }

    /**
     * @brief Compute classical orbital elements from position and velocity vectors.
     *
     * Given a position vector r and velocity vector v in an inertial frame (kilometers and
     * kilometers per second), computes the six classical orbital elements:
     *   - Semi-major axis (a)
     *   - Eccentricity (ecc)
     *   - Inclination (incl)
     *   - Argument of perigee (omega)
     *   - Right ascension of ascending node (Omega)
     *   - True anomaly (nu)
     *   - Mean anomaly (m)
     *
     * The angles in the returned OrbitalElements structure are expressed in degrees.
     *
     * @param r Position vector [x, y, z] in kilometers.
     * @param v Velocity vector [vx, vy, vz] in kilometers per second.
     * @return OrbitalElements Struct containing the computed orbital elements.
     */
    OrbitalElements compute_orbital_elements(const Eigen::Vector3d& r, const Eigen::Vector3d& v) {
        barlog::info("Computing orbital elements.");

        constexpr double undefined = std::numeric_limits<double>::quiet_NaN();
        const double small = 1e-10;

        OrbitalElements elems = {undefined, undefined, undefined, undefined, undefined, undefined, undefined};

        double r_norm = r.norm();
        double v_norm = v.norm();

        Eigen::Vector3d r_unit = r / r_norm;
        auto v_r = r_unit.dot(v);
        auto v_p = sqrt(v_norm * v_norm + v_r * v_r);

        // Specific angular momentum vector and its magnitude
        Eigen::Vector3d h = r.cross(v);
        double h_norm = h.norm();

        // Eccentricity vector and magnitude
        Eigen::Vector3d evec = ((v_norm * v_norm - mu / r_norm) * r - r.dot(v) * v) / mu;
        double ecc = evec.norm();

        // Specific mechanical energy
        double energy = v_norm * v_norm / 2.0 - mu / r_norm;

        double a, p;
        if (std::abs(ecc - 1.0) > small) {
            // Elliptic or hyperbolic orbit
            a = -mu / (2.0 * energy);
            p = a * (1.0 - ecc * ecc);
        } else {
            // Parabolic orbit
            p = h_norm * h_norm / mu;
            a = std::numeric_limits<double>::infinity();
        }

        // Inclination
        double incl = acos(clamp(h.z() / h_norm));

        // Node vector (line of nodes) and its magnitude
        Eigen::Vector3d k(0, 0, 1);
        Eigen::Vector3d n = k.cross(h);
        double n_norm = n.norm();

        // Right ascension of ascending node (Ω)
        double raan = (n_norm > small) ? atan2(n.y(), n.x()) : 0.0;
        raan = wrap_2pi(raan);

        // Argument of perigee (ω)
        double argp = (n_norm > small && ecc > small)
            ? atan2(evec.dot(h.cross(n)) / (n_norm * h_norm),
                    n.dot(evec) / (n_norm * ecc))
            : 0.0;
        argp = wrap_2pi(argp);

        // True anomaly (ν)
        double nu = (ecc > small) ? clamp(evec.dot(r) / (ecc * r_norm)) : 0.0;
        if (r.dot(v) < 0.0) {
            nu = 2.0 * M_PI - nu;
        }
        nu = wrap_2pi(nu);

        // Eccentric anomaly (E) and Mean anomaly (M)
        double cosE = (1.0 - r_norm / a) / ecc;
        cosE = clamp(cosE);
        double sinE = r.dot(v) / (ecc * std::sqrt(mu * a));
        double E = atan2(sinE, cosE);
        E = wrap_2pi(E);
        double M = E - ecc * sin(E);
        M = wrap_2pi(M);

        elems.a     = a;
        elems.ecc   = ecc;
        elems.incl  = incl * 180.0 / M_PI;
        elems.omega = argp * 180.0 / M_PI;
        elems.Omega = raan * 180.0 / M_PI;
        elems.nu    = nu * 180.0 / M_PI;
        elems.m     = M * 180.0 / M_PI;

        return elems;
    }

    /**
     * @brief Compute the two-body (Keplerian) acceleration.
     *
     * Given the position vector r (in kilometers) and a time step dt (unused
     * in the simple central‐force model), returns the acceleration vector due
     * to the Earth's gravitational parameter (mu).
     *
     * @param r Position vector [x, y, z] in kilometers.
     * @param dt Time step in seconds (not used for constant‐force evaluation).
     * @return Eigen::Vector3d Acceleration vector [ax, ay, az] in km/s².
     */
    Eigen::Vector3d kepler(const Eigen::Vector3d &r, double dt) {
        return -mu / std::pow(r.norm(), 3) * r;
    }

} // namespace orbmath
