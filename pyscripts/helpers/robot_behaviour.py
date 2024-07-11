import math
from .classes import *

# Motor related values
Motor_ids = {'shoulder_tilt':11, 'shoulder_roll':12, 'shoulder_pan':16,
                 'elbow_tilt':14, 'elbow_pan':15, 'wrist_tilt':2, 'wrist_roll':17,
                 'gripper':13 }
Grip_closed = 1500
Grip_open = 900
Wristroll_open = 2250
Wristroll_closed = 2750
#Wrist_up = 2620
#Wrist_down = 1630
Wristtilt_neutral = 2320
Elbow_relaxed = 2200
Elbow_mean = 2920 # 2000 exp decay shake
Elbow_max_amplitude = 300#800 500
Shoulder_up   = 2100 #1900
Shoulder_down = 1550 #1550

def arm_startup_position(handler):
    id_list   = [Motor_ids['shoulder_tilt'], Motor_ids['shoulder_roll'], Motor_ids['shoulder_pan'],
                 Motor_ids['elbow_tilt'], Motor_ids['elbow_pan'],
                 Motor_ids['wrist_tilt'], Motor_ids['wrist_roll'] ]
    goal_list = [Shoulder_up, 2048, 1018,
                 Elbow_mean, 3085,
                 Wristtilt_neutral, Wristroll_open]
    handler.move_motors_to_goals_list(id_list, goal_list)
    return

def arm_closedown_position(handler):
    handler.move_motor_to_goal(Motor_ids['elbow_tilt'], Elbow_relaxed)
    handler.move_motor_to_goal(Motor_ids['shoulder_tilt'], Shoulder_down)
    handler.move_motor_to_goal(Motor_ids['wrist_tilt'], Wristtilt_neutral)
    handler.move_motor_to_goal(Motor_ids['wrist_roll'], Wristroll_open)
    return

def closegrip_2dof_thumb(handler):
    handler.move_motors_til_signals_list([Motor_ids['wrist_roll'], Motor_ids['gripper']],
                                         [Wristroll_closed, Grip_closed], Thumb)
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
        sign_amp = 1 if n % 2 == 0 else -1
        amplitude = sign_amp * Elbow_max_amplitude * math.exp(-n/4)
        handler.move_motors_to_goals_list([elbow_motor, wrist_motor], [int(Elbow_mean+amplitude), int(Wristtilt_neutral+amplitude)])
        # With touch signals the cycle moves back
        if tactile and handler.check_for_condition([Side, Palm], [4]):
            if n_cycle == -1:
                n += 1
            elif n_cycle == 0:
                n -= 1
            else:
                n = max(n - 3, 0)
        else:
            n += 1
    return