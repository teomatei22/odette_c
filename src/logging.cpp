#include "logging.h"
#include <iomanip>
#include <ctime>
#include <sstream>

namespace barlog {
    std::ofstream write("default_log.log");

    std::string get_date_now() {
        std::time_t now = std::time(nullptr);
        std::tm* tm_ptr = std::localtime(&now);

        std::ostringstream oss;
        oss << std::put_time(tm_ptr, "%d-%m-%Y-%H-%M-%S");
        return oss.str();
    }

    void initialize_log() {
        auto date_str = get_date_now();
        write = std::ofstream(date_str + ".log");
    }

    void info(const std::string& msg) {
        auto date_str = get_date_now();
        write << "(" << date_str << ")[INFO] " << msg << std::endl;
    }

    void warn(const std::string& msg) {
        auto date_str = get_date_now();
        write << "(" << date_str << ")[WARN] " << msg << std::endl;
    }

    void error(const std::string& msg) {
        auto date_str = get_date_now();
        write << "(" << date_str << ")[ERROR] " << msg << std::endl;
    }
}
