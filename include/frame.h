#ifndef FRAME_H
#define FRAME_H

// -----------------------------------------------------------------------------
// FRAME_H
// This header defines functions for transforming position vectors between
// the Earth-Centered Inertial (ECI) and Earth-Centered Earth-Fixed (ECEF)
// coordinate systems using astronomical corrections including precession,
// nutation, sidereal time, and polar motion.
// -----------------------------------------------------------------------------

#include <Dense>  // Include Eigen library for matrix and vector operations

#include "iers_coef.h"  // Provides IERS coefficients required for time and rotation corrections.
#include "orbmath.h"   // Contains orbital math functions such as precession, nutation, etc.

namespace utils {
    // Define type aliases for 3D vectors in specific coordinate frames:
    typedef Eigen::Vector3d ECI;   // ECI: Earth-Centered Inertial coordinate vector
    typedef Eigen::Vector3d ECEF;  // ECEF: Earth-Centered Earth-Fixed coordinate vector

    /**
     * @brief Converts an ECEF position vector to an ECI position vector.
     *
     * The conversion applies a series of corrections including precession, nutation,
     * sidereal rotation, and polar motion based on the provided epoch. The transformations
     * are performed using a series of matrix multiplications that adjust for Earth's rotation
     * and temporal effects.
     *
     * @param r_ecef Input position vector in the ECEF frame.
     * @param epoch Epoch time used to compute the necessary corrections.
     * @return ECI The transformed position vector in the ECI frame.
     */
    inline ECI to_eci(const ECEF &r_ecef, double epoch) {
        // Bring nutation functions and variables into scope.
        using namespace orbmath::nutation;

        // Retrieve necessary correction constants for the given epoch.
        // Returns values such as dUT1 (UT1-UTC difference), dAT (leap seconds correction),
        // xp, yp (polar motion components), lod (length of day), and nutation corrections (ddpsi, ddeps).
        auto [dUT1, dAT, xp, yp, lod, ddpsi, ddeps] = get_constants(epoch);

        // Define the base UTC time.
        auto jdUTC = epoch;
        // Calculate UT1 time by correcting UTC with dUT1 (converted from seconds to days).
        double jdUT1 = jdUTC + dUT1 / 86400.0;
        // Calculate Terrestrial Time (TT) using dAT and the 32.184 second offset (converted to days).
        double jdTT = jdUTC + ((dAT + 32.184) / 86400.0);
        // Compute Julian centuries since J2000.0, a standard epoch used in astronomical calculations.
        double ttt = (jdTT - 2451545.0) / 36525.0;

        // Compute the precession matrix which models the long-term change in Earth's rotation axis.
        Eigen::Matrix3d prec = precession(ttt);

        // Compute the nutation corrections which represent short-term periodic variations in Earth's rotation.
        NutationOutput nut = nutation(ttt, ddpsi, ddeps);

        // Calculate the sidereal time rotation matrix based on UT1, LOD, and nutation corrections.
        // 'eqeterms' likely represents additional equinox-related corrections.
        Eigen::Matrix3d st = sidereal(jdUT1, lod, nut.deltapsi, nut.meaneps,
                                      nut.omega, eqeterms);

        // Obtain the polar motion matrix to correct for deviations in Earth's rotation axis.
        Eigen::Matrix3d pm = polar_motion(xp, yp);

        // Apply the polar motion correction to convert the ECEF vector to a pseudo Earth-fixed frame (PEF).
        Eigen::Vector3d r_pef = pm * r_ecef;
        // Apply the sidereal, nutation, and precession rotations sequentially to convert PEF to ECI.
        Eigen::Vector3d r_eci = prec * (nut.nut_matrix * (st * r_pef));

        // Return the converted position vector in the ECI frame.
        return r_eci;
    }

    /**
     * @brief Converts an ECI position vector to an ECEF position vector.
     *
     * This function applies the inverse transformations of the ECI-to-ECEF conversion,
     * effectively reversing the precession, nutation, and sidereal time transformations
     * along with the polar motion correction. All correction parameters are computed
     * based on the provided epoch.
     *
     * @param r_eci Input position vector in the ECI frame.
     * @param epoch Epoch time used to compute the necessary corrections.
     * @return ECEF The transformed position vector in the ECEF frame.
     */
    inline ECEF to_ecef(const ECI &r_eci, double epoch) {
        // Bring nutation-related functions and constants into scope.
        using namespace orbmath::nutation;

        // Retrieve the required correction constants for the given epoch.
        auto [dUT1, dAT, xp, yp, lod, ddpsi, ddeps] = get_constants(epoch);

        // Define the base UTC time.
        auto jdUTC = epoch;
        // Calculate UT1 time by applying the dUT1 correction.
        double jdUT1 = jdUTC + dUT1 / 86400.0;
        // Calculate Terrestrial Time (TT) applying dAT and the 32.184 second offset.
        double jdTT = jdUTC + ((dAT + 32.184) / 86400.0);
        // Compute the time in Julian centuries since J2000.0 for the transformation.
        double ttt = (jdTT - 2451545.0) / 36525.0;

        // Compute the precession matrix for reversing long-term rotational adjustments.
        Eigen::Matrix3d prec = precession(ttt);
        // Calculate the nutation corrections to account for short-term periodic variations.
        NutationOutput nut = nutation(ttt, ddpsi, ddeps);
        // Determine the sidereal time matrix using UT1 and LOD along with nutation values.
        Eigen::Matrix3d st = sidereal(jdUT1, lod, nut.deltapsi, nut.meaneps,
                                      nut.omega, eqeterms);
        // Compute the polar motion matrix for correcting Earth's rotation axis deviations.
        Eigen::Matrix3d pm = polar_motion(xp, yp);
        // Reverse the precession, nutation, and sidereal transformations to obtain the PEF vector.
        Eigen::Vector3d r_pef = st.inverse() * (nut.nut_matrix.inverse() * (prec.inverse() * r_eci));
        // Apply the inverse of the polar motion correction to convert PEF back to ECEF.
        Eigen::Vector3d r_ecef = pm.inverse() * r_pef;

        // Return the final converted position vector in the ECEF frame.
        return r_ecef;
    }
}

#endif
