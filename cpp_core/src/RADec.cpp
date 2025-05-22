#include "interpret.h"
#include <iostream>
#include <Eigen/Dense>
#include <cmath>
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
    Eigen::Vector3d radec_to_unit_vector(double ra, double dec) {
        return Eigen::Vector3d(std::cos(dec) * std::cos(ra),
                               std::cos(dec) * std::sin(ra),
                               std::sin(dec));
    }

    StateVectors gauss_solve(std::vector<Observation> &observations) {
        using namespace orbmath;

        //setting epoch

        // Ensure we have at least 3 observations
        if (observations.size() < 3)
            throw std::invalid_argument("At least 3 observations expected");
        Observation &obs1 = observations[0];
        Observation &obs2 = observations[1];
        Observation &obs3 = observations[2];

        double t1 = obs1.epoch * SECONDS_PER_DAY;
        double t2 = obs2.epoch * SECONDS_PER_DAY;
        double t3 = obs3.epoch * SECONDS_PER_DAY;

        double tau1 = t1 - t2;  // -480 s
        double tau3 = t3 - t2;  // +240 s
        double tau = tau3 - tau1;

        auto L_hat_1 = radec_to_unit_vector(obs1.ra, obs1.dec);
        auto L_hat_2 = radec_to_unit_vector(obs2.ra, obs2.dec);
        auto L_hat_3 = radec_to_unit_vector(obs3.ra, obs3.dec);

        Eigen::Matrix3d L;        //unitless
        L.col(0) = L_hat_1;
        L.col(1) = L_hat_2;
        L.col(2) = L_hat_3;

        auto r_site_eci_1 = utils::to_eci(obs1.stationECEF, obs1.epoch);
        auto r_site_eci_2 = utils::to_eci(obs2.stationECEF, obs2.epoch);
        auto r_site_eci_3 = utils::to_eci(obs3.stationECEF, obs3.epoch);

        Eigen::Vector3d r_site_1 = r_site_eci_1; // eci
        Eigen::Vector3d r_site_2 = r_site_eci_2;
        Eigen::Vector3d r_site_3 = r_site_eci_3;


        Eigen::Matrix3d r_site_eci;
        r_site_eci << r_site_eci_1, r_site_eci_2, r_site_eci_3;

        auto a1 = tau3 / tau;
        auto a1_u = tau3*(tau*tau - tau3*tau3) / (6*tau); // s^2

        auto a3 = -tau1 / tau;
        auto a3_u = -tau1 * (tau*tau - tau1*tau1) / (6 * tau); //s^2

        auto L_inv = L.inverse();

        auto M = L_inv * r_site_eci;

        auto d1 = M(1,0) * a1 - M(1,1) + M(1,2) * a3; // km
        auto d2 = a1_u * M(1,0) + a3_u * M(1,2); // km * s ^ 2

        double C_scalar = L_hat_2.dot(r_site_2); // dot product: unitless ⋅ km = km
        double d1_sq = d1 * d1;
        double r_site2_sq = r_site_2.squaredNorm();

        double A = d1_sq + 2 * C_scalar * d1 + r_site2_sq;
        double B = 2 * mu * (C_scalar * d2 + d1 * d2);
        double C = mu * mu * d2 * d2;

        Eigen::VectorXd coeffs(9);
        coeffs << -C, 0, 0, -B, 0, 0, -A, 0, 1;
        Eigen::PolynomialSolver<double, Eigen::Dynamic> solver;
        solver.compute(coeffs);
        std::vector<double> real_roots;
        solver.realRoots( real_roots );

        double r2_mag = -1;
        for (auto & root : real_roots) {
            if (root > 0) {
                r2_mag = root;
                break;
            }
        }

        if (r2_mag < 0) {
            throw std::runtime_error("No valid positive real root for r2 magnitude.");
        }

        auto u = mu / pow(r2_mag, 3); // sec ^ -2

        // Compute correct c_i (no flipping needed)
        double c1 = (a1 + a1_u * u);
        double c2 = -1.0;
        double c3 = (a3 + a3_u * u);

        // Form RHS vector of Gauss system
        Eigen::Vector3d rhs(-c1, -c2, -c3);  // right-hand side of M * rho = -c
        Eigen::Vector3d rho_vec = M * rhs;

        double rho1 = rho_vec[0] / c1;
        double rho2 = rho_vec[1] / c2;
        double rho3 = rho_vec[2] / c3;

        auto r1 = rho1 * L_hat_1 + r_site_1;
        auto r2 = rho2 * L_hat_2 + r_site_2;
        auto r3 = rho3 * L_hat_3 + r_site_3;

        auto Z12 = r1.cross(r2);
        auto Z31 = r3.cross(r1);
        auto Z23 = r2.cross(r3);

        auto N_gibbs = r1.norm() * Z23 + r2.norm() * Z31 + r3.norm() * Z12; //km ^ 3
        auto D_gibbs = Z12 + Z23 + Z31; // km ^ 2
        auto S_gibbs = (r2.norm() - r3.norm()) * r1 + (r3.norm()
                    - r1.norm()) * r2 + (r1.norm()-r2.norm()) * r3;
        auto B_gibbs = D_gibbs.cross(r2);

        auto L_g = sqrt(mu/(N_gibbs.dot(D_gibbs)));

        auto v2 = (L_g / r2.norm())* B_gibbs + L_g * S_gibbs;

        StateVectors sol;
        sol.epoch = observations[1].epoch;
        sol.r = r2;
        sol.v = v2;
        return sol;

    }


    RADec::RADec(const std::vector<Observation> &observations)
        : m_observations(observations), m_computed(false) {
    }

    Eigen::Vector3d RADec::get_position() const {
        if (!m_computed) {
            const_cast<RADec *>(this)->compute_orbit();
        }
        return m_position; // returns position in kilometers
    }

    Eigen::Vector3d RADec::get_velocity() const {
        if (!m_computed) {
            const_cast<RADec *>(this)->compute_orbit();
        }
        return m_velocity; // returns velocity in kilometers per second
    }

    void RADec::compute_orbit() {
        m_epoch = m_observations[1].epoch;
        StateVectors sol = gauss_solve(m_observations);

        m_position = sol.r;
        m_velocity = sol.v;
        m_computed = true;
    }
} // namespace interpret
