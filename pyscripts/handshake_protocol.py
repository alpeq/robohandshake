import time
import math
from helpers.robot_behaviour import *
import threading

def wait_user_feedback():
    print("Press any key to start the protocol! (or press q to quit!)")
    if getch() == chr(27):
        return True
    return False

def handshake_protocol_tactile(handmotor_sub, wait_user=False):
    handmotor_sub.move_motor_to_goal(Motor_ids['gripper'], Grip_open)
    print("REACHING: GIVE ME THAT HAND ")
    # Wait until somebody grab the hand -  side or palm in state 1 or 2
    handmotor_sub.wait_til_condition([Side, Palm], [1, 2, 3, 4, 5])
    print("CONTACT - Activated Side/Palm - Gripper closing - I grab you yours")
    # Close the hand until touch in thumb
    print("CONTACT - Activated Thumb - Shaking")
    # start the shaking
    setup_compliance(handmotor_sub)
    shaking_phase(handmotor_sub, tactile=True)
    print("CONTACT - No Movement - Rapport LOOK AT EYES/ Message ...")
    # Open hand to init
    print("RETURN: Release me, otherwise no return!")
    handmotor_sub.wait_til_condition([Side], [0, 1, 2, 3], debug=False)
    time.sleep(0.52)
    print("RETURN: Gripper To Open Position: My pleasure!")
    opengrip_2dof_thumb(handmotor_sub)
    return

def handshake_protocol_time(handmotor_sub, wait_user=False):
    handmotor_sub.move_motor_to_goal(Motor_ids['gripper'], Grip_open)
    print("REACHING: GIVE ME THAT HAND ")
    time.sleep(0.5)
    #_ = wait_user_feedback() if wait_user else ''
    print("CONTACT - I grab you yours and shake")
    # Close the hand until touch in thumb
    #handmotor_sub.move_motor_til_signal(Motor_ids['gripper'], Grip_closed - 200, Thumb)
    print("CONTACT - Activated Thumb - Shaking")
    # Inmediatly start the shaking
    setup_compliance(handmotor_sub)
    shaking_phase(handmotor_sub, tactile=False, osci_points=5)
    print("CONTACT - No Movement - Rapport LOOK AT EYES/ Message ...")
    time.sleep(0.52)
    print("RETURN: Gripper To Open Position: My pleasure!")
    opengrip_2dof_thumb(handmotor_sub)
    return


def old_protocol(handmotor_sub):
    print("Start: GIVE ME THAT HAND ")
    # Wait until somebody grab the hand -  side or palm in state 1 or 2
    handmotor_sub.wait_til_condition([Side, Palm], [1, 2])
    print("Activated Side/Palm: I grab you yours")
    # Close the hand until touch in thumb
    handmotor_sub.move_motor_til_signal(Grip_closed - 200, Thumb)
    print("Close Position: Waitting for a good shake!")
    # Wait until increase in the pressure or release - Side or palm sensors in state 2
    handmotor_sub.wait_til_condition([Side, Palm], [2])
    print("To Open Position: My pleasure!")
    time.sleep(1)
    # Open hand to init
    handmotor_sub.move_motor_to_goal(Grip_open)
    print("Release me!")
    handmotor_sub.wait_til_condition([Side], [0])
    return

def main():
    # Check if filename is provided as an argument
    if len(sys.argv) != 3 or sys.argv[2] not in ['tactile', 'time']:
        print("Usage: python script_name.py <file_name> <tactile|time>")
        sys.exit(1)
    file_name = sys.argv[1]  # Get the file name from command line arguments
    protocol = sys.argv[2]  # Get the file name from command line arguments
    # Wait to press button
    if wait_user_feedback():
        return

    # Setup motor-sensor
    all_motor_ids = list(Motor_ids.values())
    handsense_topic = SensorStatus(file_name, debug=False, serial_port="/dev/ttyACM0")
    handmotor_sub = MotorClamp(all_motor_ids, debug=False, serial_port="/dev/ttyUSB0")
    handsense_topic.attach(handmotor_sub)

    # Handshake Protocol
    sensor = threading.Thread(name="Sensor_Reading", target=handsense_topic.start_sensor_reading)
    sensor.start()
    while 1:
        setup_rigid(handmotor_sub)
        arm_startup_position(handmotor_sub)
        if protocol == "tactile":
            handshake_protocol_tactile(handmotor_sub, wait_user=False)
        elif protocol == "time":
            handshake_protocol_time(handmotor_sub, wait_user=False)
        else:
            print("error")
            return
        arm_retract_return(handmotor_sub)
        arm_closedown_position(handmotor_sub)
        print("****************************************\n"
              "DO YOU WANT MORE? \n")
        if wait_user_feedback():
            break

    handsense_topic.clean_sensor_reading()
    sensor.join()
    handaction_sub.cleanup_motor_list(all_motor_ids)

def test_sensors():
    # Check if filename is provided as an argument
    if len(sys.argv) != 2:
        print("Usage: python script_name.py <file_name>")
        sys.exit(1)
    file_name = sys.argv[1]  # Get the file name from command line arguments

    # Test
    # Setup motor-sensor
    all_motor_ids = list(Motor_ids.values())
    handsense_topic = SensorStatus(file_name, debug=False, serial_port="/dev/ttyACM0")
    handmotor_sub = MotorClamp(all_motor_ids, debug=False, serial_port="/dev/ttyUSB0")
    handsense_topic.attach(handmotor_sub)

    sensor = threading.Thread(name="Sensor_Reading", target=handsense_topic.start_sensor_reading, kwargs={'debug':False})
    sensor.start()
    while True:
        print("MOTOR READING STATES: {}".format(handmotor_sub.state_sensors))
        #wait_user_feedback()

    handsense_topic.clean_sensor_reading()
    sensor.join()


def test_motors():
    all_motor_ids = list(Motor_ids.values())

    handmotor_sub = MotorClamp(all_motor_ids, debug=False, serial_port="/dev/ttyUSB0")

    arm_startup_position(handmotor_sub)
    time.sleep(5)
    while True:
        handmotor_sub.move_motors_to_goals_list([Motor_ids['wrist_roll'], Motor_ids['gripper']],
                                                [Wristroll_open, Grip_open])
        time.sleep(2)
        closegrip_2dof_thumb(handmotor_sub)
        time.sleep(10)

if __name__ == '__main__':
    #test_sensors()
    #test_motors()
    main()
