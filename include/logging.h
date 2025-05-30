#ifndef LOGGING_H
#define LOGGING_H

#include <string>
#include <fstream>

namespace barlog {
    extern std::ofstream write;

    std::string get_date_now();
    void initialize_log();
    void info(const std::string& msg);
    void warn(const std::string& msg);
    void error(const std::string& msg);
}

#endif // LOGGING_H