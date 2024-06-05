from helpers.classes import *
import threading

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
    handsense_topic = SensorStatus(file_name, debug=False)
    handmotor_sub = MotorClamp(Closed_goal, Open_goal, debug=False)
    handsense_topic.attach(handmotor_sub)

    ''' Handshake Protocol '''
    sensor = threading.Thread(name="Sensor_Reading", target=handsense_topic.start_sensor_reading)
    sensor.start()
    handmotor_sub.move_motor_to_goal(Open_goal)

    while 1:
        print("Start: GIVE ME THAT HAND ")
        # Wait until somebody grab the hand ( side or palm activated )
        handmotor_sub.wait_til_condition([Side, Palm], [1,2])
        print("Activated Side/Palm: I grab you yours")
        # Close the hand until touch in thumb
        handmotor_sub.move_motor_til_signal(Closed_goal-200, Thumb)
        print("Close Position: Waitting for a good shake!")
        # Wait until increase in the pressure or release
        handmotor_sub.wait_til_condition([Side, Palm], [2])
        print("To Open Position: My pleasure!")
        # Open hand to init
        handmotor_sub.move_motor_to_goal(Open_goal)
        print("Release me!")
        handmotor_sub.wait_til_condition([Side], [0])


    handsense_topic.clean_sensor_reading()
    sensor.join()
    handaction_sub.cleanup_motor()

if __name__ == '__main__':
    main()
