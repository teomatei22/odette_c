#include "TDMParser.h"
#include <fstream>
#include <sstream>
#include <iostream>
#include <stdexcept>
#include <cmath>
#include <Dense>
#include "orbmath.h"
#include "SGP4.h"
#include <filesystem>
#include <format>
#include <string>
#include <vector>
#include <iostream>
#include <regex>

#include "logging.h"


namespace interpret {

    /**
     * @brief Parse an ISO 8601 formatted time string into a Julian date (with fraction).
     *
     * Given a string of the form "YYYY-MM-DDThh:mm:ss", this function extracts the
     * calendar date and time components, converts them to a Julian date (JD) and
     * fractional day component using the jday() utility, and returns their sum.
     *
     * @param timeStr The time string in ISO 8601 format ("YYYY-MM-DDThh:mm:ss").
     * @return double Julian date plus fraction (days since J2000).
     * @note Logs the input time string via barlog::info.
     * @throws None. Returns 0.0 if parsing fails or format is invalid.
     */
    static double parse_time_string(const std::string &timeStr) {
        barlog::info(std::format("Parsed time string: {}", timeStr));

        std::string date, time;
        std::istringstream iss(timeStr);

        if (std::getline(iss, date, 'T') && std::getline(iss, time)) {
            int year, month, day;
            int hour = 0, minute = 0;
            double second = 0.0;

            if (std::sscanf(date.c_str(), "%d-%d-%d", &year, &month, &day) != 3)
                return 0.0;
            if (std::sscanf(time.c_str(), "%d:%d:%lf", &hour, &minute,
                            &second) != 3)
                return 0.0;

            double jd, jdFrac;
            jday(year, month, day, hour, minute, second, &jd, &jdFrac);
            return jd + jdFrac;
        }

        return 0.0;
    }


    /**
     * @brief Parse a single TDM (Tracking Data Message) file and extract observations.
     *
     * Opens the specified TDM file, reads the metadata between META_START and META_STOP
     * markers, and reads observation lines between DATA_START and DATA_STOP. Metadata
     * fields such as TIME_SYSTEM, START_TIME, STOP_TIME, and REFERENCE_FRAME are stored
     * in the returned TDMData.meta structure. Station geodetic coordinates (longitude,
     * latitude, altitude) are parsed from COMMENT lines and converted to an ECEF position.
     * Observation lines consist of timestamp, right ascension (degrees), and declination
     * (degrees). Each pair of lines yields one Observation entry with epoch (Julian date),
     * ra (radians), dec (radians), and stationECEF (ECEF position in kilometers). All
     * observations are stored in TDMData.observations.
     *
     * @param filename Filesystem path to the TDM file to parse.
     * @return TDMData A struct containing parsed metadata and a vector of Observation entries.
     * @throws std::runtime_error If the file cannot be opened.
     * @note Logs start and end of parsing via barlog::info, and errors via barlog::error.
     */
    TDMData parse_tdm(const std::string &filename) {
        barlog::info(std::format("Parsing TDM file at path: {}", filename));

        TDMData data;
        std::ifstream infile(filename);
        if (!infile) {
            barlog::error(std::format("Failed to open file {}", filename));
            throw std::runtime_error("Could not open file: " + filename);
        }

        std::string line;
        bool inMeta = false, inData = false;
        std::vector<std::string> metaLines;
        std::vector<std::string> dataLines;

        while (std::getline(infile, line)) {
            if (line.find("META_START") != std::string::npos) {
                inMeta = true;
                continue;
            }
            if (line.find("META_STOP") != std::string::npos) {
                inMeta = false;
                continue;
            }
            if (line.find("DATA_START") != std::string::npos) {
                inData = true;
                continue;
            }
            if (line.find("DATA_STOP") != std::string::npos) {
                inData = false;
                continue;
            }

            if (inMeta) {
                metaLines.push_back(line);
            }
            if (inData) {
                dataLines.push_back(line);
            }
        }

        // Parse metadata
        for (const auto &mline: metaLines) {
            std::istringstream iss(mline);
            std::string key;
            if (!(iss >> key)) continue;

            if (key == "TIME_SYSTEM") {
                std::string eq, value;
                if (iss >> eq >> value)
                    data.meta.time_system = value;
            } else if (key == "START_TIME") {
                std::string eq, timeStr;
                if (iss >> eq >> timeStr)
                    data.meta.start_time = parse_time_string(timeStr);
            } else if (key == "STOP_TIME") {
                std::string eq, timeStr;
                if (iss >> eq >> timeStr)
                    data.meta.stop_time = parse_time_string(timeStr);
            } else if (key == "REFERENCE_FRAME") {
                std::string eq, value;
                if (iss >> eq >> value)
                    data.meta.reference_frame = value;
            } else if (key == "COMMENT") {
                std::string field;
                iss >> field;
                if (field == "LONGITUDE") {
                    double lon;
                    std::string lonDir;
                    if (iss >> lon >> lonDir)
                        data.meta.station_longitude =
                                (lonDir.find("EAST") != std::string::npos)
                                    ? lon
                                    : -lon;
                } else if (field == "LATITUDE") {
                    double lat;
                    std::string latDir;
                    if (iss >> lat >> latDir)
                        data.meta.station_latitude =
                                (latDir.find("NORTH") != std::string::npos)
                                    ? lat
                                    : -lat;
                } else if (field == "ALTITUDE") {
                    double alt;
                    std::string unit;
                    if (iss >> alt >> unit)
                        data.meta.station_altitude = alt; // still in meters
                }
            }
        }

        // Compute station ECI position from geodetic META fields
        Eigen::Vector3d siteECEF = orbmath::geodetic_to_ecef(
            data.meta.station_latitude,
            data.meta.station_longitude,
            data.meta.station_altitude
        );

        // Parse observation data lines two at a time: one for RA, next for Dec
        for (size_t i = 0; i + 1 < dataLines.size(); i += 2) {
            std::string line1 = dataLines[i];
            std::string line2 = dataLines[i + 1];

            size_t eqPos1 = line1.find('=');
            size_t eqPos2 = line2.find('=');
            if (eqPos1 == std::string::npos || eqPos2 == std::string::npos)
                continue;

            std::string content1 = line1.substr(eqPos1 + 1);
            std::string content2 = line2.substr(eqPos2 + 1);
            std::istringstream iss1(content1), iss2(content2);

            std::string obsTimeStr1, obsTimeStr2;
            double ra_deg, dec_deg;
            iss1 >> obsTimeStr1 >> ra_deg;
            iss2 >> obsTimeStr2 >> dec_deg;

            if (obsTimeStr1 != obsTimeStr2) {
                std::cerr << "Warning: mismatched timestamps.\n";
            }

            Observation obs;
            obs.epoch = parse_time_string(obsTimeStr1);
            obs.ra = orbmath::deg2rad(ra_deg);
            obs.dec = orbmath::deg2rad(dec_deg);
            obs.stationECEF = siteECEF;
            data.observations.push_back(obs);
        }

        infile.close();

        barlog::info(std::format("Parsed TDM file at path: {}", filename));
        return data;
    }

    /**
     * @brief Parse multiple TDM files matching a wildcard pattern and filter observations by time interval.
     *
     * Given a filesystem wildcard (e.g., "/path/to/dir/*.tdm"), this function:
     *   1. Extracts the directory and filename pattern from the wildcard string.
     *   2. Iterates over all regular files in that directory whose names contain the pattern prefix.
     *   3. Invokes parse_tdm() on each matching file to collect TDMData objects.
     *   4. Merges all observations into a single TDMData, sorting them by epoch.
     *   5. Filters the merged observations to include only those where the time difference
     *      from the previous selected observation is within [delta - delta_error, delta + delta_error] seconds.
     *   6. Returns the filtered, merged TDMData with metadata inherited from the first file.
     *
     * @param wildcard A wildcard string specifying directory and filename pattern (e.g., "/path/to/*.tdm").
     * @param delta Desired time separation between observations, in seconds.
     * @param delta_error Allowed tolerance for time separation, in seconds.
     * @return TDMData A struct containing the merged metadata and filtered observations.
     * @throws std::runtime_error If the directory portion does not exist or is not a directory,
     *                            or if no files match the wildcard.
     * @note Logs warnings if delta or delta_error are non-positive, and logs errors for I/O issues.
     */
    TDMData parse_tdm_w(const std::string &wildcard, double delta,
                       double delta_error) {
        namespace fs = std::filesystem;

        barlog::info(std::format("Parsing TDM by wildcard {}, with timedelta {} and error {}",
                                wildcard, delta, delta_error));

        if (delta <= 0 || delta_error <= 0) {
            barlog::warn("Delta and/or timedelta less than 0, are you sure?");
        }
        // Extract directory and pattern from wildcard
        fs::path path(wildcard);
        fs::path directory = path.parent_path();
        std::string pattern = path.filename().string();
        std::vector<TDMData> parsed;

        if (!fs::exists(directory) || !fs::is_directory(directory)) {
            barlog::error(std::format("TDM file does not exist: {}", directory.string()));
            throw std::runtime_error(
                "Invalid directory: " + directory.string());
        }

        // Iterate over each file in the directory
        for (const auto &entry: fs::directory_iterator(directory)) {
            if (entry.is_regular_file()) {
                const auto &filename = entry.path().filename().string();
                if (filename.contains(
                    pattern.substr(0, pattern.find_last_of("^")))) {
                    auto data = parse_tdm(entry.path().string());
                    parsed.push_back(data);
                }
            }
        }

        if (parsed.empty()) {
            barlog::error(std::format("No TDM files were matched by wildcard {}", wildcard));
            throw std::runtime_error(
                "No files matched the wildcard: " + wildcard);
        }

        // Merge all parsed TDMData objects
        TDMData mergedData;
        for (const auto &data: parsed) {
            mergedData.observations.insert(mergedData.observations.end(),
                                           data.observations.begin(),
                                           data.observations.end());
        }
        // Inherit metadata from the first parsed file
        mergedData.meta = parsed[0].meta;

        // Sort observations by ascending epoch
        std::sort(mergedData.observations.begin(),
                  mergedData.observations.end(),
                  [](const Observation &a, const Observation &b) {
                      return a.epoch < b.epoch;
                  });

        std::size_t p = 0;
        std::vector<Observation> good_obs;
        good_obs.push_back(mergedData.observations[0]);

        // Filter observations: keep only those separated by ~delta ±delta_error seconds
        for (std::size_t i = 1; i < mergedData.observations.size(); i++) {
            auto dt = mergedData.observations[i].epoch - mergedData.observations[p].epoch;
            dt *= orbmath::SECONDS_PER_DAY;
            if (delta - delta_error < dt && dt < delta + delta_error) {
                p = i;
                good_obs.push_back(mergedData.observations[i]);
            }
        }

        mergedData.observations = good_obs;

        barlog::info("Succesfully parsed TDM file with wildcard.");
        return mergedData;
    }

} // namespace interpret
