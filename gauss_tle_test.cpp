#include <chrono>
#include <fstream>
#include <iostream>

#include "frame.h"
#include "orbmath_perturbation.h"
#include "propagator.h"
#include "include/interpret.h"
#include "include/orbmath.h"
#include "include/TDMParser.h"
//#include "raylib.h"
#include "solar_position.h"

bool visual_test_gauss_tdm_benchmark() {
    std::ofstream test_outputs("gauss_tdm_benchmark.txt");

    auto t1 = std::chrono::high_resolution_clock::now();
    int cntr = 0;
    for (double delta = 60; delta <= 120; delta += 5) {
        for (double delta_error = 2; delta_error <= 15; delta_error += 1) {
            cntr += 1;

            try {
                auto tdms = interpret::parse_tdm_w(
                    "data/Jason/20240318_16002A_B*", delta, delta_error);
                auto radec = interpret::RADec(tdms.observations);

                std::stringstream ss;
                auto altitude = radec.get_position().norm() - 6378;
                ss << "Altitude: " << altitude << " at delta: " << delta <<
                        " delta_error: " << delta_error
                        << " for " << tdms.observations.size() <<
                        " observations, speed: " << radec.get_velocity().norm();

                if (1320 < altitude && altitude < 1340) {
                    ss << "[SUCCESS]";
                } else {
                    ss << "[FAILURE]";
                }

                test_outputs << ss.str() << std::endl;
            } catch (const std::exception &ex) {
                continue;
            }
        }
    }

    auto t2 = std::chrono::high_resolution_clock::now();

    test_outputs << "Executed " << cntr << " operations in "
            << std::chrono::duration_cast<std::chrono::milliseconds>(t2 - t1).
            count() << " ms" << std::endl;

    return true;
}

bool gauss_tle_altitude_test() {
    std::ofstream test_outputs("tle_altitude_test.txt");

    auto t1 = std::chrono::high_resolution_clock::now();
    int cntr = 0;
    int lim = ((300 - 10) / 10) * ((30 - 5) / 5);
    for (double delta = 10; delta <= 60 * 5; delta += 10) {
        for (double delta_error = 5; delta_error <= 30; delta_error += 5) {
            cntr += 1;

            try {
                auto tdms = interpret::parse_tdm_w(
                    "data/Jason/20240318_16002A_A*", delta, delta_error);
                auto radec = interpret::RADec(tdms.observations);

                const std::string line1 =
                    "1 41240U 16002A   24078.93311235 -.00000041  00000-0  88455-4 0  9998";
                const std::string line2 =
                    "2 41240  66.0433  38.7934 0008217 275.1931  84.8147 12.80929479381943";
                interpret::TwoLineElement a(line1, line2);
                auto pos_tdm = a.get_position();
                auto vel_tdm = a.get_velocity();

                std::stringstream ss;
                auto altitude = radec.get_position().norm() - 6378;
                ss << "TLE Altitude: " << altitude << " at delta: " << delta <<
                        " delta_error: " << delta_error
                        << " for " << tdms.observations.size() <<
                        " observations, speed: " << radec.get_velocity().norm();
                ss << '\n';

                auto altitude_tdm = pos_tdm.norm() - 6378;
                ss << "TDM Altitude difference: " << abs(
                            altitude_tdm - altitude)
                        << " speed difference: " << abs(
                            vel_tdm.norm() - radec.get_velocity().norm());

                ss << '\n';
                orbmath::OrbitalElements elems =
                        orbmath::compute_orbital_elements(
                            radec.get_position(), radec.get_velocity());
                orbmath::OrbitalElements tle_elems =
                        orbmath::compute_orbital_elements(pos_tdm, vel_tdm);
                ss << "ORBITAL ELEMENTS: " << "[a: " << elems.a << ", a_tle: "
                        << tle_elems.a << "]\n "
                        << "[e: " << elems.ecc << ", e_tle: " << tle_elems.ecc
                        << "]\n "
                        << "[i: " << elems.incl << ", i_tle: " << tle_elems.incl
                        << "]\n "
                        << "[raan: " << elems.Omega << ", raan_tle: " <<
                        tle_elems.Omega << "]\n "
                        << "[argp: " << elems.omega << ", argp_tle: " <<
                        tle_elems.omega << "]\n "
                        << "[nu: " << elems.nu << ", nu_tle: " << tle_elems.nu
                        << "]\n "
                        << "[M: " << elems.m << ", M_tle: " << tle_elems.m <<
                        "]\n ";

                ss <<
                        "=============================================================================";

                if (1330 < altitude && altitude < 1345) {
                    ss << "[SUCCESS]";
                } else {
                    ss << "[FAILURE]";
                }

                test_outputs << ss.str() << std::endl;
            } catch (const std::exception &ex) {
                continue;
            }
        }
        std::cout << cntr << "/" << lim << std::endl;
    }

    auto t2 = std::chrono::high_resolution_clock::now();

    test_outputs << "Executed " << cntr << " operations in "
            << std::chrono::duration_cast<std::chrono::milliseconds>(t2 - t1).
            count() << " ms" << std::endl;

    return true;
}

/*
void propagate_tle_3d() { //TODO find method to interface to java
    const std::string line1 =
            "1 41240U 16002A   25100.23333006  .00000004  00000-0  28186-3 0  9990";
    const std::string line2 =
            "2 41240  66.0422 314.5979 0007637 273.0322  86.9819 12.80929746431684";
    interpret::TwoLineElement a(line1, line2);
    auto pos_tdm = a.get_position();
    auto vel_tdm = a.get_velocity();
    auto time = a.get_jd();
    std::vector<Eigen::Vector3d> positions;

    for (double dt = 0; dt <= 112.5 * 6; dt += 0.5) {
        auto r_ecef = a.get_position(dt) ;
        auto r_eci = utils::to_eci(r_ecef, time + dt * 60 / orbmath::SECONDS_PER_DAY);
        positions.push_back(r_eci/6378);
    }

    const int screenWidth = 1920 * 0.7 ;
    const int screenHeight = 1080 * 0.7;

    InitWindow(screenWidth, screenHeight,
               "raylib [core] example - 3d camera free");

    // Define the camera to look into our 3d world
    Camera3D camera = {0};
    camera.position = (Vector3){10.0f, 10.0f, 10.0f}; // Camera position
    camera.target = (Vector3){0.0f, 0.0f, 0.0f}; // Camera looking at point
    camera.up = (Vector3){0.0f, 1.0f, 0.0f};
    // Camera up vector (rotation towards target)
    camera.fovy = 45.0f; // Camera field-of-view Y
    camera.projection = CAMERA_PERSPECTIVE; // Camera projection type

    Vector3 cubePosition = {0.0f, 0.0f, 0.0f};

    DisableCursor(); // Limit cursor to relative movement inside the window

    SetTargetFPS(60); // Set our game to run at 60 frames-per-second
    //--------------------------------------------------------------------------------------

    // Main game loop
    while (!WindowShouldClose()) // Detect window close button or ESC key
    {
        // Update
        //----------------------------------------------------------------------------------
        UpdateCamera(&camera, CAMERA_FREE);

        if (IsKeyPressed('Z')) camera.target = (Vector3){0.0f, 0.0f, 0.0f};
        //----------------------------------------------------------------------------------

        // Draw
        //----------------------------------------------------------------------------------
        BeginDrawing();

        ClearBackground(RAYWHITE);

        BeginMode3D(camera);

        DrawSphere(cubePosition, 1.f, BLUE);
        auto n = positions.size();
        for (size_t i = 0; i < n; ++i) {
            Vector3 start = { (float)positions[i].x(), (float)positions[i].y(), (float)positions[i].z() };
            Vector3 end   = { (float)positions[(i + 1) % n].x(), (float)positions[(i + 1) % n].y(), (float)positions[(i + 1) % n].z() };
            DrawLine3D(start, end, RED);
        }

        DrawGrid(10, 1.0f);

        EndMode3D();

        DrawRectangle(10, 10, 320, 93, Fade(SKYBLUE, 0.5f));
        DrawRectangleLines(10, 10, 320, 93, BLUE);

        DrawText("Free camera default controls:", 20, 20, 10, BLACK);
        DrawText("- Mouse Wheel to Zoom in-out", 40, 40, 10, DARKGRAY);
        DrawText("- Mouse Wheel Pressed to Pan", 40, 60, 10, DARKGRAY);
        DrawText("- Z to zoom to (0, 0, 0)", 40, 80, 10, DARKGRAY);

        EndDrawing();
        //----------------------------------------------------------------------------------
    }

    // De-Initialization
    //--------------------------------------------------------------------------------------
    CloseWindow(); // Close window and OpenGL context
    //--------------------------------------------------------------------------------------
}


void test_rk45_integration() {

    auto tdms = interpret::parse_tdm_w(
                    "data/Jason/20240318_16002A_A*", 130, 5);
    std::cout << tdms.observations.size() << std::endl;
    auto radec = interpret::RADec(tdms.observations);

    auto r_init = radec.get_position();
    auto v_init = radec.get_velocity();
    auto jd_init = radec.m_epoch;
    std::vector<double> epochs;
    epochs.push_back(jd_init);
    for (int i = 0; i < 1000; i++) {
        epochs.push_back(epochs.back() + 0.001);
    }
    propagate::Propagator p(r_init,v_init, epochs, propagate::integrators::rk45_eci);
    p.compute();

    for (int i = 0; i < p.ephem.epochs.size(); i++) {
        std::cout << p.ephem.epochs[i] << ' ' << p.ephem.positions[i].transpose()
        << " | " << p.ephem.velocities[i].transpose() << std::endl;

        p.ephem.positions[i] = utils::to_eci(p.ephem.positions[i], p.ephem.epochs[i]);
        p.ephem.velocities[i] = utils::to_eci(p.ephem.velocities[i], p.ephem.epochs[i]);

    }

    std::vector<Eigen::Vector3d> positions = p.ephem.positions;

    for (int i = 0; i < positions.size(); i++) {
        positions[i] /= 6378;
    }

    const int screenWidth = 1920 * 0.7 ;
    const int screenHeight = 1080 * 0.7;

    InitWindow(screenWidth, screenHeight,
               "raylib [core] example - 3d camera free");

    // Define the camera to look into our 3d world
    Camera3D camera = {0};
    camera.position = (Vector3){10.0f, 10.0f, 10.0f}; // Camera position
    camera.target = (Vector3){0.0f, 0.0f, 0.0f}; // Camera looking at point
    camera.up = (Vector3){0.0f, 1.0f, 0.0f};
    // Camera up vector (rotation towards target)
    camera.fovy = 45.0f; // Camera field-of-view Y
    camera.projection = CAMERA_PERSPECTIVE; // Camera projection type

    Vector3 cubePosition = {0.0f, 0.0f, 0.0f};

    DisableCursor(); // Limit cursor to relative movement inside the window

    SetTargetFPS(60); // Set our game to run at 60 frames-per-second
    //--------------------------------------------------------------------------------------

    // Main game loop
    while (!WindowShouldClose()) // Detect window close button or ESC key
    {
        // Update
        //----------------------------------------------------------------------------------
        UpdateCamera(&camera, CAMERA_FREE);

        if (IsKeyPressed('Z')) camera.target = (Vector3){0.0f, 0.0f, 0.0f};
        //----------------------------------------------------------------------------------

        // Draw
        //----------------------------------------------------------------------------------
        BeginDrawing();

        ClearBackground(RAYWHITE);

        BeginMode3D(camera);

        DrawSphere(cubePosition, 1.f, BLUE);
        auto n = positions.size();
        for (size_t i = 0; i < n; ++i) {
            Vector3 start = { (float)positions[i].x(), (float)positions[i].y(), (float)positions[i].z() };
            Vector3 end   = { (float)positions[(i + 1) % n].x(), (float)positions[(i + 1) % n].y(), (float)positions[(i + 1) % n].z() };
            DrawLine3D(start, end, RED);
        }

        DrawGrid(10, 1.0f);

        EndMode3D();

        DrawRectangle(10, 10, 320, 93, Fade(SKYBLUE, 0.5f));
        DrawRectangleLines(10, 10, 320, 93, BLUE);

        DrawText("Free camera default controls:", 20, 20, 10, BLACK);
        DrawText("- Mouse Wheel to Zoom in-out", 40, 40, 10, DARKGRAY);
        DrawText("- Mouse Wheel Pressed to Pan", 40, 60, 10, DARKGRAY);
        DrawText("- Z to zoom to (0, 0, 0)", 40, 80, 10, DARKGRAY);

        EndDrawing();
        //----------------------------------------------------------------------------------
    }

    // De-Initialization
    //--------------------------------------------------------------------------------------
    CloseWindow(); // Close window and OpenGL context
    //-----------------------------------------------

}

void draw_combined_orbits() {
    // --- TLE propagation ---
    const std::string line1 = // TLE from 2024-03-19
            "1 41240U 16002A   24078.54273252 -.00000041  00000-0  87212-4 0  9991";
    const std::string line2 =
        "2 41240  66.0433  39.6041 0008216 275.2526  84.7552 12.80929447381890";


    interpret::TwoLineElement a(line1, line2);
    auto time = a.get_jd();
    // --- RK45 integration ---
    auto tdms = interpret::parse_tdm_w("data/Jason/20240318_16002A_A*", 130, 5);
    auto radec = interpret::RADec(tdms.observations);
    auto r_init = radec.get_position();
    auto v_init = radec.get_velocity();
    auto jd_init = radec.m_epoch;
    auto timediff = 28.5;
    std::vector<double> epochs = {};

    std::vector<Eigen::Vector3d> tle_positions;
    for (double dt = 0; dt <= 112.5 * 2; dt += 0.5) {
        auto r = a.get_position( + dt + timediff);
        tle_positions.push_back(r / 6378); // Normalize by Earth
        epochs.push_back( + dt * 60 / orbmath::SECONDS_PER_DAY);
    }


    propagate::Propagator p(r_init, v_init, epochs, propagate::integrators::rk45_eci  );
    p.compute();

    std::vector<Eigen::Vector3d> rk45_positions = p.ephem.positions;
    for (auto& r : rk45_positions) r /= 6378; // Normalize by Earth radius

    // --- Raylib visualization ---
    const int screenWidth = 1920 * 0.7;
    const int screenHeight = 1080 * 0.7;
    double limit = 0;
    InitWindow(screenWidth, screenHeight, "3D Orbits - TLE (Red) vs RK45 (Green)");

    Camera3D camera = {0};
    camera.position = {10.0f, 10.0f, 10.0f};
    camera.target = {0.0f, 0.0f, 0.0f};
    camera.up = {0.0f, 1.0f, 0.0f};
    camera.fovy = 45.0f;
    camera.projection = CAMERA_PERSPECTIVE;

    DisableCursor();
    SetTargetFPS(60);

    while (!WindowShouldClose()) {
        UpdateCamera(&camera, CAMERA_FREE);
        if (IsKeyPressed('Z')) camera.target = {0.0f, 0.0f, 0.0f};
        if (IsKeyDown('L')) {
            limit += 0.01;
            if (limit > 1) limit = 1;
            WaitTime(0.1);
        }

        if (IsKeyDown('I')) {
            timediff += 1;
            tle_positions.clear();
            for (double dt = 0; dt <= 112.5 * 2; dt += 0.5) {
                auto r = a.get_position(dt + timediff);
                tle_positions.push_back(r / 6378); // Normalize by Earth
            }
            WaitTime(0.01);
            std::cout<< timediff << std::endl;

        }

        if (IsKeyDown('K')) {
            timediff -= 1;
            tle_positions.clear();
            for (double dt = 0; dt <= 112.5 * 2; dt += 0.5) {
                auto r = a.get_position(dt + timediff);
                tle_positions.push_back(r / 6378); // Normalize by Earth
            }
            WaitTime(0.01);
            std::cout<< timediff << std::endl;
        }

        if (IsKeyDown('J')) {
            limit -= 0.01;
            if (limit < 0) limit = 0;
            WaitTime(0.1);
        }

        BeginDrawing();
        ClearBackground(RAYWHITE);
        BeginMode3D(camera);

        DrawSphere({0.0f, 0.0f, 0.0f}, 1.f, BLUE); // Earth

        // Draw TLE-based orbit (red)
        for (size_t i = 0; i < tle_positions.size() * limit; ++i) {
            Vector3 start = {(float)tle_positions[i].x(), (float)tle_positions[i].y(), (float)tle_positions[i].z()};
            Vector3 end = {(float)tle_positions[(i + 1) % tle_positions.size()].x(),
                           (float)tle_positions[(i + 1) % tle_positions.size()].y(),
                           (float)tle_positions[(i + 1) % tle_positions.size()].z()};
            DrawLine3D(start, end, RED);
        }

        // Draw RK45-based orbit (green)
        for (size_t i = 0; i < rk45_positions.size() * limit; ++i) {
            Vector3 start = {(float)rk45_positions[i].x(), (float)rk45_positions[i].y(), (float)rk45_positions[i].z()};
            Vector3 end = {(float)rk45_positions[(i + 1) % rk45_positions.size()].x(),
                           (float)rk45_positions[(i + 1) % rk45_positions.size()].y(),
                           (float)rk45_positions[(i + 1) % rk45_positions.size()].z()};
            DrawLine3D(start, end, GREEN);
        }

        DrawGrid(10, 1.0f);
        EndMode3D();

        DrawRectangle(10, 10, 360, 110, Fade(SKYBLUE, 0.5f));
        DrawRectangleLines(10, 10, 360, 110, BLUE);
        DrawText("Free camera controls:", 20, 20, 10, BLACK);
        DrawText("- Mouse Wheel: Zoom in/out", 40, 40, 10, DARKGRAY);
        DrawText("- Mouse Wheel Pressed: Pan", 40, 60, 10, DARKGRAY);
        DrawText("- Z to re-center on origin", 40, 80, 10, DARKGRAY);
        DrawText("TLE: RED | RK45: GREEN", 40, 100, 10, DARKGRAY);

        EndDrawing();
    }

    CloseWindow();
}
*/

/*
1 41240U 16002A   24078.93311235 -.00000041  00000-0  88455-4 0  9998
2 41240  66.0433  38.7934 0008217 275.1931  84.8147 12.80929479381943

1 41240U 16002A   24078.54273252 -.00000041  00000-0  87212-4 0  9991
2 41240  66.0433  39.6041 0008216 275.2526  84.7552 12.80929447381890
 */
void test_orbital_element_err() {
    for (int combi = 0; combi < 16; ++combi) {
        // const std::string line1 = // TLE from 2024-03-19
        //     "1 41240U 16002A   24078.54273252 -.00000041  00000-0  87212-4 0  9991";
        // const std::string line2 =
        //     "2 41240  66.0433  39.6041 0008216 275.2526  84.7552 12.80929447381890";


        interpret::TwoLineElement tle("tle_jason3.json", 2);
        double jd0 = tle.get_jd();
        auto tdms = interpret::parse_tdm_w(
                      "data/Jason/20240318_16002A_A*", 100, 30);
        std::cout << tdms.observations.size() << std::endl;
        auto radec = interpret::RADec(tdms.observations);

        // Initialize state vector with r, v Gauss
        auto r_init = radec.get_position();
        auto v_init = radec.get_velocity();
        auto jd_init = radec.m_epoch; // the epoch of the Gauss output (i.e. 2nd obs)
        std::cout << abs(jd_init - jd0 )* orbmath::SECONDS_PER_DAY / 60.0 << std::endl;

        std::vector<double> epochs; // time of integration of RK45
        std::vector<double> tle_epochs; // time of propagation TLE
        auto offmins = 28.5;


        std::vector<Eigen::Vector3d> r_tle;
        std::vector<Eigen::Vector3d> v_tle;
        std::vector<Eigen::Vector3d> r_rk45;
        std::vector<Eigen::Vector3d> v_rk45;

        // Propagate TLE with SGP4 for 10 orbits of Jason3
        for (double dt = 0; dt <= 112.5*10; dt+=0.5) {
            r_tle.push_back(tle.get_position(offmins + dt));
            v_tle.push_back(tle.get_velocity(offmins + dt));

            // epochs stores the time step for RK45 at the same time
            // with the propagation of the TLE state vector
            epochs.push_back(jd_init + dt * 60.0 / orbmath::SECONDS_PER_DAY);
            tle_epochs.push_back(jd_init + dt * 60.0 / orbmath::SECONDS_PER_DAY);
        }

        // The calculations are done in ECI frame, the propagator writes all state
        // vectors and accelerations in terms of ECI frame
        propagate::Propagator rk45(r_init, v_init, epochs, propagate::integrators::rk45_eci);
        rk45.j2 = combi & 0b0001;
        rk45.tb = combi & 0b0010;
        rk45.solar = combi & 0b0100;
        rk45.atm_exp = combi & 0b1000;
        rk45.compute();

        for (size_t i = 0; i < epochs.size(); ++i) {
            r_rk45.push_back(rk45.ephem.positions[i]);
            v_rk45.push_back(rk45.ephem.velocities[i]);
        }

        std::ostringstream oe_csv_name("");
        oe_csv_name << "log_orbital_elem/_oe_err_" << combi << ".csv"; //TODO create folder if does not exist
        std::ofstream oe_csv(oe_csv_name.str());
        oe_csv_name << ".log";
        std::ofstream oe_log(oe_csv_name.str());

        oe_csv << "TLE_EPOCH,Epoch,tle_a,tle_e,tle_i,tle_O,tle_omega,tle_m,rk45_a,rk45_e,rk45_i,rk45_O,rk45_omega,rk45_m,a_err,e_err,i_err,O_err,omega_err,m_err,x_tle,y_tle,z_tle,vx_tle,vy_tle,vz_tle,alt_tle,speed_tle,x_rk45,y_rk45,z_rk45,vx_rk45,vy_rk45,vz_rk45,alt_rk45,speed_rk45,x_err,y_err,z_err,alt_err,speed_err\n";
        for (size_t i = 0; i < epochs.size(); ++i) {
            if (epochs[i] < jd0) continue;
            // if (tle_epochs[i] > epochs[epochs.size()] ) continue;
            oe_log << "DEBUG: state vector TLE: " << r_tle[i].transpose() << ' ' << v_tle[i].transpose() << std::endl;
            oe_log << "DEBUG: state vector RK45: " << r_rk45[i].transpose() << ' ' << v_rk45[i].transpose() << std::endl;
            auto oe_tle = orbmath::compute_orbital_elements(r_tle[i],v_tle[i]);
            auto oe_rk45 = orbmath::compute_orbital_elements(r_rk45[i],v_rk45[i]);
            oe_csv << std::setprecision(14) << std::scientific
            << tle_epochs[i] << ',' << epochs[i]
            << ',' <<  oe_tle.a << ',' << oe_tle.ecc << ',' << oe_tle.incl
            << ',' << oe_tle.Omega<< ',' << oe_tle.omega << ',' << oe_tle.m
            << ',' << oe_rk45.a << ',' << oe_rk45.ecc << ',' << oe_rk45.incl
            << ',' << oe_rk45.Omega<< ',' << oe_rk45.omega << ',' << oe_rk45.m
            << ',' << abs(oe_tle.a - oe_rk45.a) << ',' << abs(oe_tle.ecc - oe_rk45.ecc)
            << ',' << abs(oe_tle.incl - oe_rk45.incl) << ',' << abs(oe_tle.Omega - oe_rk45.Omega)
            << ',' << abs(oe_tle.omega - oe_rk45.omega) << ',' << abs(oe_tle.m - oe_rk45.m)
            << ',' << r_tle[i].x() << ',' << r_tle[i].y() << ',' << r_tle[i].z()
            << ',' << v_tle[i].x() << ',' << v_tle[i].y() << ',' << v_tle[i].z()
            << ',' << r_tle[i].norm() << ',' << v_tle[i].norm()
            << ',' << r_rk45[i].x() << ',' << r_rk45[i].y() << ',' << r_rk45[i].z()
            << ',' << v_rk45[i].x() << ',' << v_rk45[i].y() << ',' << v_rk45[i].z()
            << ',' << r_rk45[i].norm() << ',' << v_rk45[i].norm()
            << ',' << abs(r_tle[i].x() - r_rk45[i].x()) << ',' << abs(r_tle[i].y() - r_rk45[i].y()) << ',' << abs(r_tle[i].z() - r_rk45[i].z())
            << ',' << abs(r_tle[i].norm() - r_rk45[i].norm()) << ',' << abs(v_tle[i].norm() - v_rk45[i].norm()) << std::endl;
        }
    }
}

int main() {
    // visual_test_gauss_tdm_benchmark();
    // gauss_tle_altitude_test();
    // propagate_tle_3d();

    // test_rk45_integration();
    test_orbital_element_err();

    // draw_combined_orbits();
    // test_sgp4_vs_rk45_propagation();
    // test_orbital_element_mse_rk45_vs_sgp4();

}

