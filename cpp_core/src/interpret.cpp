#include "interpret.h"
#include "json.h"
#include <fstream>

namespace interpret {
    /// @brief Class for interpreting Two-Line Element (TLE) data.
    ///
    /// The TwoLineElement class provides functionality to parse and interpret
    /// TLE data, which is used to describe the orbit of an Earth-orbiting object.
    /// It allows for the extraction of position and velocity vectors at specified times.
    TwoLineElement::TwoLineElement(const std::string &line1, const std::string &line2) {
        m_line1 = line1;
        m_line2 = line2;
        this->m_tle = std::make_unique<TLE>();
        char c_str_line1[512];
        char c_str_line2[512];
        strcpy(c_str_line1, line1.c_str());
        strcpy(c_str_line2, line2.c_str());

        parseLines(this->m_tle.get(),c_str_line1, c_str_line2);
    }


    static std::time_t parse_epoch(const std::string& iso_time) {
        std::tm t{};
        std::istringstream ss(iso_time);
        ss >> std::get_time(&t, "%Y-%m-%dT%H:%M:%S");
        return std::mktime(&t);
    }

    TwoLineElement::TwoLineElement(const std::string &path, size_t index) {
        std::ifstream file(path);
        if (!file.is_open()) {
            throw std::runtime_error("Could not open file: " + path);
        }
        using namespace nlohmann;
        json tle_array;
        file >> tle_array;

        std::string line1, line2;

        auto entry = tle_array[index];
        if (!entry.contains("TLE_LINE1") || !entry.contains("TLE_LINE2"))
            throw std::runtime_error("Invalid TLE form.");


        line1 = entry["TLE_LINE1"];
        line2 = entry["TLE_LINE2"];


        if (line1.empty() || line2.empty()) {
            throw std::runtime_error("No valid TLE data found in: " + path);
        }else {
            m_line1 = line1;
            m_line2 = line2;
            this->m_tle = std::make_unique<TLE>();
            char c_str_line1[512];
            char c_str_line2[512];
            strcpy(c_str_line1, line1.c_str());
            strcpy(c_str_line2, line2.c_str());

            parseLines(this->m_tle.get(),c_str_line1, c_str_line2);
        }
    }

    Eigen::Vector3d TwoLineElement::get_position() const {
        double r[3], v[3];
        getRV(this->m_tle.get(), 0, r,v);
        return Eigen::Vector3d{r[0],r[1],r[2]};
    }

    Eigen::Vector3d TwoLineElement::get_position(double minutes) const {
        double r[3], v[3];
        getRV(this->m_tle.get(), minutes, r,v);
        return Eigen::Vector3d{r[0],r[1],r[2]};
    }


    Eigen::Vector3d TwoLineElement::get_velocity() const {
        double r[3], v[3];
        getRV(this->m_tle.get(),0, r,v);
        return Eigen::Vector3d{v[0],v[1],v[2]};
    }

    Eigen::Vector3d TwoLineElement::get_velocity(double minutes) const {
        double r[3], v[3];
        getRV(this->m_tle.get(),minutes, r,v);
        return Eigen::Vector3d{v[0],v[1],v[2]};
    }
}