from action_object import Action
import time

# Coordinates the actions of a bunch of peripherals to start/stop at the same
# time in response to a trigger (button press or other). Currently only runs
# for a specific amount of time (duration), but could run until a specific trigger
# instead (to be implemented)
class ActionGroup:
    def __init__(self, duration, *actions):
        # Validate arguments
        for a in actions:
            #print(a, type(a))
            if not isinstance(a, Action):
                print("cannot convert ", a, " to type action")
                raise TypeError()

        if duration <= 0:
            print("Duration must be a number greater than zero")
            raise ValueError()

        # Assign member variables
        self.action_list        = list(actions)
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
