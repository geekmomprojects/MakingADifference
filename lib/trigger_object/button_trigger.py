from trigger_object import TriggerObject

from digitalio import DigitalInOut, Direction, Pull
from adafruit_debouncer import Debouncer

# Trigger object is a push button (triggers on press)
class ButtonTrigger(TriggerObject):

    def __init__(self, name, pin, action_groups, random_actions=False, allow_restart=True):
        # Create a debounced button object
        pinobj = DigitalInOut(pin)
        pinobj.direction = Direction.INPUT
        pinobj.pull = Pull.UP
        self.switch             = Debouncer(pinobj)
        # Call base class constructor
        super().__init__(name, action_groups, random_actions=random_actions, allow_restart=allow_restart)

    def update(self):
        self.switch.update()

    def is_triggered(self):
        return self.switch.fell
