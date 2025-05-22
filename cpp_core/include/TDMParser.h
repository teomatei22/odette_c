    #ifndef TDMPARSER_H
#define TDMPARSER_H

#include <string>
#include <vector>
#include "interpret.h"  // For interpret::Observation definition

namespace interpret {

    /**
     * @brief Structure to hold metadata extracted from a TDM file.
     *
     * This includes timing system, frame, station location, and time boundaries
     * for the observation session.
     */
    struct MetaData {
        std::string time_system;         ///< Time system used (e.g., UTC, TAI)
        std::string reference_frame;     ///< Reference frame (e.g., ITRF93, EME2000)
        double start_time;               ///< Start time in seconds since epoch
        double stop_time;                ///< Stop time in seconds since epoch
        double station_longitude;        ///< Longitude of observing station (degrees east)
        double station_latitude;         ///< Latitude of observing station (degrees north)
        double station_altitude;         ///< Altitude of station above sea level (km)
    };

    /**
     * @brief Combines metadata and a list of line-of-sight observations.
     *
     * Represents the full content of a parsed TDM file.
     */
    struct TDMData {
        MetaData meta;                                   ///< Meta-information about the TDM session
        std::vector<interpret::Observation> observations;///< Vector of parsed RA/Dec observations
    };

    /**
     * @brief Parses a TDM file to extract metadata and line-of-sight observations.
     *
     * The TDM file is expected to follow CCSDS Tracking Data Message format with
     * Right Ascension and Declination values for each time step.
     *
     * @param filename The full path to the TDM file.
     * @return TDMData Struct containing parsed metadata and observation vectors.
     */
    TDMData parse_tdm(const std::string& filename);

    /**
     * @brief Extended parser that handles TDM files matched via wildcard and applies corrections.
     *
     * This overload supports time-error modeling by applying additional delta offsets.
     *
     * @param wildcard File path expression with wildcards (e.g., "*.tdm").
     * @param delta Seconds to shift each epoch.
     * @param delta_error Error bound for measurement epochs.
     * @return TDMData Combined data from parsed files with time corrections.
     */
    TDMData parse_tdm_w(const std::string& wildcard, double delta, double delta_error);

}
#endif // TDMPARSER_H
