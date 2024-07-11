# -*- coding: utf-8 -*-
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List

import json
import time
import serial

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
from dynamixel_sdk import * # Uses Dynamixel SDK library

from .motor_params import *
# Sensor index
Thumb = 2
Palm  = 0
Side  = 1

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
    def __init__(self, file_name, debug=False, serialPort=None):
        self._state: List[int] = [0,0,0]    # int state of each of the sensors [0] neutral - [1] touched -  [2] intense pressure
        self._observers: List[Observer] = []
        self.fname = file_name
        self._reading_flag = True
        self.debug = debug
        self.serial_port = serial.Serial(serialPort)
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
                line = self.serial_port.readline()
                sensor_dict = eval(line.decode().strip())
                readings = [100 * round(sensor_dict["thumb"],2), 100 * round(sensor_dict["palm"],2), 100 * round(sensor_dict["side"],2)]
                out_dump = json.dumps(sensor_dict, sort_keys=True, indent=4, separators=(',', ': '))
                file.write(out_dump)
                file.write(',')
                # States to notify
                for i, sensor in enumerate(readings): # Conditional notify
                    if sensor >= 20 and sensor < 50:
                        self._state[i] = 1
                    elif sensor >= 50:
                        self._state[i] = 2
                    else:
                        self._state[i] = 0
                self.notify()
                # print(out_dump)
                time.sleep(0.1)

class MotorClamp(Observer):
    def __init__(self, motor_ids, debug=False):
        #self.motor_handle = None
        self.portHandler, self.packetHandler =  self.setup_motor_comm()
        [self.setup_motor_init_mode(id) for id in motor_ids]
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

    def setup_motor_comm(self):
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
        return portHandler, packetHandler

    def setup_motor_init_mode(self, dxl_id):
        # Enable Dynamixel Torque
        dxl_comm_result, dxl_error = self.packetHandler.write1ByteTxRx(self.portHandler, dxl_id, ADDR_TORQUE_ENABLE, TORQUE_ENABLE)
        if dxl_comm_result != COMM_SUCCESS:
            print("%s" % self.packetHandler.getTxRxResult(dxl_comm_result))
            print("SUCCESS")
        elif dxl_error != 0:
            print("%s" % self.packetHandler.getRxPacketError(dxl_error))
        else:
            print("Dynamixel has been successfully connected")
        # Acceleration and velocity user friendly profile
        dxl_comm_result, dxl_error = self.packetHandler.write4ByteTxRx(self.portHandler, dxl_id, ADDR_PROFILE_ACCELERATION, 3)
        if dxl_comm_result != COMM_SUCCESS:
            print("%s" % self.packetHandler.getTxRxResult(dxl_comm_result))
        elif dxl_error != 0:
            print("%s" % self.packetHandler.getRxPacketError(dxl_error))
        dxl_comm_result, dxl_error = self.packetHandler.write4ByteTxRx(self.portHandler, dxl_id, ADDR_PROFILE_VELOCITY, 40)
        if dxl_comm_result != COMM_SUCCESS:
            print("%s" % self.packetHandler.getTxRxResult(dxl_comm_result))
        elif dxl_error != 0:
            print("%s" % self.packetHandler.getRxPacketError(dxl_error))
        # Compliance
        #dxl_comm_result, dxl_error = self.packetHandler.write4ByteTxRx(self.portHandler, dxl_id, ADDR_GOAL_CURRENT,
        #                                                               3000) # 200 , 60
        #if dxl_comm_result != COMM_SUCCESS:
        #    print("%s" % self.packetHandler.getTxRxResult(dxl_comm_result))
        #elif dxl_error != 0:
        #    print("%s" % self.packetHandler.getRxPacketError(dxl_error))
        # NOT COMPLIANT!! IT OVERLAP PREV
        dxl_comm_result, dxl_error = self.packetHandler.write4ByteTxRx(self.portHandler, dxl_id, ADDR_OPERATING_MODE,
                                                                       3) # 5 Compliant
        if dxl_comm_result != COMM_SUCCESS:
            print("%s" % self.packetHandler.getTxRxResult(dxl_comm_result))
        elif dxl_error != 0:
            print("%s" % self.packetHandler.getRxPacketError(dxl_error))
        return

    def cleanup_motor_list(self, dxl_id_list):
        [self.cleanup_motors(dxl_id) for dxl_id in dxl_id_list]

    def cleanup_motor(self, dxl_id):
        # Disable Dynamixel Torque
        dxl_comm_result, dxl_error = self.packetHandler.write1ByteTxRx(self.portHandler, dxl_id, ADDR_TORQUE_ENABLE, TORQUE_DISABLE)
        if dxl_comm_result != COMM_SUCCESS:
            print("%s" % self.packetHandler.getTxRxResult(dxl_comm_result))
        elif dxl_error != 0:
            print("%s" % self.packetHandler.getRxPacketError(dxl_error))

        # Close port
        self.portHandler.closePort()

    def move_motor_to_goal(self, dxl_id, goal):
        # Write goal position
        dxl_comm_result, dxl_error = self.packetHandler.write4ByteTxRx(self.portHandler, dxl_id, ADDR_GOAL_POSITION, goal)
        if dxl_comm_result != COMM_SUCCESS:
            print("%s" % self.packetHandler.getTxRxResult(dxl_comm_result))
        elif dxl_error != 0:
            print("%s" % self.packetHandler.getRxPacketError(dxl_error))

        while 1:
            # Read present position
            dxl_present_position, dxl_comm_result, dxl_error = self.packetHandler.read4ByteTxRx(self.portHandler, dxl_id,
                                                                                           ADDR_PRESENT_POSITION)
            if dxl_comm_result != COMM_SUCCESS:
                print("%s" % self.packetHandler.getTxRxResult(dxl_comm_result))
            elif dxl_error != 0:
                print("%s" % self.packetHandler.getRxPacketError(dxl_error))

            print("[ID:%03d] GoalPos:%03d  PresPos:%03d" % (dxl_id, goal, dxl_present_position))

            if abs(goal - dxl_present_position) <= DXL_MOVING_STATUS_THRESHOLD:
                break
        return

    def move_motors_to_goals_list(self, id_list, goal_list):
        for dxl_id, goal in zip(id_list, goal_list):
            # Write goal position
            dxl_comm_result, dxl_error = self.packetHandler.write4ByteTxRx(self.portHandler, dxl_id, ADDR_GOAL_POSITION, goal)
            if dxl_comm_result != COMM_SUCCESS:
                print("%s" % self.packetHandler.getTxRxResult(dxl_comm_result))
            elif dxl_error != 0:
                print("%s" % self.packetHandler.getRxPacketError(dxl_error))

        while len(id_list)!= 0:
            rm_id = []
            rm_goal = []
            for i, (dxl_id, goal) in enumerate(zip(id_list, goal_list)):
                # Read present position
                dxl_present_position, dxl_comm_result, dxl_error = self.packetHandler.read4ByteTxRx(self.portHandler, dxl_id,
                                                                                               ADDR_PRESENT_POSITION)
                if dxl_comm_result != COMM_SUCCESS:
                    print("%s" % self.packetHandler.getTxRxResult(dxl_comm_result))
                elif dxl_error != 0:
                    print("%s" % self.packetHandler.getRxPacketError(dxl_error))

                print("[ID:%03d] GoalPos:%03d  PresPos:%03d" % (dxl_id, goal, dxl_present_position))

                if abs(goal - dxl_present_position) <= DXL_MOVING_STATUS_THRESHOLD:
                    rm_id.append(dxl_id)
                    rm_goal.append(goal)

            for i,g in zip(rm_id, rm_goal):
                id_list.remove(i)
                goal_list.remove(g)

        return

    def move_motor_til_signal(self, dxl_id, goal, index_sensor):
        ''' The goal is stopped if the internal state_sensor at refered index is changed '''
        # Write goal position
        dxl_comm_result, dxl_error = self.packetHandler.write4ByteTxRx(self.portHandler, dxl_id, ADDR_GOAL_POSITION, goal)
        if dxl_comm_result != COMM_SUCCESS:
            print("%s" % self.packetHandler.getTxRxResult(dxl_comm_result))
        elif dxl_error != 0:
            print("%s" % self.packetHandler.getRxPacketError(dxl_error))

        while self.state_sensors[index_sensor] == 0:
            # Read present position
            dxl_present_position, dxl_comm_result, dxl_error = self.packetHandler.read4ByteTxRx(self.portHandler, dxl_id,
                                                                                           ADDR_PRESENT_POSITION)
            if dxl_comm_result != COMM_SUCCESS:
                print("%s" % self.packetHandler.getTxRxResult(dxl_comm_result))
            elif dxl_error != 0:
                print("%s" % self.packetHandler.getRxPacketError(dxl_error))

            print("[ID:%03d] GoalPos:%03d  PresPos:%03d" % (dxl_id, goal, dxl_present_position))

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
        return

    def setup_motor_register_mode(self, dxl_id, address, value):
        dxl_comm_result, dxl_error = self.packetHandler.write4ByteTxRx(self.portHandler, dxl_id, address,
                                                                       value)
        if dxl_comm_result != COMM_SUCCESS:
            print("%s" % self.packetHandler.getTxRxResult(dxl_comm_result))
        elif dxl_error != 0:
            print("%s" % self.packetHandler.getRxPacketError(dxl_error))
        return

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
