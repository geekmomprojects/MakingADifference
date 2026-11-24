from action_object import Action, report_old_name
import time

# Coordinates the actions of a bunch of peripherals to start/stop at the same
# time in response to a trigger (button press or other). Currently only runs
# for a specific amount of time (duration), but could run until a specific trigger
# instead (to be implemented)
class ActionGroup:
    INFINITE = -1

    def __init__(self, duration, *actions):  # If duration is ActionGroup.INFINITE, actions run until interrupted
        # Validate arguments
        for a in actions:
            if not isinstance(a, Action):
                raise TypeError("ActionGroup cannot use " + str(a) + " because it is not an Action")

        if duration != ActionGroup.INFINITE and duration <= 0:
            raise ValueError("ActionGroup duration must be a number greater than zero (or ActionGroup.INFINITE)")

        # Assign member variables
        self.action_list        = list(actions)
        self.duration           = duration  # Number of seconds the actions play for.
                                            # If duration is ActionGroup.INFINITE, the group plays until it is stopped
        self.action_start_time  = -1
        self.data               = {}        # Dictionary for storing associated data (e.g. target trigger object)

    # The value of action_start_time is -1 if group is not currently active
    def is_active(self):
        return self.action_start_time >= 0

    # Start all the actions in the list
    def start(self):
        for a in self.action_list:
            a.start()
        self.action_start_time = time.monotonic()

    # should only to call this if action_group is active
    def runtime_elapsed(self):
        if self.duration == ActionGroup.INFINITE or time.monotonic() - self.action_start_time < self.duration:
            return False
        else:
            return True

    # Must be called repeatedly in main loop while group is active.
    # Updates all the actions in the list.
    # Returns True while the group is still playing, False once it has finished
    def update(self):
        if self.is_active():
            if self.runtime_elapsed():
                self.stop()
                return False
            else:
                for a in self.action_list:
                    a.update()
                return True
        return False

    # Stop all the actions in the list
    def stop(self):
        if self.is_active():
            for a in self.action_list:
                a.stop()
            self.action_start_time = -1

    def set_data(self, key, value):
        self.data[key] = value

    def get_data(self, key):
        return self.data.get(key)    # Returns None if key was never set

    # --- Old names (version 1). They still work, but please use the new names.
    def do_action(self):
        report_old_name("do_action()", "update()")
        return self.update()
