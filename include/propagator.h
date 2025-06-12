#ifndef PROPAGATOR_H
#define PROPAGATOR_H

#include <Dense>         // Eigen vector/matrix operations
#include <vector>        // STL vector for storing ephemeris
#include <iostream>      // For potential debugging/logging
#include "orbmath.h"     // Common orbital math utilities
#include "orbmath_perturbation.h"  // Perturbation models (J2, drag, etc.)

namespace propagate {

    /// @brief Stores position, velocity, and epoch history for a propagated orbit.
    struct Ephemeris {
        std::vector<Eigen::Vector3d> positions;  // Position vectors (km)
        std::vector<Eigen::Vector3d> velocities; // Velocity vectors (km/s)
        std::vector<double> epochs;              // Time steps (Julian Days or fractional days)
    };

    /// @brief Main propagator class to evolve orbital states using numerical integration.
    class Propagator {
    public:
        Eigen::Vector3d r, v;   // Current state vectors
        std::vector<double> epochs; // List of epochs to propagate through

        /// Function pointer to an integration method: takes propagator state + index → new r, v
        std::function<std::tuple<Eigen::Vector3d,Eigen::Vector3d>(Propagator&, std::size_t)> integrator;

        Ephemeris ephem;  // Stores the complete propagation history

        std::size_t perturbations = 0;  // Optional: not used explicitly but can indicate model set

        // Flags to toggle physical perturbations
        bool j2 = true;
        bool tb = true;
        bool solar = true;
        bool atm_exp = true;

        // Default constructor
        Propagator() : r(Eigen::Vector3d::Zero()), v(Eigen::Vector3d::Zero()) {}

        /// @brief Construct with initial conditions and integrator
        Propagator(const Eigen::Vector3d& r, const Eigen::Vector3d& v, const std::vector<double>& epochs,
                   const std::function<std::tuple<Eigen::Vector3d,Eigen::Vector3d>(Propagator&, std::size_t)>& integrator,
                   std::size_t perturbations=0)
            : r(r), v(v), epochs(epochs), integrator(integrator), perturbations(perturbations) {}

        /// @brief Perform propagation using selected integrator and store result in ephemeris
        void compute();
    };
}


namespace propagate::integrators {

    //-----------------------------------------------------------------
    // Velocity Verlet integrator
    //-----------------------------------------------------------------
    /// @brief Verlet integrator for orbit propagation using fixed time step.
    /// @param pr Propagator state at current step
    /// @param i  Index in the epoch vector
    /// @return Tuple of (new position, new velocity)
    inline std::tuple<Eigen::Vector3d, Eigen::Vector3d>
    verlet(Propagator& pr, double i) {
        auto r = pr.ephem.positions.back();     // Current position
        auto v = pr.ephem.velocities.back();    // Current velocity
        auto dt = pr.epochs[i+1] - pr.epochs[i]; // Time step (in days)
        dt = dt * orbmath::SECONDS_PER_DAY;     // Convert to seconds

        auto a = orbmath::kepler(r, i);         // Initial acceleration (assumed Keplerian)
        auto v_half = v + 0.5 * a * dt;         // Velocity at half-step
        auto r_new = r + v_half*dt;             // Full step position update
        auto a_new = orbmath::kepler(r_new, dt); // New acceleration from updated position
        auto v_new = v_half + 0.5 * a_new * dt; // Full step velocity update
        return std::make_tuple(r_new, v_new);   // Return updated state
    };

    //-----------------------------------------------------------------
    // Runge-Kutta-Fehlberg (RK45) Integrator
    //-----------------------------------------------------------------
    /// @brief 4th-order RK45 integrator with optional perturbation forces.
    /// @param pr Propagator instance
    /// @param i  Current index in epoch list
    /// @return Tuple of updated position and velocity vectors
    inline std::tuple<Eigen::Vector3d, Eigen::Vector3d>
    rk45_eci(Propagator& pr, double i) {
        using namespace orbmath;

        // Initial state and time
        const Eigen::Vector3d r0 = pr.ephem.positions.back();
        const Eigen::Vector3d v0 = pr.ephem.velocities.back();
        const double t0 = pr.epochs[i] * SECONDS_PER_DAY;
        const double t1 = pr.epochs[i+1] * SECONDS_PER_DAY;
        const double dt = t1 - t0;

        // Acceleration lambda capturing all perturbations
        auto acceleration = [&](const Eigen::Vector3d &r, const Eigen::Vector3d &v, double t_sec) -> Eigen::Vector3d {
            auto a_kep = kepler(r, t_sec); // Central body

            // Add optional perturbation forces
            if (pr.j2)    a_kep += orbmath::perturbation::J2_perturbation(r);
            if (pr.tb)    a_kep += orbmath::perturbation::third_body(r, t_sec);
            if (pr.solar) a_kep += orbmath::perturbation::solar_radiation(r, t_sec);
            if (pr.atm_exp) a_kep += orbmath::perturbation::atmospheric_drag_exponential(r, v);

            return a_kep;
        };

        // RK45 coefficients
        Eigen::Vector3d k1_v = acceleration(r0, v0, t0);
        Eigen::Vector3d k1_r = v0;

        Eigen::Vector3d k2_v = acceleration(r0 + 0.25*dt*k1_r, v0 + 0.25*dt*k1_v, t0 + 0.25*dt);
        Eigen::Vector3d k2_r = v0 + 0.25*dt*k1_v;

        Eigen::Vector3d k3_v = acceleration(r0 + (3.0/32)*dt*k1_r + (9.0/32)*dt*k2_r,
                                            v0 + (3.0/32)*dt*k1_v + (9.0/32)*dt*k2_v, t0 + 3.0/8*dt);
        Eigen::Vector3d k3_r = v0 + (3.0/32)*dt*k1_v + (9.0/32)*dt*k2_v;

        Eigen::Vector3d k4_v = acceleration(r0 + (1932.0/2197)*dt*k1_r - (7200.0/2197)*dt*k2_r + (7296.0/2197)*dt*k3_r,
                                            v0 + (1932.0/2197)*dt*k1_v - (7200.0/2197)*dt*k2_v + (7296.0/2197)*dt*k3_v, t0 + 12.0/13*dt);
        Eigen::Vector3d k4_r = v0 + (1932.0/2197)*dt*k1_v - (7200.0/2197)*dt*k2_v + (7296.0/2197)*dt*k3_v;

        Eigen::Vector3d k5_v = acceleration(r0 + (439.0/216)*dt*k1_r - 8.0*dt*k2_r + (3680.0/513)*dt*k3_r - (845.0/4104)*dt*k4_r,
                                            v0 + (439.0/216)*dt*k1_v - 8.0*dt*k2_v + (3680.0/513)*dt*k3_v - (845.0/4104)*dt*k4_v, t0 + dt);
        Eigen::Vector3d k5_r = v0 + (439.0/216)*dt*k1_v - 8.0*dt*k2_v + (3680.0/513)*dt*k3_v - (845.0/4104)*dt*k4_v;

        // Final 4th-order Runge-Kutta state update
        Eigen::Vector3d r_new = r0 + dt * (25.0/216*k1_r + 1408.0/2565*k3_r + 2197.0/4104*k4_r - 1.0/5*k5_r);
        Eigen::Vector3d v_new = v0 + dt * (25.0/216*k1_v + 1408.0/2565*k3_v + 2197.0/4104*k4_v - 1.0/5*k5_v);

        return std::make_tuple(r_new, v_new); // Return new state
    }

}

#endif