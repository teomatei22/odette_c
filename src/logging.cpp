#include "logging.h"
#include <iomanip>
#include <ctime>
#include <sstream>

namespace barlog {
    /// @brief Output file stream used for logging messages.
    ///
    /// By default, logs are written to "default_log.log" until initialize_log()
    /// is called to create a timestamped log file.
    extern std::ofstream write("default_log.log");

    /**
     * @brief Retrieve the current date and time as a formatted string.
     *
     * Formats the current local time into the pattern "DD-MM-YYYY-HH-MM-SS".
     *
     * @return std::string The formatted date-time string.
     */
    std::string get_date_now() {
        std::time_t now = std::time(nullptr);
        std::tm* tm_ptr = std::localtime(&now);

        std::ostringstream oss;
        oss << std::put_time(tm_ptr, "%d-%m-%Y-%H-%M-%S");
        return oss.str();
    }

    /**
     * @brief Initialize the log file with a timestamped filename.
     *
     * Closes the default log file (if open) and opens a new file named
     * "<current_date_time>.log" to capture subsequent log entries.
     */
    void initialize_log() {
        auto date_str = get_date_now();
        write = std::ofstream(date_str + ".log");
    }

    /**
     * @brief Log an informational message.
     *
     * Prepends the current date-time and "[INFO]" level tag before writing
     * the provided message to the log file.
     *
     * @param msg The informational message to log.
     */
    void info(const std::string& msg) {
        auto date_str = get_date_now();
        write << "(" << date_str << ")[INFO] " << msg << std::endl;
    }

    /**
     * @brief Log a warning message.
     *
     * Prepends the current date-time and "[WARN]" level tag before writing
     * the provided message to the log file.
     *
     * @param msg The warning message to log.
     */
    void warn(const std::string& msg) {
        auto date_str = get_date_now();
        write << "(" << date_str << ")[WARN] " << msg << std::endl;
    }

    /**
     * @brief Log an error message.
     *
     * Prepends the current date-time and "[ERROR]" level tag before writing
     * the provided message to the log file.
     *
     * @param msg The error message to log.
     */
    void error(const std::string& msg) {
        auto date_str = get_date_now();
        write << "(" << date_str << ")[ERROR] " << msg << std::endl;
    }
}
