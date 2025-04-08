# DM_SDK_mini - Simplified Dobot Magician Control Library

This folder contains a mini-library (`dobotmagician.py`) to control the Dobot Magician robotic arm using Python, directly interacting with the official Dobot DLLs. It's designed for educational purposes, providing simple, blocking functions.

**Version:** 1.0 (Date: YYYY-MM-DD)
**Author:** [Your Name/Department]

## Folder Contents

*   `/dll/DobotDll.dll`: The official 64-bit dynamic link library from Dobot. **Do not modify or move.**
*   `dobotmagician.py`: The simplified Python library you will import and use. Contains functions like `connect()`, `home()`, `move_to()`, `set_suction_cup()`, etc.
*   `DobotDllType.py`: A necessary support file containing low-level definitions for the DLL. **Do not modify.** You don't need to interact with this file directly.
*   `test_dobot.py`: A basic example script showing how to import and use the `dobotmagician` library. You can run this to quickly check if your setup is working.
*   `README.md`: This instruction file.

## How to Use This Library in Your Project

Follow these steps to use the `dobotmagician` library in your own Python scripts:

1.  **Copy This Folder:** Copy the *entire* `DM_SDK_mini` folder (including the `dll` subfolder and all `.py` files) to a convenient location on your computer. For example, you could place it in your `Documents` folder like this: `C:\Users\YourUsername\Documents\DobotLib`. **Remember the path** where you copied it.

2.  **Create Your Project Script:** Create your Python script (e.g., `my_robot_program.py`) in a *different* folder, for example, `C:\MyProjects\`.

3.  **Add Library Path to Your Script:** At the **very beginning** of your Python script (`my_robot_program.py`), you need to tell Python where to find the `dobotmagician` library you copied in step 1. Add the following code block:

    ```python
    # my_robot_program.py

    import sys
    import os
    import time # Import other modules you need, like time

    # --- IMPORTANT: Add the path to the Dobot Library ---
    # MODIFY THE LINE BELOW to the exact path where YOU copied the DM_SDK_mini folder!
    path_to_dobot_lib = r"C:\Users\YourUsername\Documents\DobotLib" # <--- CHANGE THIS PATH!!!

    # Check if the path exists (optional but recommended)
    if not os.path.isdir(path_to_dobot_lib):
        print(f"ERROR: Cannot find the Dobot library folder at: {path_to_dobot_lib}")
        print("Please update the 'path_to_dobot_lib' variable in your script.")
        sys.exit() # Stop if the library path is wrong

    # Add the path to Python's search paths
    if path_to_dobot_lib not in sys.path:
        sys.path.insert(0, path_to_dobot_lib)
        print(f"Dobot library path added: {path_to_dobot_lib}")
    # --- End of path addition ---

    # Now you can import the Dobot library
    try:
        import dobotmagician as robot # Use 'robot' (or any name you like) to call functions
    except ImportError:
        print("ERROR: Failed to import the 'dobotmagician' library.")
        print(f"Make sure 'dobotmagician.py' is inside the folder: {path_to_dobot_lib}")
        sys.exit()

    # --- Your Robot Control Code Starts Here ---

    print("Starting Dobot program...")

    if robot.connect(): # Connect to the first available Dobot
        print("Successfully connected to Dobot.")
        try:
            # Example sequence:
            print("Moving Home...")
            robot.home()
            time.sleep(1) # Pause for visibility

            print("Moving to point (230, 0, 20)...")
            robot.move_to(230, 0, 20, 0) # x, y, z, rotation
            time.sleep(1)

            print("Turning suction ON...")
            robot.set_suction_cup(on_state=True) # Turn suction ON
            time.sleep(1.5)

            print("Moving up...")
            robot.move_to(230, 0, 70, 0) # Move Z up
            time.sleep(1)

            print("Turning suction OFF...")
            robot.set_suction_cup(on_state=False) # Turn suction OFF
            time.sleep(1)

            print("Going Home again...")
            robot.home()
            time.sleep(1)

            print("Robot sequence finished.")

        except Exception as e:
            print(f"An error occurred during robot operation: {e}")

        finally:
            # IMPORTANT: Always disconnect when finished or if an error occurs
            print("Disconnecting from Dobot...")
            robot.disconnect()
    else:
        print("Failed to connect to the Dobot.")
        print("Ensure the robot is powered on, connected via USB,")
        print("and no other software (like DobotStudio) is using the connection.")

    print("Program ended.")
    ```

4.  **Modify `path_to_dobot_lib`:** In the code block you just added to your script, **change the path** in the line `path_to_dobot_lib = r"C:\Users\YourUsername\Documents\DobotLib"` to the actual location where you copied the `DM_SDK_mini` folder. Use the `r"..."` format (raw string) especially on Windows to handle backslashes correctly.

5.  **Use the Library:** Now you can use the functions provided by the library by calling `robot.function_name()`, for example:
    *   `robot.connect()`
    *   `robot.disconnect()`
    *   `robot.home()`
    *   `robot.move_to(x, y, z, r)`
    *   `robot.set_suction_cup(True)` / `robot.set_suction_cup(False)`
    *   `robot.set_gripper(True)` / `robot.set_gripper(False)` (True=Open, False=Close)
    *   `robot.get_pose()`

## Important Notes

*   **Dependencies:** This library requires a standard Python 3 installation (64-bit on Windows to match the DLL) and the Dobot Magician connected via USB. No external Python packages need to be installed (`pip install ...`).
*   **One Program at a Time:** Only one program can be connected to the Dobot via the DLL at any given time. Make sure DobotStudio, DobotLab, or any other control software is closed before running your script.
*   **Error Handling:** The example includes basic `try...except...finally` blocks. It's good practice to use these to ensure the robot disconnects even if your code encounters an error.
*   **Blocking Functions:** All movement and end-effector functions (`home`, `move_to`, `set_suction_cup`, etc.) are *blocking*. This means your Python script will pause and wait until the Dobot finishes the command before moving to the next line of code.

Happy coding!

---

## Credits

This simplified educational library was developed by:

**Raidell Avello Martínez**
*Researcher, Universidade da Coruña*

With assistance from Google Gemini.