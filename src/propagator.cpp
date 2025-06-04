#include "propagator.h"

#include "logging.h"

namespace propagate {

    /**
     * @brief Perform orbital propagation over the configured epochs.
     *
     * This method initializes the ephemeris by recording the initial position,
     * velocity, and epoch. It then iterates over the sequence of future epochs,
     * using the configured integrator to compute the next position and velocity
     * at each epoch. The results are stored in the `ephem` member, which contains
     * vectors of positions, velocities, and corresponding epoch times.
     *
     * @note The integrator function is expected to accept a reference to this
     *       Propagator object and the index of the current epoch, and return a
     *       std::pair containing the next position and velocity vectors.
     */
    void Propagator::compute() {
        barlog::info("Propagating orbit!");

        // Record initial state
        ephem.positions.push_back(this->r);
        ephem.velocities.push_back(this->v);
        ephem.epochs.push_back(this->epochs[0]);

        // Propagate through each subsequent epoch
        for (std::size_t i = 0; i < this->epochs.size() - 1; ++i) {
            auto [r_1, v_1] = this->integrator(*this, i);

            ephem.positions.push_back(r_1);
            ephem.velocities.push_back(v_1);
            ephem.epochs.push_back(this->epochs[i + 1]);
        }
    }

} // namespace propagate
