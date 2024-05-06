from __future__ import annotations
from abc import ABC, abstractmethod
from random import randrange
from typing import List

import sys
import json
import Adafruit_BBIO.ADC as ADC
import time

ADC.setup()

Thumb = 0
Palm = 1
Side = 2

def read_pins():
    ''' Function to read pins from the board '''
    value0 = ADC.read("P9_39") # AIN0
    #value = ADC.read_raw("P9_39") # AIN0
    value1 = ADC.read("P9_40") # AIN1
    #value = ADC.read_raw("P9_40") # AIN1
    value2 = ADC.read("P9_37") # AIN2
    # "thumb"       "palm"      "side-hand"
    return [value0, value1, value2], {"ain0":100*round(value0,2), "ain1":100*round(value1,2), "ain2":100*round(value2,2)}

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

    def __init__(self, file_name):
        self._state: List[int] = [0,0,0]    # int state of each of the sensors [0] neutral - [1] touched -  [2] intense pressure
        self._observers: List[Observer] = []
        self.fname = file_name
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

    def read_sensor_logic(self) -> None:
        """
        Loop to read sensors
        """
        with open(self.fname, 'a') as file:
            while True:
                self._state, dict_out = read_pins()
                out_dump = json.dumps(dict_out, sort_keys=True, indent=4, separators=(',', ': '))
                file.write(out_dump)
                for sensor in self._state:
                    if sensor > 25:
                        break
                # print(out_dump)
                time.sleep(0.1)

        self.notify()

class MotorClamp(Observer):
    def __init__(self):
        self.motor_handle = None
    def update(self, subject: Subject) -> None:
        print("Thumb state has changed to: {}".format(str(subject._state[Thumb])))
        print("Palm state has changed to: {}".format(str(subject._state[Palm])))
        print("Side state has changed to: {}".format(str(subject._state[Side])))
        print("Send motor command according to this info ****  \n")


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
