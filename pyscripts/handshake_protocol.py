import time
import math
from helpers.classes import *
import threading

# Motor related values
Motor_ids = {'shoulder_tilt':11, 'shoulder_roll':12, 'shoulder_pan':16,
                 'elbow_tilt':14, 'elbow_pan':15, 'wrist_tilt':2, 'wrist_roll':17,
                 'gripper':13 }
Grip_closed = 1430
Grip_Open = 900
Wristroll_neutral = 2250
#Wrist_up = 2620
#Wrist_down = 1630
Wristtilt_neutral = 2020
Elbow_relaxed = 1800
Elbow_mean = 2300 # 2000 exp decay shake
Elbow_max_amplitude = 300#800 500
Shoulder_up   = 2100 #1900
Shoulder_down = 1550 #1550

def arm_startup_position(handler):
    id_list   = [Motor_ids['shoulder_tilt'], Motor_ids['shoulder_roll'], Motor_ids['shoulder_pan'],
                 Motor_ids['elbow_tilt'], Motor_ids['elbow_pan'],
                 Motor_ids['wrist_tilt'], Motor_ids['wrist_roll'] ]
    goal_list = [Shoulder_up, 2048, 1018,
                 Elbow_mean, 2020,
                 Wristtilt_neutral, Wristroll_neutral]
    handler.move_motors_to_goals_list(id_list, goal_list)
    #handler.move_motor_to_goal(Motor_ids['shoulder_tilt'], Shoulder_up)
    #handler.move_motor_to_goal(Motor_ids['shoulder_roll'], 2048)
    #handler.move_motor_to_goal(Motor_ids['shoulder_pan'], 1018)
    #handler.move_motor_to_goal(Motor_ids['elbow_tilt'], Elbow_mean)
    #handler.move_motor_to_goal(Motor_ids['elbow_pan'], 2020)
    #handler.move_motor_to_goal(Motor_ids['wrist_tilt'], 2650)
    #handler.move_motor_to_goal(Motor_ids['wrist_roll'], 2650)

def arm_closedown_position(handler):
    handler.move_motor_to_goal(Motor_ids['elbow_tilt'], Elbow_relaxed)
    handler.move_motor_to_goal(Motor_ids['shoulder_tilt'], Shoulder_down)
    handler.move_motor_to_goal(Motor_ids['wrist_tilt'], Wristtilt_neutral)
    handler.move_motor_to_goal(Motor_ids['wrist_roll'], Wristroll_neutral)

def setup_compliance(handler):
    handler.setup_motor_register_mode(Motor_ids['shoulder_tilt'], ADDR_OPERATING_MODE, 5)  # Complaint mode
    handler.setup_motor_register_mode(Motor_ids['shoulder_tilt'], ADDR_GOAL_CURRENT, 100)
    handler.setup_motor_register_mode(Motor_ids['wrist_tilt'], ADDR_OPERATING_MODE, 5)  # Complaint mode
    handler.setup_motor_register_mode(Motor_ids['wrist_tilt'], ADDR_GOAL_CURRENT, 50)

def setup_rigid(handler):
    handler.setup_motor_register_mode(Motor_ids['shoulder_tilt'], ADDR_OPERATING_MODE, 3)  # Complaint mode
    handler.setup_motor_register_mode(Motor_ids['wrist_tilt'], ADDR_OPERATING_MODE, 3)  # Complaint mode

def shaking_phase(handler, tactile=False):
    ''' Shaking based on elbow tilt axes
        Oscilation Point to Point with exponentially decrease amplitude
    '''
    elbow_motor = Motor_ids['elbow_tilt']
    wrist_motor = Motor_ids['wrist_tilt']
    n = 0
    points_cycle = 2
    while(n < 8):
        n_cycle = math.floor((n-1)/points_cycle)
        print(n)
        if n % 2 == 0:
            sign_amp = 1
        else:
            sign_amp = -1
        amplitude = sign_amp * Elbow_max_amplitude * math.exp(-n/4)
        handler.move_motors_to_goals_list([elbow_motor, wrist_motor], [int(Elbow_mean+amplitude), int(Wristtilt_neutral+amplitude)])
        # Adaptive to touch
        if tactile and handler.check_for_condition([Side, Palm],[2]):
            if n_cycle == -1:
                n += 1
            elif n_cycle == 0:
                n -= 1
            else:
                n = max(n - 3, 0)
        else:
            n += 1
    return

def handshake_protocol_tactile(handmotor_sub, wait_user=False):
    handmotor_sub.move_motor_to_goal(Motor_ids['gripper'], Grip_Open)
    print("REACHING: GIVE ME THAT HAND ")
    # Wait until somebody grab the hand -  side or palm in state 1 or 2
    handmotor_sub.wait_til_condition([Side, Palm], [1, 2])
    print("CONTACT - Activated Side/Palm - Gripper closing - I grab you yours")
    #_ = wait_user_feedback() if wait_user else ''
    # Close the hand until touch in thumb
    handmotor_sub.move_motor_til_signal(Motor_ids['gripper'], Grip_closed + 100, Thumb, debug=True)
    time.sleep(0.2)
    #_ = wait_user_feedback() if wait_user else ''
    print("CONTACT - Activated Thumb - Shaking")
    # start the shaking
    setup_compliance(handmotor_sub)
    shaking_phase(handmotor_sub, tactile=True)
    print("CONTACT - No Movement - Rapport LOOK AT EYES/ Message ...")
    time.sleep(0.52)
    #_ = wait_user_feedback() if wait_user else ''
    # Wait until increase in the pressure or release - Side or palm sensors in state 2
    #handmotor_sub.wait_til_condition([Side, Palm], [2])
    print("RETURN: Gripper To Open Position: My pleasure!")
    # Open hand to init
    print("RETURN: Release me, otherwise no return!")
    handmotor_sub.wait_til_condition([Side], [0])
    handmotor_sub.move_motor_to_goal(Motor_ids['gripper'], Grip_Open)
    _ = wait_user_feedback() if wait_user else ''
    return

def handshake_protocol(handmotor_sub, wait_user=False):
    handmotor_sub.move_motor_to_goal(Motor_ids['gripper'], Grip_Open)
    print("REACHING: GIVE ME THAT HAND ")
    # Wait until somebody grab the hand -  side or palm in state 1 or 2
    #handmotor_sub.wait_til_condition([Side, Palm], [1, 2])
    time.sleep(0.5)
    _ = wait_user_feedback() if wait_user else ''
    print("CONTACT - Activated Side/Palm - Gripper closing - I grab you yours")
    # Close the hand until touch in thumb
    #handmotor_sub.move_motor_til_signal(Motor_ids['gripper'], Grip_closed - 200, Thumb)
    handmotor_sub.move_motor_to_goal(Motor_ids['gripper'], Grip_closed)
    time.sleep(0.2)
    _ = wait_user_feedback() if wait_user else ''
    print("CONTACT - Activated Thumb - Shaking")
    # Inmediatly start the shaking
    setup_compliance(handmotor_sub)
    shaking_phase(handmotor_sub, tactile=False)   # TODO Signal based increase of time points and amplitude
    print("CONTACT - No Movement - Rapport LOOK AT EYES/ Message ...")
    time.sleep(0.52)
    _ = wait_user_feedback() if wait_user else ''
    #print("Close Position: Waitting for a good shake!")
    # Wait until increase in the pressure or release - Side or palm sensors in state 2
    #handmotor_sub.wait_til_condition([Side, Palm], [2])
    print("RETURN: Gripper To Open Position: My pleasure!")
    # Open hand to init
    handmotor_sub.move_motor_to_goal(Motor_ids['gripper'], Grip_Open)
    _ = wait_user_feedback() if wait_user else ''
    print("RETURN: Release me, otherwise no return!")
    #handmotor_sub.wait_til_condition([Side], [0])
    return

def wait_user_feedback():
    print("Press any key to start the protocol! (or press q to quit!)")
    if getch() == chr(27):
        print("IN")
        return True
    print("OUT")
    return False

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
    handmotor_sub.move_motor_to_goal(Grip_Open)
    print("Release me!")
    handmotor_sub.wait_til_condition([Side], [0])
    return

def main():
    # Check if filename is provided as an argument
    if len(sys.argv) != 2:
        print("Usage: python script_name.py <file_name>")
        sys.exit(1)
    file_name = sys.argv[1]  # Get the file name from command line arguments

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
        handshake_protocol_tactile(handmotor_sub, wait_user=True)
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
    handsense_topic = SensorStatus(file_name, debug=False, serial_port="/dev/ttyACM0")
    sensor = threading.Thread(name="Sensor_Reading", target=handsense_topic.start_sensor_reading, kwargs={'debug':True})
    sensor.start()
    wait_user_feedback()

    handsense_topic.clean_sensor_reading()
    sensor.join()

def test_motors():
    all_motor_ids = list(Motor_ids.values())

    handmotor_sub = MotorClamp(all_motor_ids, debug=False, serial_port="/dev/ttyUSB0")

    arm_startup_position(handmotor_sub)
    time.sleep(5)
    while True:
        handmotor_sub.move_motors_to_goals_list([Motor_ids['wrist_roll'], Motor_ids['gripper']], [Wristroll_neutral, Grip_Open])
        time.sleep(2)
        handmotor_sub.move_motors_to_goals_list([Motor_ids['wrist_roll'], Motor_ids['gripper']], [Wristroll_neutral+500, Grip_closed])
        time.sleep(10)

if __name__ == '__main__':
    #test_sensors()
    test_motors()
    main()
