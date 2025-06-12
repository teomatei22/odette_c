#ifndef INTERPRET_H
#define INTERPRET_H

// -----------------------------------------------------------------------------
// interpret.h
//
// This header defines structures and classes for interpreting satellite
// observation data. It includes the definitions for handling RA/Dec observations
// and Two-Line Element (TLE) data, as well as functions to compute orbital states
// using methods like Gauss's method.
// -----------------------------------------------------------------------------

#include <string>      // For using std::string.
#include <memory>      // For smart pointers (std::unique_ptr).
#include <vector>      // For using std::vector.
#include <Dense>       // For Eigen's vector/matrix operations.
#include <iostream>    // For input/output operations.

#include "TLE.h"       // Include TLE class definitions for satellite orbit propagation.

namespace interpret {

/**
 * @struct Observation
 * @brief Holds data for a single observational measurement.
 *
 * Contains the epoch (time of observation), right ascension (ra),
 * declination (dec), and the observer's ECEF (Earth-Centered
 * Earth-Fixed) station coordinates.
 */
struct Observation {
    double epoch;                ///< Seconds representing the observation time.
    double ra;                   ///< Right Ascension in radians.
    double dec;                  ///< Declination in radians.
    Eigen::Vector3d stationECEF; ///< Observer's position in the ECEF coordinate system.
};

/**
 * @struct StateVectors
 * @brief Contains computed orbit state at a reference epoch.
 *
 * Stores the position and velocity vectors for the satellite,
 * typically computed at the middle observation among a set.
 */
struct StateVectors {
    double epoch;         ///< Reference epoch, typically corresponding to the middle observation.
    Eigen::Vector3d r;    ///< Position vector in meters.
    Eigen::Vector3d v;    ///< Velocity vector in meters per second.
};

/**
 * @class InterpretationData
 * @brief Abstract base class for interpreted satellite data.
 *
 * Enforces the implementation of methods to retrieve satellite
 * position and velocity in an inertial frame.
 */
class InterpretationData {
public:
    virtual ~InterpretationData() = default; ///< Virtual destructor for proper cleanup.

    /**
     * @brief Retrieve the satellite position in an inertial frame.
     * @return Eigen::Vector3d Position vector.
     */
    virtual Eigen::Vector3d get_position() const = 0;

    /**
     * @brief Retrieve the satellite velocity in an inertial frame.
     * @return Eigen::Vector3d Velocity vector.
     */
    virtual Eigen::Vector3d get_velocity() const = 0;
};

/**
 * @class TwoLineElement
 * @brief Interprets Two-Line Element (TLE) data for a satellite.
 *
 * Extracts orbital parameters from TLE strings and provides methods
 * to obtain the satellite's state (position and velocity) at a given time
 * or at the reference epoch.
 */
class TwoLineElement : public InterpretationData {
public:
    /**
     * @brief Construct from two TLE lines.
     * @param line1 First line of the TLE data.
     * @param line2 Second line of the TLE data.
     */
    TwoLineElement(const std::string& line1, const std::string& line2);

    /**
     * @brief Construct by loading TLE data from a file.
     * @param path File path containing TLE data.
     * @param index Index of the TLE entry to use (default is 0).
     */
    TwoLineElement(const std::string& path, size_t index = 0);

    ~TwoLineElement() override = default;

    /**
     * @brief Retrieve the satellite position in an inertial frame (at epoch).
     * @return Eigen::Vector3d Position vector.
     */
    Eigen::Vector3d get_position() const override;

    /**
     * @brief Retrieve the satellite position at a specified time offset.
     * @param minutes Minutes past the TLE epoch to compute position.
     * @return Eigen::Vector3d Position vector.
     */
    Eigen::Vector3d get_position(double minutes) const;

    /**
     * @brief Retrieve the satellite velocity in an inertial frame (at epoch).
     * @return Eigen::Vector3d Velocity vector.
     */
    Eigen::Vector3d get_velocity() const override;

    /**
     * @brief Retrieve the satellite velocity at a specified time offset.
     * @param minutes Minutes past the TLE epoch to compute velocity.
     * @return Eigen::Vector3d Velocity vector.
     */
    Eigen::Vector3d get_velocity(double minutes) const;

    /**
     * @brief Get the Julian Date of the TLE epoch.
     * @return double Julian Date (integer + fraction).
     */
    double get_jd() const {
        return m_tle->rec.jdsatepoch + m_tle->rec.jdsatepochF;
    }

private:
    std::string m_line1;               ///< The first line of the TLE data.
    std::string m_line2;               ///< The second line of the TLE data.
    std::unique_ptr<TLE> m_tle;        ///< Unique pointer to a TLE object holding parsed data.
    // Additional private members and implementation details would be defined here.
};

/**
 * @class RADec
 * @brief Interprets Right Ascension/Declination (RA/Dec) observation data.
 *
 * Computes the corresponding orbital state using Gauss's method. The computed
 * position and velocity are relative to a reference epoch, usually the middle
 * of the observation set.
 */
class RADec : public InterpretationData {
public:
    /**
     * @brief Construct using a set of observations.
     * @param observations Vector of Observation objects (at least three required).
     */
    RADec(const std::vector<Observation>& observations);

    ~RADec() override = default;

    /**
     * @brief Retrieve the computed position in an inertial frame.
     * @return Eigen::Vector3d Position vector.
     */
    Eigen::Vector3d get_position() const override;

    /**
     * @brief Retrieve the computed velocity in an inertial frame.
     * @return Eigen::Vector3d Velocity vector.
     */
    Eigen::Vector3d get_velocity() const override;

    double m_epoch;  ///< Reference epoch at which the state vectors are computed.

private:
    std::vector<Observation> m_observations; ///< Original set of RA/Dec observations.
    Eigen::Vector3d m_position;             ///< Computed position vector at the reference epoch.
    Eigen::Vector3d m_velocity;             ///< Computed velocity vector at the reference epoch.
    bool m_computed;                        ///< Flag indicating if orbit computation has been performed.

    /**
     * @brief Compute the orbit state vectors from the observations using Gauss's method.
     */
    void compute_orbit();
};

} // namespace interpret

#endif // INTERPRET_H
