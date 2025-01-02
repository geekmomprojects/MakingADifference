#import board
#import busio
import time
#import random
#import math


#from digitalio import DigitalInOut, Direction, Pull
#from adafruit_debouncer import Debouncer
#from dyplayer import DYPlayer
#import adafruit_hcsr04
#from adafruit_led_animation.animation import Animation

# A base class for peripherals (motor/animation/sound, etc...) that activate when
# a button is pushed. Ideally expandable to a wide variety of peripherals.
class Action:
    def __init__(self, name=""):
        self.name               = name
        self.action_start_time  = -1
        self.last_action_time   = -1

    # Child class may override this method with a function that is called
    # when the action is started
    def on_start(self):
        pass

    # Child class may override this method with a function that is called
    # when the action is stopped
    def on_stop(self):
        pass

    # Call this method to start action
    # Call base class method if overridden
    def start_action(self):
        print("  starting action", self.name)
        self.on_start()
        self.action_start_time = time.monotonic()

    # Call this method to stop the action
    # Call base class method in the child
    # member function if this method is overridden
    def stop_action(self):
        if self.is_active():
            print("  stopping action", self.name)
            self.on_stop()
            self.action_start_time = -1
            self.last_action_time  = -1

    # Child class must override this method.
    # Returns true if action occurred, false if not
    def action(self):
        raise NotImplementedError()
        return False
	
    # Call this method repeatedly in the code's main loop to perform the
    # Peripheral's action repeatedly in a loop
    def do_action(self):
        if self.action():
            self.last_action_time = time.monotonic()

    def is_active(self):
        return (self.action_start_time > 0)

    # Returns the total time (in seconds) since this action was started
    def active_duration(self):
        return (time.monotonic() - self.action_start_time if self.is_active() else -1)

    # Returns the time (in seconds) since the last action
    def time_since_last_action(self):
        return time.monotonic() - self.action_start_time








