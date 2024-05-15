from helpers.classes import *

Closed_goal = 1200
Open_goal = 1600


def main():
    ''' Handshake Protocol '''
    while 1:
        print("Press any key to start the protocol! (or press ESC to quit!)")
        if getch() == chr(0x1b):
            break
        # The client code.

        handsense_topic = SensorStatus()
        handaction_sub = MotorClamp(Closed_goal, Open_goal)
        handsense_topic.attach(handaction_sub)

        # handaction --> Open clamp and wait for sensor input
        handsense_topic.read_sensor_logic()
        # handaction --> close clamp and shake until intense pressure
        handsense_topic.read_sensor_logic()
        # handaction --> open clamp and feedback audio?
    
    handaction_sub.cleanup_motor()


if __name__ == '__main__':
    main()
