# A simplified Python SDK for the Dobot Magician using official DLLs.
# Designed for educational purposes (secondary/VET).
# Executes commands synchronously (waits for completion).
# Create by Raidell Avello - with help of Gemini

# Import DobotDllType
import DobotDllType as dType

# --- Global variables --- (Keep these as they were)
api = None
is_connected = False
last_index = 0 # To store the index of the last command queued

# --- Internal Helper Functions ---

def _load_api():
    """Loads the Dobot DLL API if not already loaded."""
    global api
    if api is None:
        try:
            api = dType.load()
            print("Dobot DLL API loaded successfully.")
        except Exception as e:
            print(f"Error loading Dobot DLL: {e}")
            api = None # Ensure api is None if loading failed
    return api is not None

def _wait_for_command(command_index):
    """Waits until the specified command index is processed."""
    if not api or not is_connected:
        print("Error: Not connected to Dobot.")
        return False
    
    # print(f"Waiting for command index: {command_index}")
    while True:
        current_index = dType.GetQueuedCmdCurrentIndex(api)[0]
        # print(f"Current index: {current_index}")
        if current_index >= command_index:
            # print(f"Command {command_index} completed.")
            break
        dType.dSleep(100) # Wait 100ms to avoid high CPU usage
    
    # Stop execution after waiting (good practice)
    dType.SetQueuedCmdStopExec(api)
    return True

def _execute_command(cmd_func, *args, **kwargs):
    """Executes a Dobot command function and waits for completion."""
    global last_index
    if not api or not is_connected:
        print("Error: Cannot execute command - Not connected.")
        return False

    # Always clear the queue before sending a new command for sync execution
    dType.SetQueuedCmdClear(api)

    # Add isQueued=1 to the arguments for the command function
    kwargs['isQueued'] = 1
    
    # Call the underlying Dobot function (e.g., dType.SetPTPCmd)
    result = cmd_func(api, *args, **kwargs)
    
    # Check if the command function returned a valid index
    if isinstance(result, (list, tuple)) and len(result) > 0:
        last_index = result[0]
        if last_index == 0 and dType.DobotCommunicate.DobotCommunicate_BufferFull:
             print("Error: Command buffer full. Retrying might help.")
             # Optional: Add retry logic here if needed
             return False
        elif last_index > 0 :
             # Start execution of the single command in the queue
             dType.SetQueuedCmdStartExec(api)
             # Wait for the command to complete
             return _wait_for_command(last_index)
        else:
            print(f"Error: Command failed or returned invalid index {last_index}.")
            return False
    else:
        # Handle cases where the command doesn't return an index or failed
        print(f"Error: Command function {cmd_func.__name__} did not return expected index. Result: {result}")
        # Some parameter setting functions might return [0] on success without queuing
        # Let's consider this a success if no exception occured and is_connected is true
        # We won't wait in this case.
        if result == [0]: # Example check, might need adjustment based on specific functions
             print("Command likely succeeded (returned [0]), not waiting.")
             return True
        return False


# --- Public API Functions ---

def connect():
    """
    Connects to the Dobot Magician.
    Searches for the first available Dobot on serial ports and connects at 115200 baud.
    Sets default motion parameters upon successful connection.
    Returns:
        bool: True if connection is successful, False otherwise.
    """
    global api, is_connected, last_index
    
    if is_connected:
        print("Already connected.")
        return True

    if not _load_api():
        return False

    print("Searching for Dobot...")
    # Search for Dobot ports (use the function from DobotDllType)
    search_result = dType.SearchDobot(api)
    print(f"Search Result: {search_result}")

    if not search_result:
        print("Error: No Dobot Magician found on serial ports.")
        return False

    # Connect to the first Dobot found
    port = search_result[0]
    print(f"Connecting to Dobot on port: {port}...")
    # ConnectDobot returns: [state, masterDevType, slaveDevType, fwName, fwVer, masterId, slaveId, runTime]
    connect_result = dType.ConnectDobot(api, port, 115200)
    state = connect_result[0]

    # Use the CON_STR dictionary if available, otherwise map manually
    # Let's define it here for clarity if not importing DobotControl fully
    CON_STR = {
        dType.DobotConnect.DobotConnect_NoError:  "Connected successfully",
        dType.DobotConnect.DobotConnect_NotFound: "Error: Dobot not found or port unavailable",
        dType.DobotConnect.DobotConnect_Occupied: "Error: Dobot port occupied"
    }
    
    print(f"Connection status: {CON_STR.get(state, 'Unknown error')}")

    if state == dType.DobotConnect.DobotConnect_NoError:
        is_connected = True
        print("Connection successful.")
        
        # --- Set Initial Parameters (Crucial!) ---
        print("Setting initial parameters...")
        # Clean Command Queued
        dType.SetQueuedCmdClear(api)
        
        # Async Motion Params Setting - use isQueued=1 as per original example
        # We don't need to wait for parameter settings to finish immediately
        dType.SetHOMEParams(api, 200, 0, 50, 0, isQueued = 1) # Example HOME position
        # Set standard PTP joint parameters (velocity and acceleration)
        dType.SetPTPJointParams(api, 200, 200, 200, 200, 200, 200, 200, 200, isQueued = 1)
        # Set standard PTP coordinate parameters (velocity and acceleration)
        dType.SetPTPCoordinateParams(api, 100, 100, 100, 100, isQueued=1)
        # Set standard PTP common parameters (velocity/acceleration ratios)
        dType.SetPTPCommonParams(api, 50, 50, isQueued = 1) # Use 50% speed/accel ratio

        # Although parameters are queued, start execution to process them.
        # We retrieve the last index from the last parameter set command.
        last_param_index = dType.GetQueuedCmdCurrentIndex(api)[0] # Get index *before* starting
        dType.SetQueuedCmdStartExec(api)
        
        # Optional: Wait briefly for parameters to be processed if needed,
        # but usually not required as subsequent commands will wait anyway.
        # print(f"Waiting for parameter setup (index: {last_param_index})...")
        # _wait_for_command(last_param_index + 3) # Wait for the 3 param commands (+1 for safety) 
        print("Initial parameters set.")
        last_index = dType.GetQueuedCmdCurrentIndex(api)[0] # Reset last_index after setup
        
        return True
    else:
        is_connected = False
        api = None # Disconnect fully if connection failed
        return False

def disconnect():
    """
    Turns off the end effector and then disconnects from the Dobot Magician.
    """
    global api, is_connected
    
    # Check connection status first
    if not api or not is_connected:
        print("Not connected.")
        # Ensure state is consistent even if already disconnected
        is_connected = False
        api = None
        return

    print("--- Preparing to Disconnect ---")
    
    # --- Cleanup Step: Explicitly turn OFF the end effector ---
    # Choose based on the most likely used end effector or add logic later
    print("DEBUG: Turning OFF Suction Cup (pre-disconnect cleanup)...")
    try:
        # Attempt to turn OFF suction cup (most common issue)
        # Use isQueued=0 for direct execution if possible, otherwise use _execute_command
        # Let's use _execute_command for consistency, it handles queueing/waiting
        cleanup_success = _execute_command(dType.SetEndEffectorSuctionCup, enableCtrl=1, on=0)
        if cleanup_success:
             print("DEBUG: Suction cup OFF command processed.")
        else:
             print("DEBUG: Failed to turn OFF suction cup during cleanup (might be ok if not used).")
        
        # You might also want to ensure the gripper is off (open)
        # print("DEBUG: Setting Gripper to OFF/Open (pre-disconnect cleanup)...")
        # _execute_command(dType.SetEndEffectorGripper, enableCtrl=1, on=0)

        # Optional: Stop any other potential activity
        print("DEBUG: Stopping and clearing command queue (final)...")
        dType.SetQueuedCmdStopExec(api)
        dType.SetQueuedCmdClear(api)
        dType.dSleep(100) # Short pause after cleanup

    except Exception as e:
        print(f"Warning: Exception during pre-disconnect cleanup: {e}")
    # --- End of Cleanup Step ---

    print("Attempting to disconnect from Dobot...")
    try:
        # Now call the actual disconnect function from the DLL
        dType.DisconnectDobot(api)
        print("Disconnect command sent to Dobot.")
    except Exception as e:
         print(f"Exception during Dobot disconnect call: {e}")
    finally:
        # Regardless of errors during cleanup or disconnect call, reset library state
        is_connected = False
        api = None # Release the API object
        print("--- Disconnected (library state cleaned). ---")

def home():
    """Moves the Dobot Magician to its HOME position."""
    print("Moving to HOME position...")
    if _execute_command(dType.SetHOMECmd, temp=0):
         print("HOME command finished.")
         return True
    else:
         print("HOME command failed.")
         return False

def move_to(x, y, z, r):
    """
    Moves the Dobot Magician to the specified cartesian coordinates.
    Uses PTP (Point-to-Point) linear movement mode (PTPMOVLXYZMode).
    Args:
        x (float): X coordinate.
        y (float): Y coordinate.
        z (float): Z coordinate.
        r (float): R (rotation head) coordinate.
    """
    print(f"Moving to (X:{x}, Y:{y}, Z:{z}, R:{r})...")
    if _execute_command(dType.SetPTPCmd, 
                        ptpMode=dType.PTPMode.PTPMOVLXYZMode, 
                        x=float(x), 
                        y=float(y), 
                        z=float(z), 
                        rHead=float(r)):
         print("Move command finished.")
         return True
    else:
         print("Move command failed.")
         return False

def set_gripper(open_state):
    """
    Controls the Dobot Magician's gripper.
    Args:
        open_state (bool): True to open the gripper, False to close it.
    """
    if open_state:
        print("Opening gripper...")
        # Gripper ON (energized) usually means CLOSED for standard Dobot gripper.
        # Gripper OFF (de-energized) usually means OPEN.
        # So, to OPEN, we set 'on' to 0.
        on_value = 0
    else:
        print("Closing gripper...")
        # To CLOSE, we set 'on' to 1.
        on_value = 1

    # enableCtrl=1 means the firmware controls the gripper state.
    if _execute_command(dType.SetEndEffectorGripper, enableCtrl=1, on=on_value):
        # Add a small delay AFTER command completion confirmation, 
        # as the physical action takes time.
        dType.dSleep(700) # Wait 700ms for gripper action
        print("Gripper command finished.")
        return True
    else:
        print("Gripper command failed.")
        return False
    
    
def set_suction_cup(on_state):
    """
    Controls the Dobot Magician's SUCTION CUP. Waits for completion.
    Args:
        on_state (bool): True to turn SUCTION ON, False to turn SUCTION OFF.
    """
    action = "ON" if on_state else "OFF"
    # Suction cup: ON (1) = Suction Active, OFF (0) = Suction Inactive
    on_value = 1 if on_state else 0
    print(f"--- Executing SET_SUCTION_CUP ({action}) ---")

    # enableCtrl=1 means firmware controls the IO based on 'on' state.
    if _execute_command(dType.SetEndEffectorSuctionCup, enableCtrl=1, on=on_value):
        # Suction cup activation/deactivation is usually faster than gripper
        print("DEBUG: Waiting for physical suction cup action...")
        dType.dSleep(300) # Adjust if needed (might not be necessary)
        print(f"--- SET_SUCTION_CUP ({action}) command finished successfully. ---")
        return True
    else:
        print(f"--- SET_SUCTION_CUP ({action}) command failed. ---")
        return False

# Optional: Add a function to get current position if needed later
def get_pose():
    """
    Gets the current pose of the Dobot Magician.
    Returns:
        list: [x, y, z, r, j1, j2, j3, j4] or None if failed.
    """
    if not api or not is_connected:
        print("Error: Not connected.")
        return None
    
    # GetPose doesn't use the command queue, it's a direct query
    pose = dType.GetPose(api) 
    # Ensure pose contains valid data (check length or specific values if needed)
    if isinstance(pose, list) and len(pose) == 8:
        # print(f"Current Pose: X:{pose[0]:.2f}, Y:{pose[1]:.2f}, Z:{pose[2]:.2f}, R:{pose[3]:.2f}")
        return pose
    else:
        print(f"Error getting pose. Received: {pose}")
        return None

