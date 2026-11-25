from trigger_object import TriggerObject

from digitalio import DigitalInOut, Direction, Pull
from adafruit_debouncer import Debouncer

# Base class for triggers that are connected to one digital pin, such as a
# push button, a toggle switch, or a sensor whose output is on (high) or off (low).
#
# The pin uses the Pico's internal pull-up resistor, so it reads high until the
# button/switch/sensor connects it to GND. Readings are "debounced": a button's
# contacts bounce for a moment when pressed, and the debouncer makes sure one
# press counts only once.
#
# By default the trigger activates when the pin goes low (e.g. a button is pressed).
# A child class can override is_triggered() to activate on something else.
class DigitalPinTrigger(TriggerObject):

    def __init__(self, name, pin, action_groups, random_actions=False, allow_restart=True):
        pin_input           = DigitalInOut(pin)
        pin_input.direction = Direction.INPUT
        pin_input.pull      = Pull.UP
        self.switch         = Debouncer(pin_input)
        super().__init__(name, action_groups, random_actions=random_actions, allow_restart=allow_restart)

    # Read the pin. Called every time through the main loop
    def update(self):
        self.switch.update()

    # True if the pin just went low (connected to GND)
    def is_triggered(self):
        return self.switch.fell
