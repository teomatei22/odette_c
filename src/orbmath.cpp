
#include <Dense>
#include <iostream>
#include <cmath>
#include <vector>
#include "orbmath.h"

#include "logging.h"

namespace orbmath {



    // Convert degrees to radians
    double deg2rad(double deg) {
        return (M_PI / 180.0) * deg;
    }

    // Convert arcseconds to radians
    double arcsec2rad(double arcsec) {
        // 1 arcsecond = 1/3600 deg = (PI/180)/3600 rad
        return arcsec * (M_PI / (180.0 * 3600.0));
    }

    // "Wrap" an angle to the range 0..2π
    double wrap_2pi(double x) {
        x = fmod(x, 2 * M_PI);
        return (x < 0) ? x + 2 * M_PI : x;
    }

    // Clamp to avoid domain errors in acos
    double clamp(double x, double low = -1.0, double high = 1.0) {
        return std::max(low, std::min(high, x));
    }

    // Converts geodetic to ECEF using WGS-84
    Eigen::Vector3d geodetic_to_ecef(double latDeg, double lonDeg, double alt_m) {
        double phi_gd = deg2rad(latDeg);
        double lam = deg2rad(lonDeg);
        double h = alt_m / 1000.0; // convert meters to kilometers

        double e2 = EARTH_ECCENTRICITY * EARTH_ECCENTRICITY;

        // Compute C_earth and S_earth
        double C_e = EARTH_RADIUS / std::sqrt(1.0 - e2 * std::pow(std::sin(phi_gd), 2));
        double S_e = C_e * (1.0 - e2);

        // Compute r_δ and r_K
        double r_delta = (C_e + h) * std::cos(phi_gd);
        double r_K = (S_e + h) * std::sin(phi_gd);

        // Construct r_site_ECEF in km
        double x = r_delta * std::cos(lam);
        double y = r_delta * std::sin(lam);
        double z = r_K;

        return Eigen::Vector3d(x, y, z);
    }


    OrbitalElements compute_orbital_elements(const Eigen::Vector3d& r, const Eigen::Vector3d& v) {
        barlog::info("Computing orbital elements.");

        constexpr double undefined = std::numeric_limits<double>::quiet_NaN();
        const double small = 1e-10;

        OrbitalElements elems = {undefined, undefined, undefined, undefined, undefined, undefined, undefined};

        double r_norm = r.norm();
        double v_norm = v.norm();

        Eigen::Vector3d r_unit = r / r_norm;

        auto v_r = r_unit.dot(v);
        auto v_p = sqrt(v_norm*v_norm + v_r*v_r);

        Eigen::Vector3d h = r.cross(v);
        double h_norm = h.norm();

        // Eccentricity vector
        Eigen::Vector3d evec = ((v_norm * v_norm - mu / r_norm) * r - r.dot(v) * v) / mu;
        double ecc = evec.norm();

        // Specific mechanical energy
        double energy = v_norm * v_norm / 2.0 - mu / r_norm;

        // Semi-major axis and semilatus rectum
        double a, p;
        if (std::abs(ecc - 1.0) > small) {
            a = -mu / (2.0 * energy);
            p = a * (1.0 - ecc * ecc);
        } else {
            p = h_norm * h_norm / mu;
            a = std::numeric_limits<double>::infinity(); // Parabolic
        }

        // Inclination
        double incl = acos(clamp(h.z() / h_norm));

        // Node vector
        Eigen::Vector3d k(0, 0, 1);
        Eigen::Vector3d n = k.cross(h);
        double n_norm = n.norm();

        // RAAN (Ω)
        double raan = (n_norm > small) ? atan2(n.y(), n.x()) : 0.0;
        raan = wrap_2pi(raan);

        // Argument of perigee (ω)
        double argp = (n_norm > small && ecc > small) ? atan2(evec.dot(h.cross(n))
            / (n_norm * h_norm), n.dot(evec) / (n_norm * ecc)) : 0.0;
        argp = wrap_2pi(argp);

        // True anomaly (ν)
        double nu = (ecc > small) ? clamp(evec.dot(r) / (ecc * r_norm)) : 0.0;
        if (r.dot(v) < 0.0) nu = 2.0 * M_PI - nu;
        nu = wrap_2pi(nu);

        // Eccentric anomaly (E) and Mean anomaly (M)
        double cosE = (1.0 - r_norm / a) / ecc;
        cosE = clamp(cosE);
        double sinE = r.dot(v) / (ecc * std::sqrt(mu * a));
        double E = atan2(sinE, cosE);
        E = wrap_2pi(E);
        double M = E - ecc * sin(E);
        M = wrap_2pi(M);

        elems.a = a;
        elems.ecc = ecc;
        elems.incl = incl * 180.0 / M_PI;
        elems.omega = argp * 180.0 / M_PI;
        elems.Omega = raan * 180.0 / M_PI;
        elems.nu = nu * 180.0 / M_PI;
        elems.m = M * 180.0 / M_PI;

        return elems;

    }


    Eigen::Vector3d kepler(const Eigen::Vector3d &r,double dt)
    {
        return -mu/pow(r.norm(),3) * r;
    }
}
