from trigger_object import TriggerObject

import time
import adafruit_hcsr04
from adafruit_debouncer import Debouncer


class PingTrigger(TriggerObject):

    def __init__(self, name, trigger_pin, echo_pin, cutoff_distance, *button_actions):
        self.name               = name
        self.sonar              = adafruit_hcsr04.HCSR04(trigger_pin=trigger_pin,echo_pin=echo_pin)
        self.last_read_time     = 0
        self.cutoff_distance    = cutoff_distance
        self.current_distance   = 100
        self.switch             = Debouncer(lambda: self.current_distance < self.cutoff_distance, interval=0.3)
        super().__init__(name, list(button_actions))
        print("initializing ping sensor", name)

    def update(self):
        self.checkDistance()

    def is_triggered (self):
        #print("triggered")
        return self.switch.rose

    def checkDistance(self):
        now = time.monotonic()
        if now - self.last_read_time > 0.1:  # Limit how frequently distance is checked
            try:
                self.current_distance = self.sonar.distance
                #print(self.current_distance)
                self.switch.update()
                self.last_read_time = now
            except:
                print(self.name, "update failed")
