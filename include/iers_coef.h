#ifndef IERS_COEF_H
#define IERS_COEF_H

// -----------------------------------------------------------------------------
// IERS_COEF_H
// This header file handles the loading and processing of IERS (International
// Earth Rotation and Reference Systems Service) constant data from a CSV file.
// The data is used to obtain Earth orientation parameters required for
// various orbital and coordinate transformations.
// -----------------------------------------------------------------------------

#include <cmath>       // Provides mathematical functions.
#include <fstream>     // Stream classes for file input/output.
#include <iostream>    // Standard input/output streams.
#include <memory>      // Provides memory management utilities.
#include <sstream>     // String stream classes for string processing.
#include <string>      // Provides string class and related functions.
#include <tuple>       // Allows grouping multiple values into a single return type.
#include <vector>      // Provides the vector container.
#include <algorithm>   // For algorithms such as std::lower_bound.
#include <SGP4.h>      // SGP4 propagation model support.
#include "logging.h"   // Custom logging utilities for debugging/output.
#include "orbmath_nutation.h"  // Functions for nutation calculations related to orbital math.

namespace utils {

    // Constant representing the number of "equinox terms"; set as needed.
    constexpr std::size_t eqeterms = 2;

    /**
     * @brief Structure representing a record from the IERS constants CSV.
     *
     * Each IERSRecord holds date components, a reduced Julian date (rjd), and
     * the tokenized CSV line which contains all the fields. This structure
     * facilitates quick lookup and retrieval of orientation parameters.
     */
    struct IERSRecord {
        std::size_t year;                     // Year of the record.
        std::size_t month;                    // Month of the record.
        std::size_t day;                      // Day of the record.
        double rjd;                           // The "reduced" Julian Date for the record.
        std::vector<std::string> csv_line;    // Entire CSV line split into tokens.
    };

    /**
     * @brief Retrieves and caches the IERS data from the CSV file "constants.csv".
     *
     * This function reads the CSV file, tokenizes each line based on semicolons,
     * parses date information and computes the reduced Julian date (rjd) for
     * each record. The loaded records are stored in a static vector so that
     * subsequent calls do not re-read the file.
     *
     * @return std::vector<IERSRecord>& Reference to the vector containing all loaded IERS records.
     */
    inline std::vector<IERSRecord>& get_iers_data() {
        static bool loaded = false;               // Flag to indicate if CSV data has been loaded.
        static std::vector<IERSRecord> iers_data;   // Container for storing IERS records.

        // If the data has not been loaded yet, process the CSV file.
        if (!loaded) {
            std::ifstream csv_file("constants.csv"); // Open the CSV file containing constants.
            if (!csv_file) {
                // Log an error if the CSV file cannot be opened.
                barlog::error( "Error opening constants.csv" );
                loaded = true; // Mark as loaded to avoid repeated attempts.
                return iers_data;
            }

            std::string line;
            // Read the CSV file line by line.
            while (std::getline(csv_file, line)) {
                std::istringstream iss(line);
                // Tokenize the line using semicolons as delimiters.
                std::vector<std::string> tokens;
                {
                    std::string token;
                    while (std::getline(iss, token, ';')) {
                        tokens.push_back(token); // Add each token to the tokens vector.
                    }
                }

                // Verify the token count; skip the line if not enough tokens.
                if (tokens.size() < 17) {
                    // Skip invalid or incomplete lines.
                    continue;
                }

                // Parse the year, month, and day from the corresponding tokens.
                std::size_t y = 0, m = 0, d = 0;
                {
                    std::stringstream ssy(tokens[1]);
                    ssy >> y;
                    std::stringstream ssm(tokens[2]);
                    ssm >> m;
                    std::stringstream ssd(tokens[3]);
                    ssd >> d;
                }

                double rjd = 0, rjd_f = 0;
                // Calculate the reduced Julian date using the parsed date components.
                jday(y, m, d, 0, 0, 0, &rjd, &rjd_f);
                rjd += rjd_f;  // Combine day fraction with integer part of Julian date.

                // Construct an IERSRecord with the parsed values and tokenized CSV line.
                IERSRecord rec { y, m, d, rjd, tokens };
                iers_data.push_back(rec);  // Append the record to the data vector.
            }

            csv_file.close();  // Close the CSV file after processing.

            // Sort the records by the reduced Julian date (rjd) in ascending order.
            std::sort(iers_data.begin(), iers_data.end(),
                      [](const IERSRecord &a, const IERSRecord &b) {
                          return a.rjd < b.rjd;
                      });

            loaded = true;  // Set the flag to indicate that data has been loaded.
        }
        return iers_data;  // Return the cached IERS data vector.
    }

    /**
     * @brief Converts a string to a size_t.
     *
     * This helper function checks if the string is empty and then converts it
     * into a std::size_t value using a stringstream.
     *
     * @param str The input string representing a numeric value.
     * @return std::size_t The converted numeric value or 0 if the string is empty.
     */
    inline std::size_t to_size_t(const std::string &str) {
        if (str.empty()) return 0;  // Return 0 for an empty string.
        std::size_t result = 0;
        std::stringstream ss(str);
        ss >> result;  // Convert the string to a size_t.
        return result;
    }

    /**
     * @brief Converts a string to a double.
     *
     * This helper function checks if the string is empty and then converts it
     * into a double using a stringstream.
     *
     * @param str The input string representing a floating-point value.
     * @return double The converted value as a double, or 0.0 if the string is empty.
     */
    inline double to_double(const std::string &str) {
        if (str.empty()) return 0.0;  // Return 0.0 for an empty string.
        double result = 0.0;
        std::stringstream ss(str);
        ss >> result;  // Convert the string to a double.
        return result;
    }

    // Define a tuple type to hold conversion constants used in orbital coordinate transformations.
    // The tuple holds: (dUT1, dAT, xp, yp, lod, ddpsi, ddeps)
    typedef std::tuple<double, double, double, double, double, double, double> eci_conversion_tuple;

    /**
     * @brief Finds the IERS record with a reduced Julian date closest to the target.
     *
     * This function performs a binary search on the provided data vector to locate
     * the record with an rjd that is closest to the target value. If no data is present,
     * it returns a fallback dummy record.
     *
     * @param data The vector of IERS records.
     * @param target_jd The target reduced Julian date to search for.
     * @return const IERSRecord& Reference to the record closest to target_jd.
     */
    inline const IERSRecord& find_closest_record(const std::vector<IERSRecord>& data, double target_jd) {
        // Return a dummy record if the data vector is empty.
        if (data.empty()) {
            static IERSRecord dummy {0,0,0,0.0,{}};
            return dummy;
        }

        // Comparison lambda for binary search by the reduced Julian date.
        auto cmp = [](const IERSRecord &rec, double val) {
            return rec.rjd < val;
        };

        // Use lower_bound to find the first record with rjd not less than target_jd.
        auto it = std::lower_bound(data.begin(), data.end(), target_jd, cmp);

        if (it == data.begin()) {
            // If the target is earlier than or equal to the first record, return the first record.
            return *it;
        }
        else if (it == data.end()) {
            // If the target is later than all records, return the last record.
            return *(it - 1);
        }
        else {
            // For targets in between, compare the found record with the previous one
            // and return the record that is closer in time to the target.
            auto prev_it = it - 1;
            if (std::fabs(it->rjd - target_jd) < std::fabs(prev_it->rjd - target_jd)) {
                return *it;
            } else {
                return *prev_it;
            }
        }
    }

    /**
     * @brief Retrieves Earth orientation parameters for coordinate transformations.
     *
     * This function retrieves constants required for converting between different
     * coordinate frames (such as ECI and ECEF) by loading IERS data from a CSV file.
     * It performs a binary search to find the closest record to the given Julian date,
     * logs the data, and extracts specific fields. Some values are hard-coded if not found.
     *
     * @param jd The Julian date for which to retrieve the constants.
     * @return eci_conversion_tuple A 7-tuple containing: dUT1, dAT, xp, yp, lod, ddpsi, ddeps.
     */
    inline eci_conversion_tuple get_constants(double jd) {
        // Retrieve the static cached IERS data.
        auto &iers_data = get_iers_data();
        // Check if any data was loaded; if not, log an error and return default values.
        if (iers_data.empty()) {
            barlog::error( "ERROR: No IERS data loaded.\n");
            return {0, 0, 0, 0, 0, 0, 0};
        }

        // (1) Use binary search to find the IERS record closest to the given Julian date.
        const IERSRecord &rec = find_closest_record(iers_data, jd);

        // (2) Log the tokenized CSV line from the chosen record for debugging purposes.
        for (auto &res : rec.csv_line) {
            barlog::info(res);
        }

        // (3) Extract orientation parameters from specific columns in the CSV:
        //      - Column 5: xp (polar motion component)
        //      - Column 7: yp (polar motion component)
        //      - Column 14: dUT1 (difference between UT1 and UTC)
        //      - Column 16: lod (length of day correction)
        double dUT1 = 0.0;
        double xp   = 0.0;
        double yp   = 0.0;
        double lod  = 0.0;
        if (rec.csv_line.size() >= 17) {
            xp   = to_double(rec.csv_line[5]);
            yp   = to_double(rec.csv_line[7]);
            dUT1 = to_double(rec.csv_line[14]);
            lod  = to_double(rec.csv_line[16]);
        }

        // Define hard-coded parameters if they are not provided in the CSV.
        double dAT   = 37.0;   // Difference between TAI and UTC.
        double ddpsi = -85.0;  // Nutation in longitude correction.
        double ddeps = 10.0;   // Nutation in obliquity correction.

        return {dUT1, dAT, xp, yp, lod, ddpsi, ddeps}; // Return the parameters as a tuple.
    }

} // namespace utils

#endif // IERS_COEF_H
