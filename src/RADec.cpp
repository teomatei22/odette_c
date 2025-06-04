#include "interpret.h"
#include <iostream>
#include <Dense>
#include <cmath>
#include <format>
#include <stdexcept>
#include <vector>
#include <limits>
#include "TDMParser.h"
#include <iomanip>
#include "orbmath.h"
#include <unsupported/Eigen/Polynomials>

#include "frame.h"
#define frac(x) (x-floor(x))

namespace interpret {

    /**
     * @brief Convert right ascension and declination angles into a unit direction vector.
     *
     * Given right ascension (ra) and declination (dec) in radians, this function
     * computes the corresponding unit vector in Cartesian coordinates:
     *   x = cos(dec) * cos(ra)
     *   y = cos(dec) * sin(ra)
     *   z = sin(dec)
     *
     * @param ra Right ascension angle, in radians.
     * @param dec Declination angle, in radians.
     * @return Eigen::Vector3d A unit vector pointing in the direction specified by (ra, dec).
     */
    Eigen::Vector3d radec_to_unit_vector(double ra, double dec) {
        return Eigen::Vector3d(std::cos(dec) * std::cos(ra),
                               std::cos(dec) * std::sin(ra),
                               std::sin(dec));
    }

    /**
     * @brief Solve for initial position and velocity vectors using Gauss's method.
     *
     * This function takes at least three optical observations (each containing an epoch,
     * station ECEF position, and right ascension/declination angles) and computes the
     * approximate satellite state vectors (position and velocity) at the middle observation’s epoch.
     * It uses the classical Gauss method of orbit determination:
     *   1. Converts observed RA/Dec to line-of-sight unit vectors.
     *   2. Transforms station ECEF coordinates to ECI at each observation epoch.
     *   3. Constructs the Lambert-like linear system to estimate slant ranges.
     *   4. Solves a ninth‐degree polynomial for the middle slant range magnitude.
     *   5. Computes the position vectors r1, r2, r3 in ECI coordinates.
     *   6. Uses Gibbs method to estimate the velocity vector at r2.
     *
     * @param observations A reference to a vector of at least three Observation structs.
     *        Each Observation must contain:
     *          - epoch      : Time in days since J2000 (UTC).
     *          - stationECEF: Station position in ECEF coordinates (kilometers).
     *          - ra, dec    : Right ascension and declination in radians.
     *
     * @return StateVectors A struct containing:
     *          - epoch: The epoch corresponding to the second observation.
     *          - r    : Position vector at the second observation’s epoch (kilometers, ECI).
     *          - v    : Velocity vector at the second observation’s epoch (km/s, ECI).
     *
     * @throws std::invalid_argument If fewer than three observations are provided.
     * @throws std::runtime_error If no valid positive real root is found for the slant-range polynomial.
     *
     * @note All internal angle variables are assumed to be in radians. The gravitational
     *       parameter mu (mu) is assumed to be defined in orbmath namespace (km³/s²).
     */
    StateVectors gauss_solve(std::vector<Observation> &observations) {
        using namespace orbmath;

        // Ensure at least three observations are available
        if (observations.size() < 3) {
            throw std::invalid_argument("At least 3 observations expected");
        }
        Observation &obs1 = observations[0];
        Observation &obs2 = observations[1];
        Observation &obs3 = observations[2];

        // Convert epochs from days to seconds since J2000
        double t1 = obs1.epoch * SECONDS_PER_DAY;
        double t2 = obs2.epoch * SECONDS_PER_DAY;
        double t3 = obs3.epoch * SECONDS_PER_DAY;

        // Time intervals relative to the middle observation
        double tau1 = t1 - t2;
        double tau3 = t3 - t2;
        double tau = tau3 - tau1;

        // Convert observed RA/Dec to line-of-sight unit vectors
        auto L_hat_1 = radec_to_unit_vector(obs1.ra, obs1.dec);
        auto L_hat_2 = radec_to_unit_vector(obs2.ra, obs2.dec);
        auto L_hat_3 = radec_to_unit_vector(obs3.ra, obs3.dec);

        // Assemble L matrix whose columns are the unit direction vectors
        Eigen::Matrix3d L;
        L.col(0) = L_hat_1;
        L.col(1) = L_hat_2;
        L.col(2) = L_hat_3;

        // Convert station positions from ECEF to ECI at each observation epoch
        auto r_site_eci_1 = utils::to_eci(obs1.stationECEF, obs1.epoch);
        auto r_site_eci_2 = utils::to_eci(obs2.stationECEF, obs2.epoch);
        auto r_site_eci_3 = utils::to_eci(obs3.stationECEF, obs3.epoch);

        // Pack the site vectors into a 3×3 matrix
        Eigen::Matrix3d r_site_eci;
        r_site_eci << r_site_eci_1, r_site_eci_2, r_site_eci_3;

        // Compute Gauss coefficients a1, a3 and their time‐weighted variants
        double a1 = tau3 / tau;
        double a1_u = tau3 * (tau * tau - tau3 * tau3) / (6 * tau);
        double a3 = -tau1 / tau;
        double a3_u = -tau1 * (tau * tau - tau1 * tau1) / (6 * tau);

        // Invert L to solve for the scalar coefficients (M = L⁻¹ * r_site_eci)
        auto L_inv = L.inverse();
        auto M = L_inv * r_site_eci;

        // Intermediate scalar quantities for slant-range polynomial
        double C_scalar = L_hat_2.dot(r_site_eci_2);
        double d1 = M(1, 0) * a1 - M(1, 1) + M(1, 2) * a3;
        double d2 = a1_u * M(1, 0) + a3_u * M(1, 2);

        double d1_sq = d1 * d1;
        double r_site2_sq = r_site_eci_2.squaredNorm();

        // Coefficients for ninth‐degree polynomial: -C·ρ₂⁹ - B·ρ₂⁶ - A·ρ₂³ + 1 = 0
        double A = d1_sq + 2 * C_scalar * d1 + r_site2_sq;
        double B = 2 * mu * (C_scalar * d2 + d1 * d2);
        double C = mu * mu * d2 * d2;

        Eigen::VectorXd coeffs(9);
        coeffs << -C, 0, 0, -B, 0, 0, -A, 0, 1;

        // Solve the polynomial for real positive roots
        Eigen::PolynomialSolver<double, Eigen::Dynamic> solver;
        solver.compute(coeffs);
        std::vector<double> real_roots;
        solver.realRoots(real_roots);

        double r2_mag = -1;
        for (auto &root : real_roots) {
            if (root > 0) {
                r2_mag = root;
                break;
            }
        }

        if (r2_mag < 0) {
            throw std::runtime_error("No valid positive real root for r2 magnitude.");
        }

        // Compute gravitational acceleration factor at r2
        auto u = mu / std::pow(r2_mag, 3);

        // Compute scalar factors c1, c2, c3 for slant-range estimation
        double c1 = (a1 + a1_u * u);
        double c2 = -1.0;
        double c3 = (a3 + a3_u * u);

        // Solve for slant-range vector ρ = [ρ1, ρ2, ρ3]
        Eigen::Vector3d rhs(-c1, -c2, -c3);
        Eigen::Vector3d rho_vec = M * rhs;

        double rho1 = rho_vec[0] / c1;
        double rho2 = rho_vec[1] / c2;
        double rho3 = rho_vec[2] / c3;

        // Compute position vectors in ECI at each observation
        auto r1 = rho1 * L_hat_1 + r_site_eci_1;
        auto r2 = rho2 * L_hat_2 + r_site_eci_2;
        auto r3 = rho3 * L_hat_3 + r_site_eci_3;

        // Apply Gibbs method to estimate velocity at r2
        auto Z12 = r1.cross(r2);
        auto Z31 = r3.cross(r1);
        auto Z23 = r2.cross(r3);

        auto N_gibbs = r1.norm() * Z23 + r2.norm() * Z31 + r3.norm() * Z12;
        auto D_gibbs = Z12 + Z23 + Z31;
        auto S_gibbs = (r2.norm() - r3.norm()) * r1
                     + (r3.norm() - r1.norm()) * r2
                     + (r1.norm() - r2.norm()) * r3;
        auto B_gibbs = D_gibbs.cross(r2);

        auto L_g  = std::sqrt(mu / (N_gibbs.dot(D_gibbs)));
        auto v2   = (L_g / r2.norm()) * B_gibbs + L_g * S_gibbs;

        // Prepare and return solution struct
        StateVectors sol;
        sol.epoch = observations[1].epoch;
        sol.r     = r2;
        sol.v     = v2;

        return sol;
    }

    /**
     * @brief Construct a RADec solver given a set of observations.
     *
     * Stores the provided observations for later use in computing the orbit.
     * Does not perform computation until get_position() or get_velocity() is called.
     *
     * @param observations A vector of Observation structs. Must contain at least three entries.
     */
    RADec::RADec(const std::vector<Observation> &observations)
        : m_observations(observations), m_computed(false) {
    }

    /**
     * @brief Retrieve the computed satellite position in ECI coordinates.
     *
     * If the orbit has not yet been computed, this method triggers computation
     * via compute_orbit(). The returned vector is in kilometers.
     *
     * @return Eigen::Vector3d Position vector [x, y, z] in kilometers (ECI).
     */
    Eigen::Vector3d RADec::get_position() const {
        if (!m_computed) {
            const_cast<RADec *>(this)->compute_orbit();
        }
        return m_position;
    }

    /**
     * @brief Retrieve the computed satellite velocity in ECI coordinates.
     *
     * If the orbit has not yet been computed, this method triggers computation
     * via compute_orbit(). The returned vector is in kilometers per second.
     *
     * @return Eigen::Vector3d Velocity vector [vx, vy, vz] in km/s (ECI).
     */
    Eigen::Vector3d RADec::get_velocity() const {
        if (!m_computed) {
            const_cast<RADec *>(this)->compute_orbit();
        }
        return m_velocity;
    }

    /**
     * @brief Compute the orbit (position and velocity) using provided observations.
     *
     * Internally calls gauss_solve() with the stored observations to determine
     * the satellite state vectors at the second observation’s epoch. Sets m_position,
     * m_velocity, and m_epoch accordingly, and marks the orbit as computed.
     */
    void RADec::compute_orbit() {
        m_epoch = m_observations[1].epoch;
        StateVectors sol = gauss_solve(m_observations);

        m_position  = sol.r;
        m_velocity  = sol.v;
        m_computed  = true;
    }

} // namespace interpret
