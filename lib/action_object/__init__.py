import time


# Some names were changed in version 2 of this library. Code that still uses
# an old name keeps working, but prints this note (once per name) so you know
# what to change it to.
_old_names_reported = []

def report_old_name(old_name, new_name):
    if old_name not in _old_names_reported:
        _old_names_reported.append(old_name)
        print("NOTE:", old_name, "is an old name. Please use", new_name, "instead.")


# A base class for peripherals (motor/animation/sound, etc...) that activate when
# a trigger (button, sensor...) is activated. Expandable to a wide variety of peripherals.
#
# To make a new kind of action, create a child class and override:
#   on_start()  - called once when the action starts           (optional)
#   on_update() - called over and over while the action runs    (required)
#   on_stop()   - called once when the action stops             (optional)
class Action:
    def __init__(self, name=""):
        self.name               = name
        self.action_start_time  = -1
        self.last_action_time   = -1

    # Child class may override this method with a function that is called
    # when the action is started
    def on_start(self):
        pass

    # Child class must override this method with a function that is called
    # repeatedly while the action is running.
    # Returns True if the action did something, False if not
    def on_update(self):
        # This line only runs if the child class didn't define on_update().
        # Child classes written before version 2 used the name action() instead.
        report_old_name("action()", "on_update()")
        return self.action()

    # Child class may override this method with a function that is called
    # when the action is stopped
    def on_stop(self):
        pass

    # Call this method to start the action
    def start(self):
        print("  starting action", self.name)
        self.on_start()
        self.action_start_time = time.monotonic()

    # Call this method to stop the action
    def stop(self):
        if self.is_active():
            print("  stopping action", self.name)
            self.on_stop()
            self.action_start_time = -1
            self.last_action_time  = -1

    # Call this method repeatedly in the code's main loop to keep the action running
    def update(self):
        if self.on_update():
            self.last_action_time = time.monotonic()

    # The value of action_start_time is -1 if the action is not currently active
    def is_active(self):
        return self.action_start_time >= 0

    # Returns the total time (in seconds) since this action was started
    def active_duration(self):
        return (time.monotonic() - self.action_start_time if self.is_active() else -1)

    # Returns the time (in seconds) since the last update that did something
    def time_since_last_action(self):
        return time.monotonic() - self.last_action_time

    # --- Old names (version 1). They still work, but please use the new names.
    def action(self):
        raise NotImplementedError("Child class of Action must define on_update()")

    def start_action(self):
        report_old_name("start_action()", "start()")
        self.start()

    def stop_action(self):
        report_old_name("stop_action()", "stop()")
        self.stop()

    def do_action(self):
        report_old_name("do_action()", "update()")
        self.update()
