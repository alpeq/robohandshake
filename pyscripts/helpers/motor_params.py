
import sys, tty, termios

fd = sys.stdin.fileno()
old_settings = termios.tcgetattr(fd)
#********* DYNAMIXEL Model definition *********
MY_DXL = 'X_SERIES'       # X430

# Control table address
if MY_DXL == 'X_SERIES':
    ADDR_TORQUE_ENABLE          = 64
    ADDR_GOAL_POSITION          = 116
    ADDR_GOAL_CURRENT           = 102
    ADDR_PRESENT_POSITION       = 132
    ADDR_PROFILE_ACCELERATION	= 108
    ADDR_PROFILE_VELOCITY		= 112
    ADDR_OPERATING_MODE		    = 11

    DXL_MINIMUM_POSITION_VALUE  = 0         # Refer to the Minimum Position Limit of product eManual
    DXL_MAXIMUM_POSITION_VALUE  = 4090      # Refer to the Maximum Position Limit of product eManual
    BAUDRATE                    = 1000000

PROTOCOL_VERSION            = 2.0

TORQUE_ENABLE               = 1     # Value for enabling the torque
TORQUE_DISABLE              = 0     # Value for disabling the torque
DXL_MOVING_STATUS_THRESHOLD = 60    # 40 normal tolerance with specific -Dynamixel moving status threshold

ACCELERATION = 8   # 6
VELOCITY     = 60  # 60

Points_oscilation = 10 # 8
Tau_oscilation    = 4 # 4