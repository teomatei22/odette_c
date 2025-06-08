/*
 @licstart  The following is the entire license notice for the JavaScript code in this file.

 The MIT License (MIT)

 Copyright (C) 1997-2020 by Dimitri van Heesch

 Permission is hereby granted, free of charge, to any person obtaining a copy of this software
 and associated documentation files (the "Software"), to deal in the Software without restriction,
 including without limitation the rights to use, copy, modify, merge, publish, distribute,
 sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is
 furnished to do so, subject to the following conditions:

 The above copyright notice and this permission notice shall be included in all copies or
 substantial portions of the Software.

 THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING
 BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
 NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
 DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

 @licend  The above is the entire license notice for the JavaScript code in this file
*/
var NAVTREE =
[
  [ "ODETTE Python Interface", "index.html", [
    [ "API Reference", "d2/d89/api_reference.html", [
      [ "Core Classes", "d2/d89/api_reference.html#autotoc_md0", [
        [ "OrbitVisualizer", "d2/d89/api_reference.html#autotoc_md1", [
          [ "Constructor", "d2/d89/api_reference.html#autotoc_md2", null ],
          [ "Key Methods", "d2/d89/api_reference.html#autotoc_md3", [
            [ "visualize_tle()", "d2/d89/api_reference.html#autotoc_md4", null ],
            [ "visualize_rk45()", "d2/d89/api_reference.html#autotoc_md5", null ],
            [ "compare_orbits()", "d2/d89/api_reference.html#autotoc_md6", null ],
            [ "visualize_multiple_satellites()", "d2/d89/api_reference.html#autotoc_md7", null ]
          ] ],
          [ "Protected Methods", "d2/d89/api_reference.html#autotoc_md8", [
            [ "_setup_plot()", "d2/d89/api_reference.html#autotoc_md9", null ],
            [ "_plot_orbit()", "d2/d89/api_reference.html#autotoc_md10", null ]
          ] ]
        ] ],
        [ "OrbitPropagator", "d2/d89/api_reference.html#autotoc_md12", [
          [ "Constructor", "d2/d89/api_reference.html#autotoc_md13", null ],
          [ "Key Methods", "d2/d89/api_reference.html#autotoc_md14", [
            [ "propagate_tle()", "d2/d89/api_reference.html#autotoc_md15", null ],
            [ "propagate_rk45()", "d2/d89/api_reference.html#autotoc_md16", null ],
            [ "compare_orbital_elements()", "d2/d89/api_reference.html#autotoc_md17", null ],
            [ "set_perturbation_parameters()", "d2/d89/api_reference.html#autotoc_md18", null ],
            [ "get_perturbation_parameters()", "d2/d89/api_reference.html#autotoc_md19", null ]
          ] ]
        ] ],
        [ "JavaGUIBridge", "d2/d89/api_reference.html#autotoc_md21", [
          [ "Constructor", "d2/d89/api_reference.html#autotoc_md22", null ],
          [ "Key Methods", "d2/d89/api_reference.html#autotoc_md23", [
            [ "set_status_callback()", "d2/d89/api_reference.html#autotoc_md24", null ],
            [ "execute_command()", "d2/d89/api_reference.html#autotoc_md25", null ]
          ] ],
          [ "Protected Methods", "d2/d89/api_reference.html#autotoc_md26", [
            [ "_convert_to_serializable()", "d2/d89/api_reference.html#autotoc_md27", null ],
            [ "_create_success_response()", "d2/d89/api_reference.html#autotoc_md28", null ],
            [ "_create_error_response()", "d2/d89/api_reference.html#autotoc_md29", null ]
          ] ]
        ] ]
      ] ],
      [ "Data Structures", "d2/d89/api_reference.html#autotoc_md31", [
        [ "Orbital Elements Dictionary", "d2/d89/api_reference.html#autotoc_md32", null ],
        [ "Perturbations Configuration", "d2/d89/api_reference.html#autotoc_md33", null ],
        [ "Satellite Configuration", "d2/d89/api_reference.html#autotoc_md34", null ]
      ] ],
      [ "Constants and Defaults", "d2/d89/api_reference.html#autotoc_md36", [
        [ "Physical Constants", "d2/d89/api_reference.html#autotoc_md37", null ],
        [ "Default Parameters", "d2/d89/api_reference.html#autotoc_md38", null ],
        [ "Perturbation Defaults", "d2/d89/api_reference.html#autotoc_md39", null ]
      ] ],
      [ "Error Handling", "d2/d89/api_reference.html#autotoc_md41", [
        [ "Exception Types", "d2/d89/api_reference.html#autotoc_md42", null ],
        [ "Error Response Format (JavaGUIBridge)", "d2/d89/api_reference.html#autotoc_md43", null ],
        [ "Success Response Format (JavaGUIBridge)", "d2/d89/api_reference.html#autotoc_md44", null ]
      ] ]
    ] ],
    [ "Getting Started", "d1/d66/getting_started.html", [
      [ "Prerequisites", "d1/d66/getting_started.html#autotoc_md58", [
        [ "System Requirements", "d1/d66/getting_started.html#autotoc_md59", null ],
        [ "Required Python Packages", "d1/d66/getting_started.html#autotoc_md60", null ],
        [ "Optional Dependencies", "d1/d66/getting_started.html#autotoc_md61", null ]
      ] ],
      [ "Installation", "d1/d66/getting_started.html#autotoc_md62", [
        [ "1. Clone the Repository", "d1/d66/getting_started.html#autotoc_md63", null ],
        [ "2. Build the C++ Extension", "d1/d66/getting_started.html#autotoc_md64", [
          [ "On Windows", "d1/d66/getting_started.html#autotoc_md65", null ],
          [ "On Linux/macOS", "d1/d66/getting_started.html#autotoc_md66", null ]
        ] ],
        [ "3. Verify Installation", "d1/d66/getting_started.html#autotoc_md67", null ]
      ] ],
      [ "Basic Usage Examples", "d1/d66/getting_started.html#autotoc_md68", [
        [ "1. Simple TLE Visualization", "d1/d66/getting_started.html#autotoc_md69", null ],
        [ "2. Orbit Propagation with Analysis", "d1/d66/getting_started.html#autotoc_md70", null ],
        [ "3. High-Precision RK45 Propagation", "d1/d66/getting_started.html#autotoc_md71", null ],
        [ "4. Comparative Analysis", "d1/d66/getting_started.html#autotoc_md72", null ],
        [ "5. Multiple Satellite Visualization", "d1/d66/getting_started.html#autotoc_md73", null ]
      ] ],
      [ "Java Integration", "d1/d66/getting_started.html#autotoc_md74", [
        [ "Setting up the Bridge", "d1/d66/getting_started.html#autotoc_md75", null ],
        [ "Executing Commands from Java", "d1/d66/getting_started.html#autotoc_md76", null ]
      ] ],
      [ "Configuration Management", "d1/d66/getting_started.html#autotoc_md77", [
        [ "Setting Perturbation Parameters", "d1/d66/getting_started.html#autotoc_md78", null ]
      ] ],
      [ "Data Formats", "d1/d66/getting_started.html#autotoc_md79", [
        [ "TLE Format", "d1/d66/getting_started.html#autotoc_md80", null ],
        [ "TDM Files", "d1/d66/getting_started.html#autotoc_md81", null ]
      ] ],
      [ "Troubleshooting", "d1/d66/getting_started.html#autotoc_md82", [
        [ "Common Issues", "d1/d66/getting_started.html#autotoc_md83", null ],
        [ "Performance Tips", "d1/d66/getting_started.html#autotoc_md84", null ]
      ] ],
      [ "Next Steps", "d1/d66/getting_started.html#autotoc_md85", null ],
      [ "Need Help?", "d1/d66/getting_started.html#autotoc_md86", null ]
    ] ],
    [ "ODETTE Python Interface Documentation", "db/d8b/md_docs_2mainpage.html", [
      [ "Overview", "db/d8b/md_docs_2mainpage.html#autotoc_md88", null ],
      [ "🚀 Key Features", "db/d8b/md_docs_2mainpage.html#autotoc_md89", [
        [ "Core Capabilities", "db/d8b/md_docs_2mainpage.html#autotoc_md90", null ],
        [ "Perturbation Models", "db/d8b/md_docs_2mainpage.html#autotoc_md91", null ],
        [ "Data Formats", "db/d8b/md_docs_2mainpage.html#autotoc_md92", null ]
      ] ],
      [ "📚 Architecture", "db/d8b/md_docs_2mainpage.html#autotoc_md93", [
        [ "1. Core Classes", "db/d8b/md_docs_2mainpage.html#autotoc_md94", null ],
        [ "2. C++ Bindings", "db/d8b/md_docs_2mainpage.html#autotoc_md95", null ],
        [ "3. Supporting Modules", "db/d8b/md_docs_2mainpage.html#autotoc_md96", null ]
      ] ],
      [ "🎯 Quick Start", "db/d8b/md_docs_2mainpage.html#autotoc_md97", [
        [ "Basic Orbit Visualization", "db/d8b/md_docs_2mainpage.html#autotoc_md98", null ],
        [ "Advanced Propagation", "db/d8b/md_docs_2mainpage.html#autotoc_md99", null ],
        [ "Java Integration", "db/d8b/md_docs_2mainpage.html#autotoc_md100", null ]
      ] ],
      [ "📖 Documentation Structure", "db/d8b/md_docs_2mainpage.html#autotoc_md101", null ],
      [ "🔬 Scientific Applications", "db/d8b/md_docs_2mainpage.html#autotoc_md102", [
        [ "Orbital Mechanics", "db/d8b/md_docs_2mainpage.html#autotoc_md103", null ],
        [ "Research Areas", "db/d8b/md_docs_2mainpage.html#autotoc_md104", null ],
        [ "Educational Use", "db/d8b/md_docs_2mainpage.html#autotoc_md105", null ]
      ] ],
      [ "🛠 Technical Specifications", "db/d8b/md_docs_2mainpage.html#autotoc_md106", [
        [ "System Requirements", "db/d8b/md_docs_2mainpage.html#autotoc_md107", null ],
        [ "Performance Characteristics", "db/d8b/md_docs_2mainpage.html#autotoc_md108", null ],
        [ "Accuracy", "db/d8b/md_docs_2mainpage.html#autotoc_md109", null ]
      ] ],
      [ "🌟 Examples Gallery", "db/d8b/md_docs_2mainpage.html#autotoc_md110", null ],
      [ "🔗 Related Resources", "db/d8b/md_docs_2mainpage.html#autotoc_md111", null ],
      [ "📞 Support", "db/d8b/md_docs_2mainpage.html#autotoc_md112", null ]
    ] ],
    [ "Perturbation Models", "d0/dde/perturbations.html", [
      [ "Overview", "d0/dde/perturbations.html#autotoc_md114", null ],
      [ "Available Perturbation Models", "d0/dde/perturbations.html#autotoc_md115", [
        [ "1. J2 Earth Oblateness", "d0/dde/perturbations.html#j2-perturbation", [
          [ "Physical Description", "d0/dde/perturbations.html#autotoc_md116", null ],
          [ "Mathematical Model", "d0/dde/perturbations.html#autotoc_md117", null ],
          [ "Configuration", "d0/dde/perturbations.html#autotoc_md118", null ],
          [ "Typical Effects", "d0/dde/perturbations.html#autotoc_md119", null ],
          [ "Example Usage", "d0/dde/perturbations.html#autotoc_md120", null ]
        ] ],
        [ "2. Third-Body Perturbations", "d0/dde/perturbations.html#third-body", [
          [ "Physical Description", "d0/dde/perturbations.html#autotoc_md121", null ],
          [ "Mathematical Model", "d0/dde/perturbations.html#autotoc_md122", null ],
          [ "Lunar Position Model", "d0/dde/perturbations.html#autotoc_md123", null ],
          [ "Solar Position Model", "d0/dde/perturbations.html#autotoc_md124", null ],
          [ "Configuration", "d0/dde/perturbations.html#autotoc_md125", null ],
          [ "Typical Effects", "d0/dde/perturbations.html#autotoc_md126", null ],
          [ "Parameters", "d0/dde/perturbations.html#autotoc_md127", null ]
        ] ],
        [ "3. Solar Radiation Pressure", "d0/dde/perturbations.html#solar-radiation-pressure", [
          [ "Physical Description", "d0/dde/perturbations.html#autotoc_md128", null ],
          [ "Mathematical Model", "d0/dde/perturbations.html#autotoc_md129", null ],
          [ "Configuration", "d0/dde/perturbations.html#autotoc_md130", null ],
          [ "Parameter Guidelines", "d0/dde/perturbations.html#autotoc_md131", null ],
          [ "Typical Effects", "d0/dde/perturbations.html#autotoc_md132", null ],
          [ "Shadow Modeling", "d0/dde/perturbations.html#autotoc_md133", null ]
        ] ],
        [ "4. Atmospheric Drag", "d0/dde/perturbations.html#atmospheric-drag", [
          [ "Physical Description", "d0/dde/perturbations.html#autotoc_md134", null ],
          [ "Mathematical Model", "d0/dde/perturbations.html#autotoc_md135", null ],
          [ "Atmospheric Density Model", "d0/dde/perturbations.html#autotoc_md136", null ],
          [ "Default Atmospheric Parameters", "d0/dde/perturbations.html#autotoc_md137", null ],
          [ "Configuration", "d0/dde/perturbations.html#autotoc_md138", null ],
          [ "Drag Coefficient Guidelines", "d0/dde/perturbations.html#autotoc_md139", null ],
          [ "Altitude Effects", "d0/dde/perturbations.html#autotoc_md140", null ],
          [ "Typical Effects", "d0/dde/perturbations.html#autotoc_md141", null ]
        ] ]
      ] ],
      [ "Perturbation Interaction Effects", "d0/dde/perturbations.html#autotoc_md142", [
        [ "Combined Perturbations", "d0/dde/perturbations.html#autotoc_md143", null ],
        [ "Resonance Effects", "d0/dde/perturbations.html#autotoc_md144", [
          [ "Geosynchronous Resonances", "d0/dde/perturbations.html#autotoc_md145", null ],
          [ "Sun-synchronous Orbits", "d0/dde/perturbations.html#autotoc_md146", null ]
        ] ]
      ] ],
      [ "Mission-Specific Considerations", "d0/dde/perturbations.html#autotoc_md147", [
        [ "Low Earth Orbit (LEO)", "d0/dde/perturbations.html#autotoc_md148", null ],
        [ "Geostationary Earth Orbit (GEO)", "d0/dde/perturbations.html#autotoc_md149", null ],
        [ "Highly Elliptical Orbit (HEO)", "d0/dde/perturbations.html#autotoc_md150", null ]
      ] ],
      [ "Advanced Perturbation Modeling", "d0/dde/perturbations.html#autotoc_md151", [
        [ "Custom Perturbation Parameters", "d0/dde/perturbations.html#autotoc_md152", null ],
        [ "Validation Against Reference Models", "d0/dde/perturbations.html#autotoc_md153", null ]
      ] ],
      [ "Performance Considerations", "d0/dde/perturbations.html#autotoc_md154", [
        [ "Computational Cost", "d0/dde/perturbations.html#autotoc_md155", null ],
        [ "Adaptive Integration", "d0/dde/perturbations.html#autotoc_md156", null ]
      ] ],
      [ "Error Analysis and Uncertainty", "d0/dde/perturbations.html#autotoc_md157", [
        [ "Perturbation Parameter Uncertainties", "d0/dde/perturbations.html#autotoc_md158", null ]
      ] ],
      [ "Best Practices", "d0/dde/perturbations.html#autotoc_md159", [
        [ "1. Perturbation Selection", "d0/dde/perturbations.html#autotoc_md160", null ],
        [ "2. Parameter Estimation", "d0/dde/perturbations.html#autotoc_md161", null ],
        [ "3. Computational Efficiency", "d0/dde/perturbations.html#autotoc_md162", null ],
        [ "4. Validation and Testing", "d0/dde/perturbations.html#autotoc_md163", null ]
      ] ],
      [ "References and Further Reading", "d0/dde/perturbations.html#autotoc_md164", [
        [ "Fundamental References", "d0/dde/perturbations.html#autotoc_md165", null ],
        [ "Perturbation-Specific References", "d0/dde/perturbations.html#autotoc_md166", null ]
      ] ]
    ] ],
    [ "ODETTE Python Interface Documentation", "dc/dae/md__r_e_a_d_m_e___d_o_c_u_m_e_n_t_a_t_i_o_n.html", [
      [ "📁 Directory Structure", "dc/dae/md__r_e_a_d_m_e___d_o_c_u_m_e_n_t_a_t_i_o_n.html#autotoc_md168", null ],
      [ "🚀 Quick Start", "dc/dae/md__r_e_a_d_m_e___d_o_c_u_m_e_n_t_a_t_i_o_n.html#autotoc_md169", [
        [ "Generate Documentation", "dc/dae/md__r_e_a_d_m_e___d_o_c_u_m_e_n_t_a_t_i_o_n.html#autotoc_md170", null ],
        [ "View Documentation", "dc/dae/md__r_e_a_d_m_e___d_o_c_u_m_e_n_t_a_t_i_o_n.html#autotoc_md171", null ]
      ] ],
      [ "📋 Prerequisites", "dc/dae/md__r_e_a_d_m_e___d_o_c_u_m_e_n_t_a_t_i_o_n.html#autotoc_md172", [
        [ "Required Software", "dc/dae/md__r_e_a_d_m_e___d_o_c_u_m_e_n_t_a_t_i_o_n.html#autotoc_md173", null ],
        [ "Installation", "dc/dae/md__r_e_a_d_m_e___d_o_c_u_m_e_n_t_a_t_i_o_n.html#autotoc_md174", [
          [ "Windows", "dc/dae/md__r_e_a_d_m_e___d_o_c_u_m_e_n_t_a_t_i_o_n.html#autotoc_md175", null ],
          [ "macOS", "dc/dae/md__r_e_a_d_m_e___d_o_c_u_m_e_n_t_a_t_i_o_n.html#autotoc_md176", null ],
          [ "Linux (Ubuntu/Debian)", "dc/dae/md__r_e_a_d_m_e___d_o_c_u_m_e_n_t_a_t_i_o_n.html#autotoc_md177", null ]
        ] ],
        [ "Python Dependencies", "dc/dae/md__r_e_a_d_m_e___d_o_c_u_m_e_n_t_a_t_i_o_n.html#autotoc_md178", null ]
      ] ],
      [ "⚙️ Configuration", "dc/dae/md__r_e_a_d_m_e___d_o_c_u_m_e_n_t_a_t_i_o_n.html#autotoc_md179", [
        [ "Doxyfile Settings", "dc/dae/md__r_e_a_d_m_e___d_o_c_u_m_e_n_t_a_t_i_o_n.html#autotoc_md180", null ],
        [ "Customization Options", "dc/dae/md__r_e_a_d_m_e___d_o_c_u_m_e_n_t_a_t_i_o_n.html#autotoc_md181", null ]
      ] ],
      [ "📝 Documentation Structure", "dc/dae/md__r_e_a_d_m_e___d_o_c_u_m_e_n_t_a_t_i_o_n.html#autotoc_md182", [
        [ "Main Pages", "dc/dae/md__r_e_a_d_m_e___d_o_c_u_m_e_n_t_a_t_i_o_n.html#autotoc_md183", null ],
        [ "Examples Collection", "dc/dae/md__r_e_a_d_m_e___d_o_c_u_m_e_n_t_a_t_i_o_n.html#autotoc_md184", null ],
        [ "Images and Diagrams", "dc/dae/md__r_e_a_d_m_e___d_o_c_u_m_e_n_t_a_t_i_o_n.html#autotoc_md185", null ]
      ] ],
      [ "🛠️ Advanced Usage", "dc/dae/md__r_e_a_d_m_e___d_o_c_u_m_e_n_t_a_t_i_o_n.html#autotoc_md186", [
        [ "Custom Documentation Generation", "dc/dae/md__r_e_a_d_m_e___d_o_c_u_m_e_n_t_a_t_i_o_n.html#autotoc_md187", null ],
        [ "Extending Documentation", "dc/dae/md__r_e_a_d_m_e___d_o_c_u_m_e_n_t_a_t_i_o_n.html#autotoc_md188", null ],
        [ "Documentation Best Practices", "dc/dae/md__r_e_a_d_m_e___d_o_c_u_m_e_n_t_a_t_i_o_n.html#autotoc_md189", null ]
      ] ],
      [ "🔧 Troubleshooting", "dc/dae/md__r_e_a_d_m_e___d_o_c_u_m_e_n_t_a_t_i_o_n.html#autotoc_md190", [
        [ "Common Issues", "dc/dae/md__r_e_a_d_m_e___d_o_c_u_m_e_n_t_a_t_i_o_n.html#autotoc_md191", null ],
        [ "Debug Mode", "dc/dae/md__r_e_a_d_m_e___d_o_c_u_m_e_n_t_a_t_i_o_n.html#autotoc_md192", null ],
        [ "Validation", "dc/dae/md__r_e_a_d_m_e___d_o_c_u_m_e_n_t_a_t_i_o_n.html#autotoc_md193", null ]
      ] ],
      [ "📊 Statistics and Metrics", "dc/dae/md__r_e_a_d_m_e___d_o_c_u_m_e_n_t_a_t_i_o_n.html#autotoc_md194", [
        [ "Documentation Coverage", "dc/dae/md__r_e_a_d_m_e___d_o_c_u_m_e_n_t_a_t_i_o_n.html#autotoc_md195", null ],
        [ "Performance", "dc/dae/md__r_e_a_d_m_e___d_o_c_u_m_e_n_t_a_t_i_o_n.html#autotoc_md196", null ]
      ] ],
      [ "🤝 Contributing", "dc/dae/md__r_e_a_d_m_e___d_o_c_u_m_e_n_t_a_t_i_o_n.html#autotoc_md197", [
        [ "Adding Documentation", "dc/dae/md__r_e_a_d_m_e___d_o_c_u_m_e_n_t_a_t_i_o_n.html#autotoc_md198", null ],
        [ "Documentation Standards", "dc/dae/md__r_e_a_d_m_e___d_o_c_u_m_e_n_t_a_t_i_o_n.html#autotoc_md199", null ],
        [ "Review Process", "dc/dae/md__r_e_a_d_m_e___d_o_c_u_m_e_n_t_a_t_i_o_n.html#autotoc_md200", null ]
      ] ],
      [ "📞 Support", "dc/dae/md__r_e_a_d_m_e___d_o_c_u_m_e_n_t_a_t_i_o_n.html#autotoc_md201", [
        [ "Getting Help", "dc/dae/md__r_e_a_d_m_e___d_o_c_u_m_e_n_t_a_t_i_o_n.html#autotoc_md202", null ],
        [ "Useful Resources", "dc/dae/md__r_e_a_d_m_e___d_o_c_u_m_e_n_t_a_t_i_o_n.html#autotoc_md203", null ]
      ] ]
    ] ],
    [ "Namespaces", "namespaces.html", [
      [ "Namespace List", "namespaces.html", "namespaces_dup" ],
      [ "Namespace Members", "namespacemembers.html", [
        [ "All", "namespacemembers.html", null ],
        [ "Functions", "namespacemembers_func.html", null ]
      ] ]
    ] ],
    [ "Classes", "annotated.html", [
      [ "Class List", "annotated.html", "annotated_dup" ],
      [ "Class Index", "classes.html", null ],
      [ "Class Hierarchy", "hierarchy.html", "hierarchy" ],
      [ "Class Members", "functions.html", [
        [ "All", "functions.html", null ],
        [ "Functions", "functions_func.html", null ]
      ] ]
    ] ],
    [ "Files", "files.html", [
      [ "File List", "files.html", "files_dup" ]
    ] ]
  ] ]
];

var NAVTREEINDEX =
[
"annotated.html",
"d6/dd4/classorbit__toolkit_1_1_orbit_visualizer_ab734f8814570988be63278c8c61c881a.html#ab734f8814570988be63278c8c61c881a",
"namespaces.html"
];

var SYNCONMSG = 'click to disable panel synchronization';
var SYNCOFFMSG = 'click to enable panel synchronization';
var LISTOFALLMEMBERS = 'List of all members';