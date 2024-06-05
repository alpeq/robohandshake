from helpers.classes import *
import time

Closed_goal = 1270
Open_goal = 1600


def main():
    # Check if filename is provided as an argument
    if len(sys.argv) != 2:
        print("Usage: python script_name.py <file_name>")
        sys.exit(1)

    file_name = sys.argv[1]  # Get the file name from command line arguments

    print("Press any key to start the protocol! (or press ESC to quit!)")
    if getch() == chr(0x1b):
        return

    # Setup motor-sensor
    handsense_topic = SensorStatus(file_name)
    handmotor_sub = MotorClamp(Closed_goal, Open_goal)
    handsense_topic.attach(handmotor_sub)

    ''' Handshake Protocol '''
    handsense_topic.start_sensor_reading()
    while 1:
        # Wait until somebody grab the hand ( side or palm activated )
        handmotor_sub.wait_til_condition([Side, Palm], [1,2])
        # Close the hand until touch in thumb
        handmotor_sub.move_motor_til_signal(Closed_goal-100,Thumb)
        # Wait until increase in the pressure or release
        handmotor_sub.wait_til_condition([Side], [0,2])
        # Open hand to init
        handmotor_sub.move_motor_to_goal(Open_goal)

    handsense_topic.clean_sensor_reading()
    handaction_sub.cleanup_motor()

if __name__ == '__main__':
    main()
