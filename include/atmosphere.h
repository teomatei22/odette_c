#ifndef ATMOSPHERE_H
#define ATMOSPHERE_H

// Standard library includes for math functions and algorithms
#include <cmath>
#include <algorithm>
#include <Dense>

/*
    ATMOSPHERE calculates density for altitudes from sea level
    through 1000 km using exponential interpolation.
*/

// Namespace for orbital mathematics and perturbation models
namespace orbmath::perturbation {

    /**
     * @brief Computes the atmospheric density for a given altitude using exponential interpolation.
     *
     * This inline function takes an altitude in kilometers, clamps it within a supported range,
     * and then uses pre-defined base altitudes, nominal densities, and scale heights to calculate
     * the density using an exponential decay formula. If the altitude exceeds the highest base value,
     * it extrapolates using the last available data.
     *
     * @param z_km Altitude in kilometers.
     * @return double The atmospheric density in kg/m^3 at the specified altitude.
     */
    inline double atmosphere(double z_km)
    {
        // Clamp the altitude to the supported range: minimum 0 km, maximum 1500 km.
        z_km = std::clamp(z_km, 0.0, 1500.0);

        // Base altitudes (in km) from sea level for which density data is provided.
        static constexpr double h[] = {
            0, 25, 30, 40, 50, 60, 70, 80, 90, 100,
            110, 120, 130, 140, 150, 180, 200, 250, 300, 350,
            400, 450, 500, 600, 700, 800, 900, 1000
        };

        // Nominal densities (in kg/m^3) corresponding to the altitudes in h[].
        static constexpr double rho[] = {
            1.225, 3.899e-2, 1.774e-2, 3.972e-3, 1.057e-3,
            3.206e-4, 8.770e-5, 1.905e-5, 3.396e-6, 5.297e-7,
            9.661e-8, 2.438e-8, 8.484e-9, 3.845e-9, 2.070e-9,
            5.464e-10, 2.789e-10, 7.248e-11, 2.418e-11, 9.518e-12,
            3.725e-12, 1.585e-12, 6.967e-13, 1.454e-13, 3.614e-14,
            1.170e-14, 5.245e-15, 3.019e-15
        };

        // Scale heights (in km) for each layer, used in the exponential density model.
        static constexpr double H[] = {
            7.249, 6.349, 6.682, 7.554, 8.382,
            7.714, 6.549, 5.799, 5.382, 5.877,
            7.263, 9.473, 12.636, 16.149, 22.523,
            29.740, 37.105, 45.546, 53.628, 53.298,
            58.515, 60.828, 63.822, 71.835, 88.667,
            124.640, 181.050, 268.000
        };

        // Initialize an index for finding the right interpolation segment.
        int i = 0;
        // Determine the number of elements in the altitude table.
        const int n = sizeof(h) / sizeof(h[0]);

        // Loop through the altitude intervals to find the correct segment for z_km.
        for (int j = 0; j < n - 1; ++j) {
            // Identify the interval in which the given altitude lies.
            if (z_km >= h[j] && z_km < h[j + 1]) {
                i = j;  // Set the index to the current interval.
                break;  // Exit loop once the correct interval is found.
            }
        }

        // Special handling for altitudes that are at or beyond the highest table entry.
        // If z_km is greater than or equal to the highest defined altitude,
        // use the last available density and scale height for extrapolation.
        if (z_km >= h[n - 1]) {
            const double h0 = h[n - 1];
            const double rho0 = rho[n - 1];
            const double H0 = H[n - 1];
            return rho0 * std::exp(-(z_km - h0) / H0);
        }

        // Apply exponential interpolation within the current layer.
        // The density is decayed exponentially based on the altitude difference.
        return rho[i] * std::exp(-(z_km - h[i]) / H[i]);
    }

} // End of namespace orbmath::perturbation

#endif // ATMOSPHERE_H
