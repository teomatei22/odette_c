
#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <iomanip>
#include "json.h"

#include "TDMParser.h"
#include "interpret.h"
#include "orbmath.h"
#include "popl.h"
#include "SGP4.h"
#include "TLE.h"
#include "propagator.h"
#include "orbmath_perturbation.h"
#include "frame.h"
#include "json.h"

using json = nlohmann::json;

#define HELP_ME \
"Odette - Orbit Determination Technologies\n" \
"-----------------------------------------\n" \
"\n" \
"Usage:\n" \
"    odette [OPTIONS]\n" \
"\n" \
"Description:\n" \
"    Odette is a command-line tool for orbit determination and propagation.\n" \
"    It supports two main modes:\n" \
"      - SGP4 propagation based on Two-Line Elements (TLE)\n" \
"      - Gauss method orbit determination from Right Ascension/Declination observations (TDM)\n" \
"    Output can be generated in CSV or JSON formats for easy interoperability.\n" \
"\n" \
"Options:\n" \
"    --method <sgp4|gauss>\n" \
"        Selects the orbit determination method:\n" \
"          - sgp4: Uses TLE input and SGP4 model for orbit propagation\n" \
"          - gauss: Uses RA/Dec observations to solve the orbit and propagate using RK45\n" \
"\n" \
"    --tle-json <file>\n" \
"        Path to the TLE input file. If the file is JSON-formatted, it is parsed accordingly; otherwise, plaintext TLE format is assumed.\n" \
"\n" \
"    --tdm <wildcard>\n" \
"        Path pattern (wildcard allowed) to TDM observation files, used only with Gauss method.\n" \
"        Example: ./data/Jason/20240318_16002A_A^.tdm , where ^ is the \"match anything\" wildcard.\n"\
"\n" \
"    --output <file>\n" \
"        Path where the propagated orbit data will be saved.\n" \
"\n" \
"    --format-out <csv|json>\n" \
"        Output format of the saved orbit file.\n" \
"          - csv: Outputs epochs, positions, and velocities in comma-separated format\n" \
"          - json: Outputs structured JSON entries for each point in time\n" \
"\n" \
"    --period <minutes>\n" \
"        Total duration (in minutes) for orbit propagation starting from the initial epoch.\n" \
"\n" \
"    --points <integer>\n" \
"        Number of sample points to generate within the propagation period.\n" \
"\n" \
"    --time-delta <minutes>\n" \
"        (Only for Gauss method) Time difference between observations to use when parsing TDM files.\n" \
"\n" \
"    --time-delta-error <minutes>\n" \
"        (Only for Gauss method) Allowable time error margin when filtering TDM observations.\n" \
"\n" \
"    -h, --help\n" \
"        Displays this help message.\n" \
"\n" \
"Examples:\n" \
"    odette --method sgp4 --tle-json tle.txt --output orbit.csv --format-out csv --period 90 --points 300\n" \
"    odette --method gauss --tdm ./data/Jason/20240318_16002A_A^.tdm --output orbit.json --format-out json --period 120 --points 400 --time-delta 100 --time-delta-error 30\n" \
"\n"

void write_csv(const std::string& path, const std::vector<double>& epochs,
               const std::vector<Eigen::Vector3d>& positions,
               const std::vector<Eigen::Vector3d>& velocities) {
    std::ofstream out(path);
    out << "Epoch,Position_X_km,Position_Y_km,Position_Z_km,Velocity_X_kmps,Velocity_Y_kmps,Velocity_Z_kmps\n";
    for (size_t i = 0; i < epochs.size(); ++i) {
        out << std::fixed << std::setprecision(6) << epochs[i] << ","
            << positions[i].x() << "," << positions[i].y() << "," << positions[i].z() << ","
            << velocities[i].x() << "," << velocities[i].y() << "," << velocities[i].z() << "\n";
    }
}

void write_json(const std::string& path, const std::vector<double>& epochs,
                const std::vector<Eigen::Vector3d>& positions,
                const std::vector<Eigen::Vector3d>& velocities) {
    json j = json::array();
    for (size_t i = 0; i < epochs.size(); ++i) {
        j.push_back({
            {"epoch", epochs[i]},
            {"position", {positions[i].x(), positions[i].y(), positions[i].z()}},
            {"velocity", {velocities[i].x(), velocities[i].y(), velocities[i].z()}}
        });
    }
    std::ofstream out(path);
    out << std::setw(4) << j << std::endl;
}

int main(int argc, char* argv[]) {
    using namespace popl;//command line argument parsing library
    OptionParser op("Odette CLI Options");
    auto help = op.add<Switch>("h", "help", "Show help message");
    auto method = op.add<Value<std::string>>("", "method", "sgp4 or gauss"); //mandatory
    auto tle_file = op.add<Value<std::string>>("", "tle-json", "TLE input file"); //mandatory(sgp)
    auto tdm_file = op.add<Value<std::string>>("", "tdm", "TDM observation file"); //mandatory(gauss)
    auto output = op.add<Value<std::string>>("", "output", "Output file"); //optional (default orbit_output.csv)
    auto format = op.add<Value<std::string>>("", "format-out", "csv or json");//optional(default csv)
    auto period = op.add<Value<double>>("", "period", "Time in minutes to propagate");//optional(2h)
    auto points = op.add<Value<int>>("", "points", "Number of points");//optional(200)
    auto time_delta = op.add<Value<double>>("", "time-delta", "Time delta in minutes"); //optional(100s)
    auto time_delta_error = op.add<Value<double>>("", "time-delta-error", "Time delta error in minutes"); //optional(30s)

    op.parse(argc, argv);

    if (help->is_set() || argc == 1) {
        std::cout << HELP_ME;
        return 0;
    }

    //default parameters if values left unspecified
    std::string method_val = method->value_or(""); //no method is default, MUST be specified
    std::string format_val = format->value_or("csv"); //csv format default
    std::string out_path = output->value_or("orbit_output.txt"); //dummy file if user doesn't specify
    double duration_min = period->value_or(120.0); //default orbit duration (2h)
    int num_points = points->value_or(200); // 200 points by default

    std::vector<double> epochs;
    std::vector<Eigen::Vector3d> positions;
    std::vector<Eigen::Vector3d> velocities;

    if (method_val == "sgp4") {
        std::string tlepath = tle_file->value_or(""); //assume empty tle filepath if unspecified
        if (tlepath.empty()) { //check if filepath is empty, if so them ask for file
            std::cerr << "TLE input file required for SGP4.\n";
            return 1;
        }
        interpret::TwoLineElement tle(tlepath);
        double jd0 = tle.get_jd();
        for (int i = 0; i < num_points; ++i) {
            double dt_min = (i * duration_min) / (num_points - 1);
            epochs.push_back(jd0 + dt_min / orbmath::SECONDS_PER_DAY);
            positions.push_back(tle.get_position(dt_min));
            velocities.push_back(tle.get_velocity(dt_min));
        }
    } else if (method_val == "gauss") {
        std::string tdm = tdm_file->value_or("");
        if (tdm.empty()) {
            std::cerr << "TDM file required for Gauss method.\n";
            return 1;
        }
        std::cout<<tdm<<std::endl;
        auto tdmdata = interpret::parse_tdm_w(tdm, time_delta->value_or(100),
                                               time_delta_error->value_or(30));
        interpret::RADec solver(tdmdata.observations); // initialize gauss for the obs obtained using wildcard
        auto r0 = solver.get_position(); //results from gauss
        auto v0 = solver.get_velocity();
        double jd0 = solver.m_epoch;

        //generate epoch vector
        epochs.push_back(jd0);
        for (int i = 1; i < num_points; ++i) {
            epochs.push_back(jd0 + (i * duration_min / (num_points - 1)) / orbmath::SECONDS_PER_DAY);
        }

        //initialize propagator and compute
        propagate::Propagator p(r0, v0, epochs, propagate::integrators::rk45_eci);
        p.compute();
        positions = p.ephem.positions;
        velocities = p.ephem.velocities;
    } else { //if method is unspecified or doesnt exist then error
        std::cerr << "Unsupported or unspecified method: " << method_val << "\n";
        return 1;
    }

    if (format_val == "csv") {
        write_csv(out_path, epochs, positions, velocities);
    } else if (format_val == "json") {
        write_json(out_path, epochs, positions, velocities);
    } else {
        std::cerr << "Unsupported format: " << format_val << "\n";
        return 1;
    }

    std::cout << "Orbit written to " << out_path << " in " << format_val << " format.\n";
    return 0;
}
