import board
import busio
import time
import random
import math

from adafruit_motor import servo
from digitalio import DigitalInOut, Direction, Pull
from adafruit_debouncer import Debouncer
from dyplayer import DYPlayer
from adafruit_led_animation.animation import Animation

# A base class for peripherals (motor/animation/sound, etc...) that activate when
# a button is pushed. Ideally expandable to a wide variety of peripherals.
class Action:
    def __init__(self, name):
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
        print("starting", self.name)
        self.on_start()
        self.action_start_time = time.monotonic()

    # Call this method to stop the action
    # Call base class method in the child
    # member function if this method is overridden
    def stop_action(self):
        if self.is_active():
            print("stopping", self.name)
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

# An action class that controls a servo. Can specify the start/end angle and the period
# for one complete back and forth motion
class ActionServo(Action):
    def __init__(self, name, servo_obj, start_angle=20, end_angle=160, period=3):
        self.servo_obj = servo_obj
        self.start_angle = start_angle
        self.end_angle = end_angle
        self.period = period
        self.sevo_pos = start_angle
        super().__init__(name)

    def action(self):
        if not self.is_active() or self.time_since_last_action() < 0.05:  #Don't update TOO frequently
            return False

        # Create periodic motion of the servo over the angle range with a bit of trig
        period_frac = (math.sin(6.28*self.active_duration()/self.period) + 1)/2
        self.servo_pos = self.start_angle + (self.end_angle - self.start_angle)*period_frac
        self.servo_obj.angle = self.servo_pos
        return True

# An action class for an LED animation
class ActionAnimation(Action):
    def __init__(self, animation):
        self.animation = animation
        super().__init__(animation.__class__.__name__)

    def action(self):
        return self.animation.animate()

    # When animation is stopped, set pixels to black and reset animation
    def on_stop(self):
        self.animation.reset()
        self.animation.pixel_object.fill((0,0,0))
        self.animation.pixel_object.show()

# An action class to play a track. Takes a DYPlayer object and track number
class ActionSound(Action):
    def __init__(self, player, track_num, track_duration=-1):
        self.player         = player
        self.track_num      = track_num
        self.track_duration = track_duration    # Length of time (seconds) to play track
        super().__init__("Track " + str(track_num))

    def on_start(self):
        self.player.playByNumber(self.track_num)

    def on_stop(self):
        self.player.stop()

    # Stop the player if the duration is specified and the song has played
    # for longer than the specified duration
    def action(self):
        if self.track_duration >= 0 and self.active_duration() > track_duration:
            self.stop_action()
            return True
        else:
            return False

# Coordinates the actions of a bunch of peripherals to start/stop at the same
# time in response to a trigger (button press or other). Currently only runs
# for a specific amount of time (duration), but could run until a specific trigger
# instead (to be implemented)
class ActionGroup:
    def __init__(self, duration, *actions):
        # Validate arguments
        for a in actions:
            #print(a, type(a))
            if not (isinstance(a, Action) or isinstance(a, Animation)):
                print("Action items must be of type Action or Animation")
                raise TypeError()

        if duration <= 0:
            Print("Duration must be a number greater than zero")
            raise ValueError()

        # Assign member variables
        self.action_list        = [ActionAnimation(a) if isinstance(a, Animation) else a for a in actions]
        self.duration           = duration  # Must be number (seconds) for the action to take place. TBD - add different end condition
        self.action_start_time  = -1

        #print(self.action_list)

    # The value of action_start_time is -1 if group is not currently active
    def is_active(self):
        return self.action_start_time >= 0

    # Start all the actions in the list
    def start(self):
        for a in self.action_list:
            a.start_action()
        self.action_start_time = time.monotonic()

    # must be called repeatedly in main loop while group is active
    # will update the actions in the list
    def update(self):
        if self.is_active():
            if time.monotonic() - self.action_start_time < self.duration:
                for a in self.action_list:
                    a.do_action()
                return True
            else:
                self.stop()
                return False

    # Stop all the actions in the list
    def stop(self):
        if self.is_active():
            for a in self.action_list:
                a.stop_action()
            self.action_start_time = -1


# Abstract base class for all triggers. Can be a button/toggle switch/sensor or any input
# that changes state
class TriggerObject:
    def __init__(self, name, actions):
        trigger_actions = []
        for a in actions:
            if type(a) is list:     # unpack any actions in list format
                for item in a:
                    if isinstance(item, ActionGroup):
                        trigger_actions.append(item)
                    else:
                        raise TypeError("Actions passed to TriggerObject must be part of an ActionGroup")
            elif isinstance(a, ActionGroup):
                trigger_actions.append(a)
            else:
                raise TypeError("Actions passed to TriggerObject must be part of an ActionGroup")

        self.name               = name
        self.actions            = trigger_actions
        self.action_index       = 0
        self.current_action     = self.actions[self.action_index] if len(self.actions) > 0 else None

    def addActionGroup(self, duration, *actions):
        self.actions.append(ActionGroup(duration, actions))
        if self.current_action is None:
            self.action_index = 0
            self.current_action = self.actions[self.action_index]

    # Must be overridden in child class
    def is_triggered(self):
        raise NotImplementedError()
        return False

    # Override this function with any updates that must be called repeatedly
    def update(self):
        pass

    def advance(self):
        if len(self.actions) > 0:
            self.action_index = (self.action_index + 1) % len(self.actions)
            self.current_action = self.actions[self.action_index]

    def is_active(self):
        if self.current_action is not None:
            return self.current_action.is_active()
        else:
            return False

    def start(self):
        if self.current_action is not None:
            self.current_action.start()

    def stop(self):
        if self.current_action is not None:
            self.current_action.stop()
            self.advance()

    def play(self):
        if self.current_action is None:
            return False
        else:
            return self.current_action.update()

# Trigger object is a push button (triggers on press)
class ButtonTrigger(TriggerObject):

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
        return self.switch.fell

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




