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
#Wrist_up = 2620
#Wrist_down = 1630
Wrist_neutral = 2020
Elbow_relaxed = 1800
Elbow_mean = 2200 # 2000 exp decay shake
Elbow_max_amplitude = 400#800 500
Shoulder_up   = 2100 #1900
Shoulder_down = 1700 #1550

def arm_startup_position(handler):
    id_list   = [Motor_ids['shoulder_tilt'], Motor_ids['shoulder_roll'], Motor_ids['shoulder_pan'],
                 Motor_ids['elbow_tilt'], Motor_ids['elbow_pan'],
                 Motor_ids['wrist_tilt'], Motor_ids['wrist_roll'] ]
    goal_list = [Shoulder_up, 2048, 1018,
                 Elbow_mean, 2020,
                 Wrist_neutral, 2650]
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
    handler.move_motor_to_goal(Motor_ids['wrist_tilt'], Wrist_neutral)

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
    for n in range(8):
        if n % 2 == 0:
            sign_amp = 1
        else:
            sign_amp = -1

        amplitude = sign_amp * Elbow_max_amplitude * math.exp(-n/4)
        handler.move_motors_to_goals_list([elbow_motor, wrist_motor], [int(Elbow_mean+amplitude), int(Wrist_neutral+amplitude)])
        #handler.move_motor_to_goal(elbow_motor, int(Elbow_mean+amplitude))
        #handler.move_motor_to_goal(wrist_motor, wrist_goal)
        # handler.state_sensors if any in state==2 n = n-3 with max(n,0)
    return

def handshake_protocol_tactile(handmotor_sub):
    #TOCHECK COPY FROM NO TACTILE
    handmotor_sub.move_motor_to_goal(Motor_ids['gripper'], Grip_Open)
    print("REACHING: GIVE ME THAT HAND ")
    # Wait until somebody grab the hand -  side or palm in state 1 or 2
    handmotor_sub.wait_til_condition([Side, Palm], [1, 2])
    print("CONTACT - Activated Side/Palm - Gripper closing - I grab you yours")
    # Close the hand until touch in thumb
    handmotor_sub.move_motor_til_signal(Motor_ids['gripper'], Grip_closed - 200, Thumb)
    print("CONTACT - Activated Thumb - Shaking")
    # Inmediatly start the shaking
    handmotor_sub.setup_motor_register_mode(Motor_ids['shoulder_tilt'], ADDR_GOAL_CURRENT, 30)# Extra shoulder complaince
    shaking_phase(handmotor_sub, tactile=True)   # TODO Signal based increase of time points and amplitude
    print("CONTACT - No Movement - Rapport LOOK AT EYES/ Message ...")
    time.sleep(0.52)
    #print("Close Position: Waitting for a good shake!")
    # Wait until increase in the pressure or release - Side or palm sensors in state 2
    #handmotor_sub.wait_til_condition([Side, Palm], [2])
    print("RETURN: Gripper To Open Position: My pleasure!")
    # Open hand to init
    handmotor_sub.move_motor_to_goal(Motor_ids['gripper'], Grip_Open)
    print("RETURN: Release me, otherwise no return!")
    handmotor_sub.wait_til_condition([Side], [0])
    # TODO RETURN whole arm at same time?
    return

def handshake_protocol(handmotor_sub):
    handmotor_sub.move_motor_to_goal(Motor_ids['gripper'], Grip_Open)
    print("REACHING: GIVE ME THAT HAND ")
    # Wait until somebody grab the hand -  side or palm in state 1 or 2
    #handmotor_sub.wait_til_condition([Side, Palm], [1, 2])
    time.sleep(0.5)
    wait_user_feedback()
    print("CONTACT - Activated Side/Palm - Gripper closing - I grab you yours")
    # Close the hand until touch in thumb
    #handmotor_sub.move_motor_til_signal(Motor_ids['gripper'], Grip_closed - 200, Thumb)
    handmotor_sub.move_motor_to_goal(Motor_ids['gripper'], Grip_closed)
    time.sleep(0.2)
    wait_user_feedback()
    print("CONTACT - Activated Thumb - Shaking")
    # Inmediatly start the shaking
    setup_compliance(handmotor_sub)
    shaking_phase(handmotor_sub, tactile=False)   # TODO Signal based increase of time points and amplitude
    print("CONTACT - No Movement - Rapport LOOK AT EYES/ Message ...")
    time.sleep(0.52)
    wait_user_feedback()
    #print("Close Position: Waitting for a good shake!")
    # Wait until increase in the pressure or release - Side or palm sensors in state 2
    #handmotor_sub.wait_til_condition([Side, Palm], [2])
    print("RETURN: Gripper To Open Position: My pleasure!")
    # Open hand to init
    handmotor_sub.move_motor_to_goal(Motor_ids['gripper'], Grip_Open)
    wait_user_feedback()
    print("RETURN: Release me, otherwise no return!")
    #handmotor_sub.wait_til_condition([Side], [0])
    return

def wait_user_feedback():
    print("Press any key to start the protocol! (or press ESC to quit!)")
    if getch() == chr(0x1b):
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
    wait_user_feedback()

    # Setup motor-sensor
    all_motor_ids = list(Motor_ids.values())
    handsense_topic = SensorStatus(file_name, debug=False, serial_port="/dev/ttyACM1")
    handmotor_sub = MotorClamp(all_motor_ids, debug=False, serial_port="/dev/ttyUSB1")
    handsense_topic.attach(handmotor_sub)

    # Handshake Protocol
    sensor = threading.Thread(name="Sensor_Reading", target=handsense_topic.start_sensor_reading)
    sensor.start()
    while 1:
        setup_rigid(handmotor_sub)
        arm_startup_position(handmotor_sub)
        handshake_protocol(handmotor_sub)
        arm_closedown_position(handmotor_sub)
        print("****************************************\n"
              "DO YOU WANT MORE? \n")
        wait_user_feedback()

    handsense_topic.clean_sensor_reading()
    sensor.join()
    handaction_sub.cleanup_motor_list(all_motor_ids)

if __name__ == '__main__':
    main()
