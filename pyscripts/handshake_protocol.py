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
    handaction_sub = MotorClamp(Closed_goal, Open_goal)
    handsense_topic.attach(handaction_sub)

    ''' Handshake Protocol '''
    while 1:

        # handaction --> Open clamp and wait for sensor input
        handsense_topic.read_sensor_logic()
        time.sleep(1)
        # handaction --> close clamp and shake until intense pressure
        handsense_topic.read_sensor_logic()
        # handaction --> open clamp and feedback audio?
    
    handaction_sub.cleanup_motor()


if __name__ == '__main__':
    main()
