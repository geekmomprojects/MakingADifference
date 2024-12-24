from trigger_object import TriggerObject

from digitalio import DigitalInOut, Direction, Pull
from adafruit_debouncer import Debouncer

# Trigger object is a toggle switch (triggers on flip)
class ToggleTrigger(TriggerObject):

    def __init__(self, name, pin, *button_actions):
        # Create a debounced button object
        pinobj = DigitalInOut(pin)
        pinobj.direction = Direction.INPUT
        pinobj.pull = Pull.UP
        self.switch             = Debouncer(pinobj)
        #print(name, pin, button_actions)
        # Call base class constructor
        super().__init__(name, list(button_actions))

    def update(self):
        self.switch.update()

    def is_triggered(self):
        return (self.switch.fell or self.switch.rose)
