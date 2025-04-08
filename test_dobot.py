# Example script to test the DM_SDK_mini library.

import dobotmagician as dobot # Import the simplified SDK
import time

print("--- Dobot Magician Mini SDK Test ---")

# Attempt to connect
if dobot.connect():
    print("\nConnection successful! Starting test sequence...")
    
    try:
        # 1. Go Home
        print("\nStep 1: Going Home")
        dobot.home()
        time.sleep(1) # Pause between steps

        # Get and print initial pose
        current_pose = dobot.get_pose()
        if current_pose:
             print(f"Current Pose after Home: X:{current_pose[0]:.2f}, Y:{current_pose[1]:.2f}, Z:{current_pose[2]:.2f}, R:{current_pose[3]:.2f}")


        # 2. Move to a specific point
        target_x, target_y, target_z, target_r = 145.49, -114.58, 47.45, -0.24
        print(f"\nStep 2: Moving to ({target_x}, {target_y}, {target_z}, {target_r})")
        dobot.move_to(target_x, target_y, target_z, target_r)
        time.sleep(1)
        
        current_pose = dobot.get_pose()
        if current_pose:
             print(f"Current Pose after Move: X:{current_pose[0]:.2f}, Y:{current_pose[1]:.2f}, Z:{current_pose[2]:.2f}, R:{current_pose[3]:.2f}")


        # 3. Close Gripper
        print("\nStep 3: Closing Gripper")
        dobot.set_suction_cup(on_state=False)
        time.sleep(1)

        # 4. Move to another point
        target_x, target_y, target_z, target_r = 200, -50, 0, 0
        print(f"\nStep 4: Moving to ({target_x}, {target_y}, {target_z}, {target_r})")
        dobot.move_to(target_x, target_y, target_z, target_r)
        time.sleep(1)
        
        current_pose = dobot.get_pose()
        if current_pose:
             print(f"Current Pose after Move: X:{current_pose[0]:.2f}, Y:{current_pose[1]:.2f}, Z:{current_pose[2]:.2f}, R:{current_pose[3]:.2f}")


        # 5. Open Gripper
        print("\nStep 5: Opening Gripper")
        dobot.set_suction_cup(on_state=True)
        time.sleep(1)

        # 6. Go Home again
        print("\nStep 6: Going Home")
        dobot.home()
        time.sleep(1)
        
        current_pose = dobot.get_pose()
        if current_pose:
             print(f"Current Pose after Home: X:{current_pose[0]:.2f}, Y:{current_pose[1]:.2f}, Z:{current_pose[2]:.2f}, R:{current_pose[3]:.2f}")

        # 7. Close Gripper
        print("\nStep 5: Closing Gripper")
        dobot.set_suction_cup(on_state=False)
        time.sleep(1)


        print("\nTest sequence finished successfully!")

    except Exception as e:
        print(f"\nAn error occurred during the test sequence: {e}")
    
    finally:
        # Always ensure disconnection
        print("\nDisconnecting...")
        dobot.disconnect()
        print("--- Test Complete ---")

else:
    print("\nConnection failed. Please check the Dobot connection and ensure no other software (like DobotStudio) is using the port.")
    print("--- Test Aborted ---")