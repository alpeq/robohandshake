# -*- coding: utf-8 -*-
from __future__ import annotations
from abc import ABC, abstractmethod
from random import randrange
from typing import List

import sys
import json
import Adafruit_BBIO.ADC as ADC
import time

## Motor

import os

if os.name == 'nt':
    import msvcrt
    def getch():
        return msvcrt.getch().decode()
else:
    import sys, tty, termios
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    def getch():
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch
import sys, tty, termios
from dynamixel_sdk import * # Uses Dynamixel SDK library
from abc import ABC, abstractmethod

fd = sys.stdin.fileno()
old_settings = termios.tcgetattr(fd)
#********* DYNAMIXEL Model definition *********
MY_DXL = 'X_SERIES'       # X430

# Control table address
if MY_DXL == 'X_SERIES':
    ADDR_TORQUE_ENABLE          = 64
    ADDR_GOAL_POSITION          = 116
    ADDR_PRESENT_POSITION       = 132
    ADDR_PROFILE_ACCELERATION	= 108
    ADDR_PROFILE_VELOCITY		= 112
    DXL_MINIMUM_POSITION_VALUE  = 0         # Refer to the Minimum Position Limit of product eManual
    DXL_MAXIMUM_POSITION_VALUE  = 4090      # Refer to the Maximum Position Limit of product eManual
    BAUDRATE                    = 1000000

PROTOCOL_VERSION            = 2.0
DXL_ID                      = 1
DEVICENAME                  = '/dev/ttyUSB0'

TORQUE_ENABLE               = 1     # Value for enabling the torque
TORQUE_DISABLE              = 0     # Value for disabling the torque
DXL_MOVING_STATUS_THRESHOLD = 20    # Dynamixel moving status threshold


## Sensor
ADC.setup()

Thumb = 0
Palm = 1
Side = 2

def read_pins():
    ''' Function to read pins from the board '''
    value0 = 100*round(ADC.read("P9_39"),2) # AIN0
    #value = 100*round(ADC.read_raw("P9_39") # AIN0
    value1 = 100*round(ADC.read("P9_40"),2) # AIN1
    #value = 100*round(ADC.read_raw("P9_40") # AIN1
    value2 = 100*round(ADC.read("P9_37"),2) # AIN2
    # "thumb"       "palm"      "side-hand"
    return [value0, value1, value2], {"ain0":value0, "ain1":value1, "ain2":value2}

class Subject(ABC):
    """
    The Subject interface declares a set of methods for managing subscribers.
    """
    @abstractmethod
    def attach(self, observer: Observer) -> None:
        """
        Attach an observer to the subject.
        """
        pass

    @abstractmethod
    def detach(self, observer: Observer) -> None:
        """
        Detach an observer from the subject.
        """
        pass

    @abstractmethod
    def notify(self) -> None:
        """
        Notify all observers about an event.
        """
        pass
class Observer(ABC):
    """
    The Observer interface declares the update method, used by subjects.
    """

    @abstractmethod
    def update(self, subject: Subject) -> None:
        """
        Receive update from subject.
        """
        pass


class SensorStatus(Subject):
    """
    SensorStatus is a Subject node that notifies the status of each of the sensors for motor control and logging
    """
    def __init__(self, file_name, debug=False, ):
        self._state: List[int] = [0,0,0]    # int state of each of the sensors [0] neutral - [1] touched -  [2] intense pressure
        self._observers: List[Observer] = []
        self.fname = file_name
        self._reading_flag = True
        self.debug = debug
    def clean_sensor_reading(self):
        self._reading_flag = False
    def activate_sensor_reading(self):
        self._reading_flag = True

    def attach(self, observer: Observer) -> None:
        print("Subject: Attached an observer.")
        self._observers.append(observer)
    def detach(self, observer: Observer) -> None:
        self._observers.remove(observer)
    """
    The subscription management methods.
    """
    def notify(self) -> None:
        """
        Trigger an update in each subscriber.
        """
        for observer in self._observers:
            observer.update(self)

    def start_sensor_reading(self) -> None:
        """
        Loop to read sensors
        """
        with open(self.fname, 'a') as file:
            while True and self._reading_flag:
                readings, dict_out = read_pins()
                out_dump = json.dumps(dict_out, sort_keys=True, indent=4, separators=(',', ': '))
                file.write(out_dump)
                file.write(',')
                # States to notify
                for i,sensor in enumerate(readings): # Conditional notify
                    if sensor >= 25 and sensor < 50:
                        self._state[i] = 1
                    elif sensor >= 50:
                        self._state[i] = 2
                    else:
                        self._state[i] = 0
                self.notify()
                # print(out_dump)
                time.sleep(0.1)


class MotorClamp(Observer):
    def __init__(self, goal_open, goal_closed, debug=False):
        #self.motor_handle = None
        self.portHandler, self.packetHandler =  self.setup_motor()
        self.open = goal_open
        self.close = goal_closed
        self.state_sensors = [0, 0, 0]
        self.flag_change = False
        self.debug = debug
    def update(self, subject: Subject) -> None:
        self.state_sensors = subject._state
        if self.debug:
            print("Change notified: {}".format(self.state_sensors))
        #print("Thumb state has changed to: {}".format(str(subject._state[Thumb])))
        #print("Palm state has changed to: {}".format(str(subject._state[Palm])))
        #print("Side state has changed to: {}".format(str(subject._state[Side])))
        #print("Send motor command according to this info ****  \n")

    def setup_motor(self):
        # Initialize PortHandler and PacketHandler instance
        portHandler = PortHandler(DEVICENAME)
        packetHandler = PacketHandler(PROTOCOL_VERSION)

        # Open port
        if portHandler.openPort():
            print("Succeeded to open the port")
        else:
            print("Failed to open the port")
            print("Press any key to terminate...")
            getch()
            quit()

        # Set port baudrate
        if portHandler.setBaudRate(BAUDRATE):
            print("Succeeded to change the baudrate")
        else:
            print("Failed to change the baudrate")
            print("Press any key to terminate...")
            getch()
            quit()

        # Enable Dynamixel Torque
        dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, DXL_ID, ADDR_TORQUE_ENABLE, TORQUE_ENABLE)
        if dxl_comm_result != COMM_SUCCESS:
            print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
            print("SUCCESS")
        elif dxl_error != 0:
            print("%s" % packetHandler.getRxPacketError(dxl_error))
        else:
            print("Dynamixel has been successfully connected")
        # Acceleration and velocity user friendly profile
        dxl_comm_result, dxl_error = packetHandler.write4ByteTxRx(portHandler, DXL_ID, ADDR_PROFILE_ACCELERATION, 3)
        if dxl_comm_result != COMM_SUCCESS:
            print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
        elif dxl_error != 0:
            print("%s" % packetHandler.getRxPacketError(dxl_error))
        dxl_comm_result, dxl_error = packetHandler.write4ByteTxRx(portHandler, DXL_ID, ADDR_PROFILE_VELOCITY, 40)
        if dxl_comm_result != COMM_SUCCESS:
            print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
        elif dxl_error != 0:
            print("%s" % packetHandler.getRxPacketError(dxl_error))

        return portHandler, packetHandler

    def cleanup_motor(self):
        # Disable Dynamixel Torque
        dxl_comm_result, dxl_error = self.packetHandler.write1ByteTxRx(self.portHandler, DXL_ID, ADDR_TORQUE_ENABLE, TORQUE_DISABLE)
        if dxl_comm_result != COMM_SUCCESS:
            print("%s" % self.packetHandler.getTxRxResult(dxl_comm_result))
        elif dxl_error != 0:
            print("%s" % self.packetHandler.getRxPacketError(dxl_error))

        # Close port
        self.portHandler.closePort()

    def move_motor_to_goal(self, goal):
        # Write goal position
        dxl_comm_result, dxl_error = self.packetHandler.write4ByteTxRx(self.portHandler, DXL_ID, ADDR_GOAL_POSITION, goal)
        if dxl_comm_result != COMM_SUCCESS:
            print("%s" % self.packetHandler.getTxRxResult(dxl_comm_result))
        elif dxl_error != 0:
            print("%s" % self.packetHandler.getRxPacketError(dxl_error))

        while 1:
            # Read present position
            dxl_present_position, dxl_comm_result, dxl_error = self.packetHandler.read4ByteTxRx(self.portHandler, DXL_ID,
                                                                                           ADDR_PRESENT_POSITION)
            if dxl_comm_result != COMM_SUCCESS:
                print("%s" % self.packetHandler.getTxRxResult(dxl_comm_result))
            elif dxl_error != 0:
                print("%s" % self.packetHandler.getRxPacketError(dxl_error))

            print("[ID:%03d] GoalPos:%03d  PresPos:%03d" % (DXL_ID, goal, dxl_present_position))

            if abs(goal - dxl_present_position) <= DXL_MOVING_STATUS_THRESHOLD:
                break
        return

    def move_motor_til_signal(self, goal, index_sensor):
        ''' The goal is stopped if the internal state_sensor at refered index is changed '''
        # Write goal position
        dxl_comm_result, dxl_error = self.packetHandler.write4ByteTxRx(self.portHandler, DXL_ID, ADDR_GOAL_POSITION, goal)
        if dxl_comm_result != COMM_SUCCESS:
            print("%s" % self.packetHandler.getTxRxResult(dxl_comm_result))
        elif dxl_error != 0:
            print("%s" % self.packetHandler.getRxPacketError(dxl_error))

        while self.state_sensors[index_sensor] == 0:
            # Read present position
            dxl_present_position, dxl_comm_result, dxl_error = self.packetHandler.read4ByteTxRx(self.portHandler, DXL_ID,
                                                                                           ADDR_PRESENT_POSITION)
            if dxl_comm_result != COMM_SUCCESS:
                print("%s" % self.packetHandler.getTxRxResult(dxl_comm_result))
            elif dxl_error != 0:
                print("%s" % self.packetHandler.getRxPacketError(dxl_error))

            print("[ID:%03d] GoalPos:%03d  PresPos:%03d" % (DXL_ID, goal, dxl_present_position))

            if abs(goal - dxl_present_position) <= DXL_MOVING_STATUS_THRESHOLD:
                break
        return

    def wait_til_condition(self, index_sensor, state_list):
        '''
        @param index_sensor : List of sensor indexes to check
        @param state_list: List of states to fill the condition
        '''
        break_flag = False
        while 1:
            for ind in index_sensor:
                if self.state_sensors[ind] in state_list:
                    break_flag = True
            if break_flag:
                break
            time.sleep(0.1)

if __name__ == "__main__":
    # The client code.

    handsense_topic = SensorStatus()

    handaction_sub = MotorClamp()
    handsense_topic.attach(handaction_sub)

    # handaction --> Open clamp and wait for sensor input
    handsense_topic.read_sensor_logic()
    # handaction --> close clamp and shake until intense pressure
    handsense_topic.read_sensor_logic()
    # handaction --> open clamp and feedback audio?
