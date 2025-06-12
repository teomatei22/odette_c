#ifndef LOGGING_H
#define LOGGING_H

#include <string>
#include <fstream>

namespace barlog {

    /**
     * @brief Output file stream used for logging messages.
     *
     * By default, logs are written to "default_log.log" until initialize_log()
     * is called to open a timestamped file.
     */
    extern std::ofstream write;

    /**
     * @brief Get the current date and time as a formatted string.
     *
     * Formats the current local time into the pattern "DD-MM-YYYY-HH-MM-SS".
     *
     * @return std::string The formatted date-time string.
     */
    std::string get_date_now();

    /**
     * @brief Initialize the log file with a timestamped filename.
     *
     * Closes the default log file (if open) and opens a new file named
     * "<current_date_time>.log" to capture subsequent log entries.
     */
    void initialize_log();

    /**
     * @brief Log an informational message.
     *
     * Prepends the current date-time and "[INFO]" level tag before writing
     * the provided message to the log file.
     *
     * @param msg The informational message to log.
     */
    void info(const std::string& msg);

    /**
     * @brief Log a warning message.
     *
     * Prepends the current date-time and "[WARN]" level tag before writing
     * the provided message to the log file.
     *
     * @param msg The warning message to log.
     */
    void warn(const std::string& msg);

    /**
     * @brief Log an error message.
     *
     * Prepends the current date-time and "[ERROR]" level tag before writing
     * the provided message to the log file.
     *
     * @param msg The error message to log.
     */
    void error(const std::string& msg);

} // namespace barlog

#endif // LOGGING_H
