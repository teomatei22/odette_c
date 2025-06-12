// ALGORITHM 10.4: CALCULATE THE GEOCENTRIC POSITION OF THE MOON AT A GIVEN EPOCH

#ifndef LUNAR_POSITION_H
#define LUNAR_POSITION_H

#include <cmath>    // Provides standard math functions such as sin, cos, and fmod.
#include <array>    // For fixed-size arrays if needed.
#include <Dense>    // Provides Eigen library functionality for vector operations.
#define _USE_MATH_DEFINES  // Ensure M_PI and other math constants are defined.

 /*
    Calculates the geocentric equatorial position vector of the moon
    given the Julian day.

    User h-functions required: None
*/

// -----------------------------------------------------------------------------
// Namespace: orbmath::perturbation
// This namespace encapsulates functions that apply perturbation models to
// celestial bodies. In this case, it includes the function to compute the
// Moon's position given a Julian date.
// -----------------------------------------------------------------------------
namespace orbmath::perturbation {

    /**
     * @brief Computes the geocentric equatorial position vector of the Moon.
     *
     * This inline function calculates the position of the Moon in Earth's equatorial
     * coordinate system using a series of trigonometric functions based on the input
     * Julian date (jd). The computed vector (r_moon) is expressed in kilometers.
     *
     * @param jd The Julian day for which the Moon's position is calculated.
     * @param r_moon Reference to an Eigen::Vector3d that will hold the computed position vector.
     */
    inline void lunar_position(double jd, Eigen::Vector3d &r_moon) {
        // Earth's mean radius (in kilometers)
        const double RE = 6378.14;

        // ------------------------- implementation -----------------
        // Compute the time (in Julian centuries) since the standard epoch J2000.0.
        double T = (jd - 2451545.0) / 36525.0;
        // T represents the elapsed time in centuries since J2000, used for trigonometric arguments.

        // Compute the ecliptic longitude of the Moon (in degrees)
        // The formula is a series expansion with periodic terms accounting for the Moon's orbital elements.
        double e_long = 218.32 + 481267.881 * T
            + 6.29 * sin((135.0 + 477198.87 * T) * M_PI / 180.0)
            - 1.27 * sin((259.3 - 413335.36 * T) * M_PI / 180.0)
            + 0.66 * sin((235.7 + 890534.22 * T) * M_PI / 180.0)
            + 0.21 * sin((269.9 + 954397.74 * T) * M_PI / 180.0)
            - 0.19 * sin((357.5 + 35999.05 * T) * M_PI / 180.0)
            - 0.11 * sin((186.5 + 966404.03 * T) * M_PI / 180.0);
        // Normalize the ecliptic longitude to the range [0, 360) degrees.
        e_long = fmod(e_long, 360.0);

        // Compute the ecliptic latitude of the Moon (in degrees)
        // This calculation accounts for the Moon's inclination relative to the ecliptic.
        double e_lat = 5.13 * sin((93.3 + 483202.02 * T) * M_PI / 180.0)
            + 0.28 * sin((228.2 + 960400.89 * T) * M_PI / 180.0)
            - 0.28 * sin((318.3 + 6003.15 * T) * M_PI / 180.0)
            - 0.17 * sin((217.6 - 407332.21 * T) * M_PI / 180.0);
        // Normalize the ecliptic latitude if necessary.
        e_lat = fmod(e_lat, 360.0);

        // Compute the horizontal parallax (in degrees)
        // Horizontal parallax relates to the apparent shift in the Moon's position due to the observer's perspective.
        double h_par = 0.9508
            + 0.0518 * cos((135.0 + 477198.87 * T) * M_PI / 180.0)
            + 0.0095 * cos((259.3 - 413335.36 * T) * M_PI / 180.0)
            + 0.0078 * cos((235.7 + 890534.22 * T) * M_PI / 180.0)
            + 0.0028 * cos((269.9 + 954397.74 * T) * M_PI / 180.0);
        // Normalize the horizontal parallax angle.
        h_par = fmod(h_par, 360.0);

        // Compute the obliquity of the ecliptic (in degrees)
        // This is the angle between Earth's orbital plane and its equator.
        double obliquity = 23.439291 - 0.0130042 * T;

        // Compute the direction cosines of the Moon's position vector.
        // These factors convert the computed spherical coordinates into Cartesian coordinates.
        double l = cos(e_lat * M_PI / 180.0) * cos(e_long * M_PI / 180.0);
        double m = cos(obliquity * M_PI / 180.0) * cos(e_lat * M_PI / 180.0) * sin(e_long * M_PI / 180.0)
                 - sin(obliquity * M_PI / 180.0) * sin(e_lat * M_PI / 180.0);
        double n = sin(obliquity * M_PI / 180.0) * cos(e_lat * M_PI / 180.0) * sin(e_long * M_PI / 180.0)
                 + cos(obliquity * M_PI / 180.0) * sin(e_lat * M_PI / 180.0);

        // Compute the Earth-Moon distance (in kilometers)
        // The distance is derived from the Earth’s radius and the horizontal parallax.
        double dist = RE / sin(h_par * M_PI / 180.0);

        // Compute the Moon's geocentric equatorial position vector (in kilometers)
        // The vector is formed by scaling the direction cosines by the Earth-Moon distance.
        r_moon = {dist * l, dist * m, dist * n};
    }
}

#endif // LUNAR_POSITION_H
