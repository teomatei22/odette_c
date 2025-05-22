#include "propagator.h"

void propagate::Propagator::compute() {
    ephem.positions.push_back(this->r);
    ephem.velocities.push_back(this->v);
    ephem.epochs.push_back(this->epochs[0]);


    for (std::size_t i = 0; i < this->epochs.size()-1; ++i) {
        auto [r_1, v_1] = this->integrator(*this, i);

        ephem.positions.push_back(r_1);
        ephem.velocities.push_back(v_1);
        ephem.epochs.push_back(this->epochs[i+1]);
    }
}