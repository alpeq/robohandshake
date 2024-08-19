import sys
import json
import time
from helpers.classes import SensorStatus
import threading
import logging

def main_read_sensors(filename):
    file_name = filename # Get the file name from command line arguments

    # Test
    # Setup motor-sensor
    handsense_topic = SensorStatus(file_name, debug=False, serial_port="/dev/ttyACM0")
    # handmotor_sub = MotorClamp(all_motor_ids, debug=False, serial_port="/dev/ttyUSB0")
    # handsense_topic.attach(handmotor_sub)

    sensor = threading.Thread(name="Sensor_Reading", target=handsense_topic.start_sensor_reading,
                              kwargs={'debug': False})
    sensor.start()
    # while True:
    #    print("MOTOR READING STATES: {}".format(handmotor_sub.state_sensors))
    # wait_user_feedback()
    time.sleep(20)
    handsense_topic.clean_sensor_reading()
    sensor.join()


if __name__ == "__main__":
    # Check if filename is provided as an argument
    if len(sys.argv) != 2:
        print("Usage: python script_name.py <file_name>")
        sys.exit(1)

    file_name = sys.argv[1]  # Get the file name from command line arguments
    main_read_sensors(file_name)
