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
#include <Eigen/Dense>       // For Eigen's vector/matrix operations.
#include <iostream>    // For input/output operations.

#include "TLE.h"       // Include TLE class definitions for satellite orbit propagation.

namespace interpret {

// -----------------------------------------------------------------------------
// Structure: Observation
//
// Holds the data for a single observational measurement, including the epoch,
// right ascension (ra), declination (dec), and the observer's ECEF (Earth-Centered
// Earth-Fixed) station coordinates.
// -----------------------------------------------------------------------------
struct Observation {
    double epoch;              // seconds (e.g. seconds of day) representing the observation time.
    double ra;                 // Right Ascension in radians.
    double dec;                // Declination in radians.
    Eigen::Vector3d stationECEF; // Observer's position in the ECEF coordinate system.
};

// -----------------------------------------------------------------------------
// Structure: StateVectors
//
// Contains the computed orbit state at a reference epoch, including position
// and velocity vectors. Typically, the state is computed at the middle observation
// among a set of observations.
// -----------------------------------------------------------------------------
struct StateVectors {
    double epoch;         // Reference epoch, typically corresponding to the middle observation.
    Eigen::Vector3d r;    // Position vector in meters.
    Eigen::Vector3d v;    // Velocity vector in meters per second.
};

// -----------------------------------------------------------------------------
// Function: solveRadecOrbit
//
// Computes a preliminary orbit from at least three RA/Dec observations using
// Gauss's method along with full-precision FG series propagation. The gravitational
// parameter (mu) is used in the orbit determination process.
//
// Parameters:
//   observations - Vector of Observation objects. Must contain at least three entries.
//   mu           - Gravitational parameter in m³/s².
//
// Returns:
//   A StateVectors structure containing the computed orbit state at the middle epoch.
// -----------------------------------------------------------------------------
//StateVectors solveRadecOrbit(const std::vector<Observation>& observations, double mu);
////TODO modify


// -----------------------------------------------------------------------------
// Abstract Class: InterpretationData
//
// Serves as the base class for any interpreted satellite data (such as TLE or RA/Dec),
// enforcing the implementation of methods to retrieve satellite position and velocity
// in an inertial frame.
// -----------------------------------------------------------------------------
class InterpretationData {
public:
    virtual ~InterpretationData() = default; // Virtual destructor for proper cleanup.
    /// @brief Returns the satellite position as a 3D vector (in an inertial frame).
    virtual Eigen::Vector3d get_position() const = 0;
    /// @brief Returns the satellite velocity as a 3D vector (in an inertial frame).
    virtual Eigen::Vector3d get_velocity() const = 0;
};



// -----------------------------------------------------------------------------
// Class: TwoLineElement
//
// Interprets Two-Line Element (TLE) data for a satellite. This class extracts
// orbital parameters from TLE strings and provides methods to obtain the satellite's
// state (position and velocity) at a given time or the reference epoch.
// -----------------------------------------------------------------------------
class TwoLineElement : public InterpretationData {
public:
    /// @brief Constructs a TwoLineElement instance from two TLE lines.
    /// @param line1 First line of the TLE data.
    /// @param line2 Second line of the TLE data.
    TwoLineElement(const std::string& line1, const std::string& line2);
    /// @brief Constructs a TwoLineElement instance by loading TLE data from a file.
    /// @param path File path containing TLE data.
    /// @param index Index of the TLE entry to use (default is 0).
    TwoLineElement(const std::string& path, size_t index=0);
    ~TwoLineElement() override = default;

    // Retrieve the satellite position in an inertial frame.
    Eigen::Vector3d get_position() const override;
    // Overloaded: Retrieve the satellite position at a specified time offset (in minutes).
    Eigen::Vector3d get_position(double minutes) const;
    // Retrieve the satellite velocity in an inertial frame.
    Eigen::Vector3d get_velocity() const override;
    // Overloaded: Retrieve the satellite velocity at a specified time offset (in minutes).
    Eigen::Vector3d get_velocity(double minutes) const ;

    // Returns the Julian Date of the TLE epoch calculated from the TLE record.
    double get_jd() const {
        return m_tle->rec.jdsatepoch + m_tle->rec.jdsatepochF;
    }

private:
    std::string m_line1;              // The first line of the TLE data.
    std::string m_line2;              // The second line of the TLE data.
    std::unique_ptr<TLE> m_tle;         // Unique pointer to a TLE object holding parsed data.
    // Additional private members and implementation details (e.g., parsed orbital elements)
    // would be defined here.
};



// -----------------------------------------------------------------------------
// Class: RADec
//
// Interprets Right Ascension/Declination (RA/Dec) observation data and computes
// the corresponding orbital state using Gauss's method. The computed position
// and velocity are relative to a reference epoch, usually the middle of the observation set.
// -----------------------------------------------------------------------------
class RADec : public InterpretationData {
public:
    /// @brief Constructs a RADec instance using a vector of observations.
    /// @param observations A vector of Observation objects (at least three required).
    RADec(const std::vector<Observation>& observations);
    ~RADec() override = default;

    // Retrieve the computed position in an inertial frame.
    Eigen::Vector3d get_position() const override;
    // Retrieve the computed velocity in an inertial frame.
    Eigen::Vector3d get_velocity() const override;
    double m_epoch;  // Public member: Reference epoch at which the state vectors are computed.

private:
    std::vector<Observation> m_observations; // Original set of RA/Dec observations.
    Eigen::Vector3d m_position;  // Computed position vector at the reference epoch (typically from the second observation).
    Eigen::Vector3d m_velocity;  // Computed velocity vector at the reference epoch.
    bool m_computed;             // Flag to indicate if the orbit computation has been performed.
    /// @brief Computes the orbit state vectors from the observations using Gauss's method.
    void compute_orbit();
};

} // namespace interpret

#endif // INTERPRET_H
