//
// Created by croi on 4/12/2025.
//

#ifndef ORBMATH_NUTATION_H
#define ORBMATH_NUTATION_H

#include <cmath>       // Provides mathematical functions (sin, cos, fmod, etc.)
#include <Dense>       // For Eigen types used in matrix and vector operations.
#include "orbmath.h"   // Provides common orbital math utilities (e.g., deg2rad, wrap_2pi).

// -----------------------------------------------------------------------------
// Namespace: orbmath::nutation
// This namespace encapsulates functions and data for calculating nutation
// effects as defined by the IAU-1980 model. Nutation is the oscillation in the
// Earth's rotation axis and affects celestial coordinate transformations.
// -----------------------------------------------------------------------------
namespace orbmath {
    namespace nutation {

        // -----------------------------------------------------------------------------
        // EMBEDDED IAU-1980 NUTATION COEFFICIENTS
        // Exactly as used in the "nut80.dat" from Vallado (each row has 9 columns):
        //   First 5 integer columns -> iar80[i][*]
        //   Next 4 real columns    -> rar80[i][*]
        // The Java code then divides the last 4 columns by 10000 and converts arcsec->rad
        // in the function. We'll do exactly the same steps below.
        // -----------------------------------------------------------------------------

        // Define the number of nutation terms provided in the dataset.
        static const int NUT_TERMS = 106;

        // -------------------------------------------------------------------------
        // iar80_data: 2D array of 106 rows and 5 columns of integer multipliers.
        // These multipliers relate to the fundamental arguments (l, l1, F, D, Omega)
        // used in the nutation calculation.
        // -------------------------------------------------------------------------
        static const int iar80_data[NUT_TERMS][5] = {
            {0, 0, 0, 0, 1}, {-2, 0, 2, 0, 2}, {0, 0, 2, -2, 2},
            {0, 0, 2, 0, 2}, {0, 1, 0, 0, 0}, {0, 0, 0, 2, 0},
            {-2, 1, 2, 0, 2}, {0, 0, 2, 2, 2}, {0, 1, 0, 0, 1},
            {-2, -1, 2, 0, 2}, {-2, 0, 2, 2, 2}, {0, -1, 2, 0, 2},
            {0, 0, 2, -2, 1}, {2, 0, 2, 0, 2}, {0, 0, 2, 2, 1},
            {2, 0, 2, 0, 1}, {2, 0, 0, 0, 0}, {0, 0, 2, 0, 0},
            {-2, 0, 2, 0, 1}, {0, 0, 0, 0, 2}, {2, 0, 2, -2, 2},
            {0, 0, 2, -2, 0}, {0, 1, 2, 0, 2}, {-2, 1, 0, 0, 0},
            {0, 0, 0, 2, 1}, {2, 1, 2, 0, 2}, {0, -1, 2, 0, 1},
            {0, 1, 0, -2, 0}, {-2, 0, 0, 2, 0}, {0, 1, 2, -2, 2},
            {2, -1, 2, 0, 2}, {2, 0, 2, 0, 0}, {2, -1, 2, 0, 1},
            {0, 1, 2, 2, 2}, {-2, 1, 2, 0, 1}, {0, 0, 2, 2, 0},
            {-2, 0, 2, 2, 2}, {-2, 0, 2, 0, 0}, {0, 0, 0, 2, 2},
            {-2, 0, 2, 2, 1}, {2, 0, 0, 2, 0}, {-2, 1, 2, 2, 2},
            {0, 1, 0, 2, 0}, {-2, 1, 2, 0, 0}, {0, -1, 2, 2, 2},
            {2, -1, 0, 2, 0}, {0, 0, 2, 1, 2}, {-2, 0, 2, 1, 2},
            {0, 0, 2, -1, 2}, {0, 2, 0, 0, 0}, {2, 0, 2, -1, 2},
            {-2, 1, 0, 2, 0}, {0, 1, 2, -1, 2}, {-1, 0, 2, 0, 2},
            {0, 1, 0, 1, 0}, {-1, -1, 2, 2, 2}, {0, 1, 0, -1, 0},
            {2, 0, -2, 0, 0}, {1, 1, 2, -2, 2}, {0, 1, -2, 2, 0},
            {0, 1, 2, 0, 1}, {-2, 1, 2, -2, 2}, {0, 1, -2, 0, 1},
            {0, 0, 2, 2, 2}, {0, 1, 2, -2, 1}, {1, 0, 0, 0, 0},
            {0, 1, 0, 2, 1}, {3, 0, 2, -2, 2}, {1, 0, 2, 0, 2},
            {-1, 0, 2, 2, 2}, {0, 0, 0, 2, 1}, {2, 0, 2, 0, 1},
            {1, 0, 2, -2, 2}, {3, 0, 2, 0, 2}, {-2, 0, 2, 0, 1},
            {1, 0, 2, 0, 1}, {-3, 0, 2, 0, 2}, {-2, -1, 2, 2, 2},
            {0, 2, 2, 0, 2}, {0, 2, 2, -2, 2}, {-1, 0, 2, 0, 1},
            {0, 1, -2, 2, 1}, {-1, -1, 2, 0, 2}, {0, 0, 0, 1, 0},
            {-2, 0, 0, 2, 1}, {2, 0, -2, 0, 1}, {0, -1, 2, 0, 2},
            {0, 0, 0, 1, 1}, {2, 0, 0, -2, 1}, {0, 0, 2, -1, 2},
            {0, 1, 0, 0, 1}, {-1, 0, 2, 2, 2}, {2, 0, 0, 1, 0},
            {1, 0, 0, 0, 1}, {3, 0, 0, 0, 0}, {0, 0, 2, 1, 2},
            {-1, 0, 2, 0, 2}, {1, 0, 2, -2, 2}, {3, 0, 2, -2, 2},
            {-2, 0, 2, 2, 2}, {-1, 0, 2, 2, 2}, {0, 1, 2, 0, 2}
        };

        // -------------------------------------------------------------------------
        // rar80_data: 2D array of 106 rows and 4 columns of real numbers.
        // Each number is given in units of 0.0001 arcseconds (i.e. must be scaled).
        // These values represent the amplitudes for the sine and cosine terms in the
        // nutation calculation for Δψ and Δε.
        // -------------------------------------------------------------------------
        static const double rar80_data[NUT_TERMS][4] = {
            {-72574, 0, 21881, 0}, {2175, 0, -95, 0},
            {712, 0, -7, 0}, {-386, 0, 6, 0},
            {-46, 0, 0, 0}, {127, 0, -1, 0},
            {61, 0, -2, 0}, {-42, 0, 0, 0},
            {-41, 0, 26, 0}, {-25, 0, 0, 0},
            {-22, 0, 0, 0}, {21, 0, -1, 0},
            {17, 0, 0, 0}, {-16, 0, 1, 0},
            {-13, 0, 0, 0}, {-12, 0, 0, 0},
            {11, 0, 0, 0}, {-11, 0, 0, 0},
            {-6, 0, 3, 0}, {-3, 0, 0, 0},
            {-3, 0, 1, 0}, {3, 0, 0, 0},
            {-2, 0, 1, 0}, {2, 0, 0, 0},
            {2, 0, 0, 0}, {2, 0, -1, 0},
            {1, 0, 0, 0}, {1, 0, 0, 0},
            {1, 0, -1, 0}, {1, 0, 0, 0},
            {-1, 0, 0, 0}, {1, 0, 0, 0},
            {-1, 0, 1, 0}, {1, 0, 0, 0},
            {1, 0, 0, 0}, {-1, 0, 1, 0},
            {1, 0, 0, 0}, {-1, 0, 1, 0},
            {1, 0, 0, 0}, {1, 0, 0, 0},
            {-1, 0, 1, 0}, {1, 0, 0, 0},
            {-1, 0, 1, 0}, {1, 0, 0, 0},
            {-1, 0, 1, 0}, {1, 0, 0, 0},
            {1, 0, 0, 0}, {-1, 0, 1, 0},
            {-1, 0, 1, 0}, {-1, 0, 1, 0},
            {1, 0, 0, 0}, {1, 0, 0, 0},
            {1, 0, 0, 0}, {-1, 0, 1, 0},
            {1, 0, 0, 0}, {-1, 0, 1, 0},
            {1, 0, 0, 0}, {1, 0, 0, 0},
            {-1, 0, 1, 0}, {1, 0, 0, 0},
            {1, 0, 0, 0}, {-1, 0, 1, 0},
            {1, 0, 0, 0}, {1, 0, 0, 0},
            {1, 0, 0, 0}, {-1, 0, 1, 0},
            {1, 0, 0, 0}, {1, 0, 0, 0},
            {1, 0, 0, 0}, {1, 0, 0, 0},
            {-1, 0, 1, 0}, {1, 0, 0, 0},
            {1, 0, 0, 0}, {1, 0, 0, 0},
            {-1, 0, 1, 0}, {1, 0, 0, 0},
            {1, 0, 0, 0}, {-1, 0, 1, 0},
            {-1, 0, 1, 0}, {1, 0, 0, 0},
            {-1, 0, 1, 0}, {1, 0, 0, 0},
            {-1, 0, 1, 0}, {1, 0, 0, 0},
            {1, 0, 0, 0}, {1, 0, 0, 0},
            {1, 0, 0, 0}, {-1, 0, 1, 0}
        };
        // Note: The amplitudes in rar80_data are originally in units of 0.0001 arcsec.
        // They will later be scaled and converted to radians.

        // -----------------------------------------------------------------------------
        // UTILITY FUNCTIONS
        // -----------------------------------------------------------------------------

        // -----------------------------------------------------------------------------
        // cross()
        // Computes the cross product of two 3D vectors using Eigen's built-in function.
        // -----------------------------------------------------------------------------
        static Eigen::Vector3d cross(const Eigen::Vector3d &a,
                                     const Eigen::Vector3d &b) {
            return a.cross(b);
        }

        // -----------------------------------------------------------------------------
        //  1) POLAR MOTION: Converts polar motion parameters (in arcseconds) to a rotation
        //     matrix for transforming from the ECEF frame to the PEF (Pseudo Earth Fixed)
        //     frame.
        // -----------------------------------------------------------------------------
        static Eigen::Matrix3d polar_motion(double xp_arcsec, double yp_arcsec) {
            // Convert arcseconds to radians using the provided conversion function.
            double xp = arcsec2rad(xp_arcsec);
            double yp = arcsec2rad(yp_arcsec);

            // Pre-compute trigonometric functions for the rotation matrix.
            double cosxp = cos(xp);
            double sinxp = sin(xp);
            double cosyp = cos(yp);
            double sinyp = sin(yp);

            // Construct the polar motion matrix using the transformation equations.
            Eigen::Matrix3d pm;
            pm << cosxp, 0.0, -sinxp,
                    sinxp * sinyp, cosyp, cosxp * sinyp,
                    sinxp * cosyp, -sinyp, cosxp * cosyp;

            return pm;
        }

        // -----------------------------------------------------------------------------
        //  2) PRECESSION: Computes the precession matrix (IAU-76/FK5) to transform
        //     from the Mean of Date (MOD) frame to the Geocentric Celestial Reference
        //     Frame (GCRF) or J2000 frame.
        //     Input parameter: ttt, which is the Julian centuries elapsed since J2000.
        // -----------------------------------------------------------------------------
        static Eigen::Matrix3d precession(double ttt) {
            double ttt2 = ttt * ttt;
            double ttt3 = ttt2 * ttt;

            // Compute the precession angles (in arcseconds) using polynomial approximations.
            double zeta = 2306.2181 * ttt + 0.30188 * ttt2 + 0.017998 * ttt3;
            double theta = 2004.3109 * ttt - 0.42665 * ttt2 - 0.041833 * ttt3;
            double z = 2306.2181 * ttt + 1.09468 * ttt2 + 0.018203 * ttt3;

            // Convert the computed angles from arcseconds to radians.
            zeta = arcsec2rad(zeta);
            theta = arcsec2rad(theta);
            z = arcsec2rad(z);

            // Pre-compute sine and cosine of the angles.
            double coszeta = cos(zeta);
            double sinzeta = sin(zeta);
            double costheta = cos(theta);
            double sintheta = sin(theta);
            double cosz = cos(z);
            double sinz = sin(z);

            // Build the precession rotation matrix based on Vallado eq. 3-54.
            Eigen::Matrix3d prec;
            prec(0, 0) = coszeta * costheta * cosz - sinzeta * sinz;
            prec(0, 1) = coszeta * costheta * sinz + sinzeta * cosz;
            prec(0, 2) = coszeta * sintheta;

            prec(1, 0) = -sinzeta * costheta * cosz - coszeta * sinz;
            prec(1, 1) = -sinzeta * costheta * sinz + coszeta * cosz;
            prec(1, 2) = -sinzeta * sintheta;

            prec(2, 0) = -sintheta * cosz;
            prec(2, 1) = -sintheta * sinz;
            prec(2, 2) = costheta;

            return prec;
        }

        // -----------------------------------------------------------------------------
        //  3) NUTATION: Computes the nutation effects using the full 106-term summation
        //     based on the IAU-1980 model. This calculation outputs the nutation rotation
        //     matrix as well as key parameters (mean obliquity, omega, deltapsi, deltaeps).
        //     The external corrections ddpsi_mas and ddeps_mas are provided in milliarcseconds.
        // -----------------------------------------------------------------------------
        struct NutationOutput {
            Eigen::Matrix3d nut_matrix; // Final nutation rotation matrix.
            double meaneps;            // Mean obliquity of the ecliptic in radians.
            double omega;              // The fundamental angle omega in radians.
            double deltapsi;           // Nutation in longitude in radians.
            double deltaeps;           // Nutation in obliquity in radians.
        };

        static NutationOutput nutation(double ttt, double ddpsi_mas,
                                       double ddeps_mas) {
            // Convert the external corrections from milliarcseconds to arcseconds.
            double ddpsi_as = ddpsi_mas / 1000.0;
            double ddeps_as = ddeps_mas / 1000.0;

            // 1) Compute the mean obliquity of the ecliptic (in arcseconds) using Vallado's formula.
            double ttt2 = ttt * ttt;
            double ttt3 = ttt2 * ttt;
            double meaneps_as = 84381.448 - 46.8150 * ttt - 0.00059 * ttt2 +
                                0.001813 * ttt3;
            double meaneps = arcsec2rad(meaneps_as); // Convert mean obliquity to radians.

            // 2) Compute fundamental arguments (l, l1, F, D, omega) in degrees.
            //    These expressions are taken from Vallado's text (p. 211, 4th ed) and then wrapped modulo 360.
            double l = (1717915923.2178 * ttt + 31.8792 * ttt2 + 0.051635 * ttt3
                        - 0.00024470 * ttt3 * ttt)
                       / 3600.0 + 134.96340251;
            double l1 = (129596581.0481 * ttt - 0.5532 * ttt2 + 0.000136 * ttt3
                         - 0.00001149 * ttt3 * ttt)
                        / 3600.0 + 357.52910918;
            double F = (1739527262.8478 * ttt + 12.7512 * ttt2 + 0.001037 * ttt3
                        - 0.00000417 * ttt3 * ttt)
                       / 3600.0 + 93.27209062;
            double D = (1602961601.2090 * ttt - 6.3706 * ttt2 + 0.006593 * ttt3
                        + 0.00003169 * ttt3 * ttt)
                       / 3600.0 + 297.85019547;
            double om = (-6962890.2665 * ttt + 7.4722 * ttt2 + 0.007702 * ttt3 -
                         0.00005939 * ttt3 * ttt)
                        / 3600.0 + 125.04455501;

            // Wrap each of the fundamental arguments to the range [0, 360) degrees.
            auto wrap360 = [](double x) {
                double r = fmod(x, 360.0);
                return (r < 0) ? r + 360.0 : r;
            };
            l = wrap360(l);
            l1 = wrap360(l1);
            F = wrap360(F);
            D = wrap360(D);
            om = wrap360(om);

            // Convert the fundamental arguments from degrees to radians.
            double l_rad = deg2rad(l);
            double l1_rad = deg2rad(l1);
            double F_rad = deg2rad(F);
            double D_rad = deg2rad(D);
            double om_rad = deg2rad(om);

            // 3) Sum the 106-term nutation series using the provided coefficients.
            double deltapsi = 0.0; // Nutation in longitude (arcseconds)
            double deltaeps = 0.0; // Nutation in obliquity (arcseconds)
            for (int i = 0; i < NUT_TERMS; i++) {
                // Unpack the integer multipliers for the current term.
                int n0 = iar80_data[i][0];
                int n1 = iar80_data[i][1];
                int n2 = iar80_data[i][2];
                int n3 = iar80_data[i][3];
                int n4 = iar80_data[i][4];

                // Retrieve the corresponding real amplitudes (in 0.0001 arcsec).
                double a0 = rar80_data[i][0];
                double a1 = rar80_data[i][1];
                double a2 = rar80_data[i][2];
                double a3 = rar80_data[i][3];

                // Compute the argument for the trigonometric functions.
                double arg = (n0 * l_rad + n1 * l1_rad + n2 * F_rad + n3 * D_rad
                              + n4 * om_rad);

                // For Δψ, use the sine term; for Δε, use the cosine term.
                double psi_term = ((a0 + a1 * ttt) * 1.0e-4) * sin(arg);
                double eps_term = ((a2 + a3 * ttt) * 1.0e-4) * cos(arg);

                deltapsi += psi_term;
                deltaeps += eps_term;
            }

            // Add the external Earth Orientation Parameter (EOP) corrections.
            deltapsi += ddpsi_as;
            deltaeps += ddeps_as;

            // Convert the final nutation values from arcseconds to radians.
            double deltapsi_rad = arcsec2rad(deltapsi);
            double deltaeps_rad = arcsec2rad(deltaeps);

            // Compute the true obliquity of the ecliptic.
            double trueeps = meaneps + deltaeps_rad;

            // 4) Build the nutation rotation matrix using Vallado eq. 3-58.
            double cospsi = cos(deltapsi_rad);
            double sinpsi = sin(deltapsi_rad);
            double coseps = cos(meaneps);
            double sineps = sin(meaneps);
            double costrue = cos(trueeps);
            double sintrue = sin(trueeps);

            // Initialize the nutation matrix to zero.
            Eigen::Matrix3d nut = Eigen::Matrix3d::Zero();
            // Fill in the matrix elements based on the nutation parameters.
            nut(0, 0) = cospsi;
            nut(0, 1) = costrue * sinpsi;
            nut(0, 2) = sintrue * sinpsi;

            nut(1, 0) = -coseps * sinpsi;
            nut(1, 1) = costrue * coseps * cospsi + sintrue * sineps;
            nut(1, 2) = sintrue * coseps * cospsi - sineps * costrue;

            nut(2, 0) = -sineps * sinpsi;
            nut(2, 1) = costrue * sineps * cospsi - sintrue * coseps;
            nut(2, 2) = sintrue * sineps * cospsi + costrue * coseps;

            // Package the results into a NutationOutput structure.
            NutationOutput out;
            out.nut_matrix = nut;
            out.meaneps = meaneps;
            out.omega = om_rad;
            out.deltapsi = deltapsi_rad;
            out.deltaeps = deltaeps_rad;
            return out;
        }

        // -----------------------------------------------------------------------------
        //  4) SIDEREAL TIME
        // Computes the transformation from Universal Time (UT1) to sidereal time,
        // and builds the rotation matrix corresponding to a rotation about the Z-axis.
        //
        // The function computes GMST (Greenwich Mean Sidereal Time) based on the input
        // UT1 Julian date, adds the equation of the equinoxes, and returns the final
        // sidereal rotation matrix.
        // -----------------------------------------------------------------------------
        static Eigen::Matrix3d sidereal(double jdUT1, double lod,
                                        double deltapsiRad, double meaneps,
                                        double omega, int eqeterms) {
            // Compute the UT1 time in Julian centuries.
            double tut1 = (jdUT1 - 2451545.0) / 36525.0;

            // Compute GMST in seconds using Vallado eq. 3-64.
            double GMST_sec = 67310.54841
                              + (876600.0 * 3600.0 + 8640184.812866) * tut1
                              + 0.093104 * (tut1 * tut1)
                              - 6.2e-6 * (tut1 * tut1 * tut1);

            // Convert GMST from seconds to radians.
            double GMST = GMST_sec * (M_PI / 43200.0);
            GMST = wrap_2pi(GMST);

            // Apparent sidereal time (AST) is GMST adjusted by the equation of the equinoxes.
            double AST = GMST + deltapsiRad * cos(meaneps);

            // For dates later than JD 2450449.5 and if eqeterms > 0, add extra correction terms.
            if ((jdUT1 > 2450449.5) && (eqeterms > 0)) {
                double term1 = arcsec2rad(0.00264) * sin(omega);
                double term2 = arcsec2rad(0.000063) * sin(2.0 * omega);
                AST += (term1 + term2);
            }
            AST = wrap_2pi(AST);

            // Build the final rotation matrix for a rotation about the Z-axis by AST.
            Eigen::Matrix3d st;
            double c = cos(AST);
            double s = sin(AST);
            st << c, -s, 0,
                  s,  c, 0,
                  0,  0, 1;

            return st;
        }
    }
}

#endif //ORBMATH_NUTATION_H
