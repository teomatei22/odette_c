// ALGORITHM 10.2: CALCULATE THE GEOCENTRIC POSITION OF THE SUN AT A GIVEN EPOCH

#ifndef SOLAR_POSITION_H
#define SOLAR_POSITION_H

#include <cmath>     ///< Math functions like sin, cos, fmod
#include <array>
#include <Dense>     ///< Eigen::Vector3d
#define _USE_MATH_DEFINES

/**
 * @file solar_position.h
 * @brief Computes the geocentric equatorial position vector of the Sun.
 */

namespace orbmath::perturbation {

    /**
     * @brief Calculates the Sun's geocentric position vector at a given Julian date.
     *
     * This function estimates the Sun's position in geocentric equatorial coordinates
     * based on simplified solar theory. The position is returned in kilometers and
     * assumes Earth is at the origin.
     *
     * @param[in]  jd     Julian Date at which to compute the solar position.
     * @param[out] lamda  Apparent ecliptic longitude of the Sun in degrees.
     * @param[out] eps    Obliquity of the ecliptic in degrees.
     * @param[out] r_S    Geocentric equatorial position vector of the Sun (km).
     */
    inline void solar_position(double jd, double &lamda, double &eps, Eigen::Vector3d &r_S)
    {
        // Astronomical Unit in kilometers
        const double AU = 149597870.691;

        // Days since J2000.0
        double n = jd - 2451545.0;

        // Julian centuries since J2000.0
        double cy = n / 36525.0;

        // Mean anomaly (degrees)
        double M = 357.528 + 0.9856003 * n;
        M = fmod(M, 360.0);

        // Mean longitude (degrees)
        double L = 280.460 + 0.98564736 * n;
        L = fmod(L, 360.0);

        // Apparent ecliptic longitude (degrees)
        lamda = L + 1.915 * sin(M * M_PI / 180.0) + 0.020 * sin(2 * M * M_PI / 180.0);
        lamda = fmod(lamda, 360.0);

        // Obliquity of the ecliptic (degrees)
        eps = 23.439 - 0.0000004 * n;

        // Direction cosines from Earth to Sun
        double u_x = cos(lamda * M_PI / 180.0);
        double u_y = sin(lamda * M_PI / 180.0) * cos(eps * M_PI / 180.0);
        double u_z = sin(lamda * M_PI / 180.0) * sin(eps * M_PI / 180.0);

        // Earth-Sun distance in km
        double rS = (1.00014
                     - 0.01671 * cos(M * M_PI / 180.0)
                     - 0.000140 * cos(2 * M * M_PI / 180.0)) * AU;

        // Geocentric position vector of the Sun
        r_S = {rS * u_x, rS * u_y, rS * u_z};
    }

}

#endif // SOLAR_POSITION_H