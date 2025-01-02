from trigger_object import TriggerObject

from digitalio import DigitalInOut, Direction, Pull
from adafruit_debouncer import Debouncer

# Trigger object is a toggle switch (triggers on flip)
class ToggleTrigger(TriggerObject):

    def __init__(self, name, pin, button_actions, allow_restart=False, toggle_both=True):
        # Create a debounced button object
        pinobj = DigitalInOut(pin)
        pinobj.direction    = Direction.INPUT
        pinobj.pull         = Pull.UP
        self.switch         = Debouncer(pinobj)
        self.toggle_both    = toggle_both
        #print(name, pin, button_actions)
        # Call base class constructor
        super().__init__(name, button_actions, allow_restart)

    def update(self):
        self.switch.update()

    def is_triggered(self):
        if self.toggle_both:
            return (self.switch.fell or self.switch.rose)
        else:
            return self.switch.rose
