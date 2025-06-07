# Installation Guide for Odette C

Follow the steps below to set up and run Odette C:

---

### Steps:

1. **Navigate to the Build Folder**  
    cd into the **build** folder.

2. **Run CMake**  
    In the CLI, run `cmake ..`.  
    (**YOU MUST HAVE A GCC COMPILER, THIS DOES NOT COMPILE ON MSVC**)

3. **Copy Library Files**  
    Copy the `.dll` files (if on Windows) or the `.so` files (if on Linux) from **lib** into build.

4. **Move Required Files**  
    Move the **constants.csv** and the **data** folder into the build folder.

5. **Optional Step**  
    You may move the **data**, **constants.csv**, and the DLL/so files, together with the executable, wherever you wish.

6. **Enjoy!**

---

Happy compiling!