#include "TDMParser.h"
#include <fstream>
#include <sstream>
#include <iostream>
#include <stdexcept>
#include <cmath>
#include <Eigen/Dense>
#include "orbmath.h"
#include "SGP4.h"
#include <filesystem>
#include <string>
#include <vector>
#include <iostream>
#include <regex>


namespace interpret {
    static double parse_time_string(const std::string &timeStr) {
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


    TDMData parse_tdm(const std::string &filename) {
        TDMData data;
        std::ifstream infile(filename);
        if (!infile) {
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

        // Compute station ECI from SITE-TRACK
        Eigen::Vector3d siteECEF = orbmath::geodetic_to_ecef(
            data.meta.station_latitude,
            data.meta.station_longitude,
            data.meta.station_altitude
        );

        // Parse observation data
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
        return data;
    }

    TDMData parse_tdm_w(const std::string &wildcard, double delta,
                       double delta_error) {
        namespace fs = std::filesystem;

        // Extract the directory and the regex pattern directly from the input path.
        fs::path path(wildcard);
        fs::path directory = path.parent_path();
        std::string pattern = path.filename().string();
        std::vector<TDMData> parsed;

        if (!fs::exists(directory) || !fs::is_directory(directory)) {
            throw std::runtime_error(
                "Invalid directory: " + directory.string());
        }

        // Iterate over each file in the directory.
        for (const auto &entry: fs::directory_iterator(directory)) {
            if (entry.is_regular_file()) {
                const auto &filename = entry.path().filename().string();
                if (filename.find(
                    pattern.substr(0, pattern.find_last_of("^")))) {
                    auto data = parse_tdm(entry.path().string());
                    parsed.push_back(data);
                }
            }
        }

        if (parsed.empty()) {
            throw std::runtime_error(
                "No files matched the wildcard: " + wildcard);
        }

        // Merge the parsed TDMData objects.
        TDMData mergedData;
        for (const auto &data: parsed) {
            mergedData.observations.insert(mergedData.observations.end(),
                                           data.observations.begin(),
                                           data.observations.end());
        }
        // Merge meta-data as needed. Here we simply take the meta from the first parsed data.
        mergedData.meta = parsed[0].meta;

        // Sort the observations by epoch.
        std::sort(mergedData.observations.begin(),
                  mergedData.observations.end(),
                  [](const Observation &a, const Observation &b) {
                      return a.epoch < b.epoch;
                  });

        std::size_t p = 0;
        std::vector<Observation> good_obs;
        good_obs.push_back(mergedData.observations[0]);

        // Filter to be at least delta - delta_error and at most delta + delta_error apart
        for (std::size_t i = 1; i < mergedData.observations.size(); i++) {
            auto dt = mergedData.observations[i].epoch - mergedData.observations
                      [p].epoch;
            dt *= orbmath::SECONDS_PER_DAY;
            if (delta - delta_error < dt && dt < delta + delta_error) {
                p = i;
                good_obs.push_back(mergedData.observations[i]);
            }
        }

        mergedData.observations = good_obs;
        return mergedData;
    }
} // namespace interpret
