#ifndef ORBMATH_PERTURBATION_H
#define ORBMATH_PERTURBATION_H

#include <cmath>     // Provides math functions for trigonometric and exponential calculations.
#include <Dense>     // Provides the Eigen library for vector and matrix operations.

#include "atmosphere.h"      // Provides atmospheric density model.
#include "orbmath.h"         // Provides common orbital math constants and functions.
#include "lunar_position.h"  // Provides functions to compute the Moon's position.
#include "solar_position.h"  // Provides functions to compute the Sun's position.

namespace orbmath {
    namespace perturbation {

        // ---------------------------------------------------------------------
        // CONSTANTS FOR PERTURBATION CALCULATIONS
        // ---------------------------------------------------------------------
        static const double J2 = 1082.63e-6; // Earth's second zonal harmonic (J2) accounting for Earth's oblateness.
        static const double MU_MOON = 4903.0;  // Gravitational parameter of the Moon in km^3/s^2.

        // ---------------------------------------------------------------------
        // SOLAR RADIATION PRESSURE CONSTANTS (for Jason-3 satellite)
        // ---------------------------------------------------------------------
        // CR: Radiation pressure coefficient.
        inline double CR = 1.3;
        // Am: Area-to-mass ratio in km^2/kg.
        inline double Am = 0.02;
        // Sc: Solar constant (pressure scaling factor).
        inline double Sc = 4.56e-6;
        // nu: Shadow factor (equal to 1 if in sunlight, 0 if in shadow).
        inline double nu = 1;

        // ---------------------------------------------------------------------
        // ATMOSPHERIC DRAG CONSTANTS (for Jason-3 satellite)
        // ---------------------------------------------------------------------
        // C_D: Drag coefficient.
        inline double C_D = 2.2;
        // H0: Scale height for the exponential atmospheric model.
        inline double H0 = 100.0;
        // rho0: Reference atmospheric density (kg/m^3) at H0.
        inline double rho0 = 3.614e-13;


        // -----------------------------------------------------------------------------
        //  1) J2 PERTURBATION
        // -----------------------------------------------------------------------------
        /**
         * @brief Computes the acceleration due to the Earth's J2 perturbation.
         *
         * This function calculates the perturbing acceleration caused by the oblateness
         * of the Earth (J2 effect) using the formula from Howard Curtis, equation (12.30).
         *
         * @param pos The current position vector of the satellite (in km).
         * @return Eigen::Vector3d The acceleration vector due to the J2 perturbation (in km/s²).
         */
        inline Eigen::Vector3d J2_perturbation(const Eigen::Vector3d &pos) {
            constexpr double r_tol = 1e-6; // Tolerance to avoid division by zero singularity.

            // Extract Cartesian coordinates from the position vector.
            double x = pos[0];
            double y = pos[1];
            double z = pos[2];
            // Compute squared norm and norm (magnitude) of the position vector.
            double r2 = pos.squaredNorm();
            double r = std::sqrt(r2);

            // If r is too small, return zero vector to avoid singularity in the computation.
            if (r < r_tol) return Eigen::Vector3d::Zero();

            double z2 = z * z;
            // Compute r^5 for scaling in the J2 formula.
            double r5 = r2 * r2 * r;

            // Compute the scaling factor for the J2 perturbation acceleration.
            double factor = -1.5 * J2 * mu * (orbmath::EARTH_RADIUS * orbmath::EARTH_RADIUS) / r5;
            // fz2 is used to account for the z-component effect relative to the radial distance.
            double fz2 = 5.0 * z2 / r2;

            // Return the computed acceleration vector.
            return factor * Eigen::Vector3d {
                x * (1.0 - fz2),
                y * (1.0 - fz2),
                z * (3.0 - fz2)
            };
        }


        // -----------------------------------------------------------------------------
        //  2) THIRD BODY PERTURBATION
        // -----------------------------------------------------------------------------
        /**
         * @brief Computes the acceleration due to third-body gravitational perturbation.
         *
         * This function calculates the perturbing acceleration from a third body—here, the Moon.
         * It computes the difference between the gravitational effects at the satellite's position
         * and the third body's position.
         *
         * @param pos The current position vector of the satellite (in km).
         * @param jd The Julian date at which the perturbation is evaluated.
         * @return Eigen::Vector3d The acceleration vector due to the third body (in km/s²).
         */
        inline Eigen::Vector3d third_body(const Eigen::Vector3d &pos, double jd) {
            auto rvec = pos; // Satellite position vector.

            // Get Moon's geocentric position vector (in the appropriate frame).
            Eigen::Vector3d r_moon;
            lunar_position(jd, r_moon);

            // Compute the relative vector from the satellite to the Moon.
            Eigen::Vector3d r_ms = r_moon - rvec;

            // Compute norms required for acceleration calculation.
            double r_ms_norm = r_ms.norm();
            double r_moon_norm = r_moon.norm();

            // Calculate the third-body perturbing acceleration using the inverse cube law.
            Eigen::Vector3d a_third_body =
                MU_MOON * ((r_ms / std::pow(r_ms_norm, 3)) - (r_moon / std::pow(r_moon_norm, 3)));

            return a_third_body;
        }


        // -----------------------------------------------------------------------------
        //  3) SOLAR RADIATION PRESSURE
        // -----------------------------------------------------------------------------
        /**
         * @brief Computes the acceleration due to solar radiation pressure.
         *
         * This function estimates the perturbing acceleration resulting from solar radiation.
         * It calculates the acceleration by scaling the unit vector from the satellite to the Sun
         * by the solar pressure parameters and satellite properties.
         *
         * @param pos The current position vector of the satellite (in km).
         * @param jd The Julian date for which the solar position is computed.
         * @return Eigen::Vector3d The acceleration vector due to solar radiation pressure (in km/s²).
         */
        inline Eigen::Vector3d solar_radiation(const Eigen::Vector3d &pos, double jd) {
            auto rvec = pos; // Satellite position vector.

            double lambda, epsilon; // Variables to hold solar longitude and obliquity.
            Eigen::Vector3d r_sun;  // Will store the Sun's position.
            // Obtain the solar position with the corresponding parameters.
            solar_position(jd, lambda, epsilon, r_sun);

            // Compute the vector from the satellite to the Sun.
            Eigen::Vector3d r = rvec - r_sun;
            double r_norm = r.norm();

            // Calculate the solar radiation pressure acceleration.
            // The acceleration is opposite to the direction of the Sun relative to the satellite.
            Eigen::Vector3d a_solar_radiation = -nu * Sc * (CR * Am) * (r / r_norm);

            return a_solar_radiation;
        }



        // -----------------------------------------------------------------------------
        //  4) ATMOSPHERIC DRAG
        // -----------------------------------------------------------------------------
        /**
         * @brief Computes the atmospheric drag acceleration using an exponential model.
         *
         * This function calculates the drag acceleration acting on a satellite due to
         * atmospheric density. The satellite's relative velocity with respect to the atmosphere
         * (which rotates with the Earth) is used to compute the drag force.
         *
         * @param pos Satellite position vector in ECEF coordinates (km).
         * @param vel Satellite velocity vector in ECEF coordinates (km/s).
         * @return Eigen::Vector3d The drag acceleration vector (km/s²).
         */
        inline Eigen::Vector3d atmospheric_drag_exponential(const Eigen::Vector3d &pos,
                                                      const Eigen::Vector3d &vel) {

            // Treat input position and velocity as already in the Earth-Centered Earth-Fixed (ECEF) frame.
            const Eigen::Vector3d r_ecef = pos; // km
            const Eigen::Vector3d v_ecef = vel; // km/s

            // Compute the norm of the position vector and the altitude above Earth's surface.
            const double r_norm = r_ecef.norm();          // km
            const double alt_km = r_norm - EARTH_RADIUS;

            // Retrieve the atmospheric density at the given altitude using the exponential model.
            // The atmosphere() function returns density in kg/m^3.
            const double rho = atmosphere(alt_km);        // kg/m^3

            // Earth's atmosphere rotates. Compute the rotational velocity vector:
            // v_atm = ω × r, where ω is Earth's rotation rate, assumed along the z-axis.
            Eigen::Vector3d v_atm = EARTH_ROTATION_RATE * Eigen::Vector3d(0, 0, 1).cross(r_ecef); // km/s

            // Compute the relative velocity between the satellite and the rotating atmosphere.
            Eigen::Vector3d v_rel = v_ecef - v_atm;       // km/s
            double v_rel_norm = v_rel.norm();             // km/s

            // Compute the atmospheric drag acceleration using the drag equation:
            // a_drag = -0.5 * ρ * C_D * (A/m) * |v_rel| * v_rel, where A/m is the area-to-mass ratio.
            Eigen::Vector3d a_drag = -0.5 * rho * C_D * Am * v_rel_norm * v_rel; // km/s²

            return a_drag;
        }

    } // namespace perturbation
} // namespace orbmath

#endif //ORBMATH_PERTURBATION_H
