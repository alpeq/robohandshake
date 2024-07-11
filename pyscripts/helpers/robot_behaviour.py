import math
from .classes import *

# Motor related values
Motor_ids = {'neck':3, 'shoulder_tilt':11, 'shoulder_roll':12, 'shoulder_pan':16,
                 'elbow_tilt':14, 'elbow_pan':15, 'wrist_tilt':2, 'wrist_roll':17,
                 'gripper':13 }
Grip_closed = 1500
Grip_open = 900
Wristroll_open = 2250
Wristroll_closed = 2750
#Wrist_up = 2620
#Wrist_down = 1630
Wristtilt_neutral = 2320
Elbow_relaxed = 2400
Elbow_mean = 2920 # 2000 exp decay shake
Elbow_max_amplitude = 300#800 500
Shoulder_up   = 2100 #1900
Shoulder_down = 1550 #1550
Neck_up   = 2100
Neck_down = 1700

def arm_startup_position(handler):
    id_list = [Motor_ids['neck'],
                 Motor_ids['shoulder_tilt'], Motor_ids['shoulder_roll'], Motor_ids['shoulder_pan'],
                 Motor_ids['elbow_tilt'], Motor_ids['elbow_pan'],
                 Motor_ids['wrist_tilt'], Motor_ids['wrist_roll'] ]
    goal_list = [Neck_up,
                 Shoulder_up, 2048, 1018,
                 Elbow_mean, 3085,
                 Wristtilt_neutral, Wristroll_open]
    handler.move_motors_to_goals_list(id_list, goal_list)
    return

def arm_retract_return(handler):
    id_list = [Motor_ids['shoulder_tilt'], Motor_ids['elbow_tilt']]
    goal_list = [Shoulder_down + 300, Elbow_mean + 300]
    handler.move_motors_to_goals_list(id_list, goal_list)
    return

def arm_closedown_position(handler):
    #handler.move_motor_to_goal(Motor_ids['neck'], Neck_down)
    id_list = [Motor_ids['elbow_tilt'], Motor_ids['shoulder_tilt'],
               Motor_ids['wrist_tilt'],Motor_ids['wrist_roll']]
    goal_list = [Elbow_relaxed, Shoulder_down, Wristtilt_neutral, Wristroll_open]
    handler.move_motors_to_goals_list(id_list, goal_list)
    return

def closegrip_2dof_thumb(handler, tactile=False):
    if tactile:
        handler.move_motors_til_signals_list([Motor_ids['wrist_roll'], Motor_ids['gripper']],
                                             [Wristroll_closed, Grip_closed], Thumb, debug=False)
    else:
        handler.move_motors_to_goals_list([Motor_ids['wrist_roll'], Motor_ids['gripper']],
                                             [Wristroll_closed-50, Grip_closed-50])
    return

def opengrip_2dof_thumb(handler):
    handler.move_motors_til_signals_list([Motor_ids['wrist_roll'], Motor_ids['gripper']],
                                         [Wristroll_open, Grip_open], Thumb)
    return

def setup_compliance(handler):
    handler.setup_motor_register_mode(Motor_ids['shoulder_tilt'], ADDR_OPERATING_MODE, 5)  # Complaint mode
    handler.setup_motor_register_mode(Motor_ids['shoulder_tilt'], ADDR_GOAL_CURRENT, 100)
    handler.setup_motor_register_mode(Motor_ids['wrist_tilt'], ADDR_OPERATING_MODE, 5)  # Complaint mode
    handler.setup_motor_register_mode(Motor_ids['wrist_tilt'], ADDR_GOAL_CURRENT, 50)

def setup_rigid(handler):
    handler.setup_motor_register_mode(Motor_ids['shoulder_tilt'], ADDR_OPERATING_MODE, 3)  # Complaint mode
    handler.setup_motor_register_mode(Motor_ids['wrist_tilt'], ADDR_OPERATING_MODE, 3)  # Complaint mode

def shaking_phase(handler, tactile=False, osci_points=Points_oscilation):
    ''' Shaking based on elbow tilt axes
        Oscilation Point to Point with exponentially decrease amplitude
    '''
    closegrip_2dof_thumb(handler, tactile=tactile)

    elbow_motor = Motor_ids['elbow_tilt']
    wrist_motor = Motor_ids['wrist_tilt']
    n = 0
    total_n = 0
    points_cycle = 2
    while(n < osci_points):
        n_cycle = math.floor((n-1)/points_cycle)
        print(n)
        sign_amp = 1 if n % 2 == 0 else -1
        amplitude = sign_amp * Elbow_max_amplitude * math.exp(-n/Tau_oscilation)
        handler.move_motors_to_goals_list([elbow_motor, wrist_motor], [int(Elbow_mean+amplitude), int(Wristtilt_neutral+amplitude)])
        # With touch signals the cycle moves back
        if tactile:
            if handler.check_for_condition([Side], [4,5]) and total_n < Points_oscilation:
                if n_cycle == -1:
                    n += 1
                elif n_cycle == 0:
                    n -= 1
                else:
                    n = max(n - 3, 0)
            else:
                n += 5
        else:
            n += 1
        total_n += 1
    return