from action_object import report_old_name
from action_object.action_group import ActionGroup
import random


# Base class for all triggers. Can be a button/toggle switch/sensor or any input
# that changes state.
#
# To make a new kind of trigger, create a child class and override:
#   is_triggered() - returns True when the trigger was just activated  (required)
#   update()       - reads the sensor; called every time through the main loop (optional)
class TriggerObject:

    def __init__(self, name, action_groups, allow_restart=True, random_actions=False):

        groups = []                 # list of action groups corresponding to trigger
        for a in action_groups:
            if type(a) is list:     # unpack any action groups in list format
                for item in a:
                    if isinstance(item, ActionGroup):
                        groups.append(item)
                    else:
                        raise TypeError("Actions passed to TriggerObject must be part of an ActionGroup")
            elif isinstance(a, ActionGroup):
                groups.append(a)
            else:
                raise TypeError("Actions passed to TriggerObject must be part of an ActionGroup")

        self.name                   = name
        self.action_groups          = groups
        self.allow_restart          = allow_restart     # What happens if the trigger is activated while its actions are playing:
                                                        #  True  - stop them and start the next action group
                                                        #  False - just stop them
        self.random_actions         = random_actions    # Determines whether the action groups play sequentially (False)
                                                        # or randomly (True)
        self.group_index            = 0                 # Index (in action_groups) of the group that plays next
        self.current_group          = self.action_groups[self.group_index] if len(self.action_groups) > 0 else None
        self.start_callback         = None
        self.stop_callback          = None


    # Must be overridden in child class
    def is_triggered(self):
        raise NotImplementedError()

    # Override this function with any updates that must be called repeatedly
    def update(self):
        pass

    # Move to the next item in the list of action groups
    def advance(self):
        if len(self.action_groups) > 1:
            if self.random_actions:
                self.set_random_group()
            else:
                self.group_index = (self.group_index + 1) % len(self.action_groups)
                self.current_group = self.action_groups[self.group_index]

    def set_random_group(self):
        self.group_index = random.randint(0, len(self.action_groups)-1)
        self.current_group = self.action_groups[self.group_index]

    def is_active(self):
        if self.current_group is not None:
            return self.current_group.is_active()
        else:
            return False

    def start(self):
        print("starting trigger ", self.name)
        # Invoke callback function if any exists
        if self.start_callback is not None:
            self.start_callback(self)
        if self.current_group is not None:
            self.current_group.start()
        print("")

    def stop(self, set_next_action=True):
        print("stopping trigger ", self.name)
        # Invoke callback function if any exists
        if self.stop_callback is not None:
            self.stop_callback(self)
        if self.current_group is not None:
            self.current_group.stop()
        if set_next_action:
            self.advance()
        print("")

    def toggle(self):
        if self.is_active():
            self.stop()
        else:
            self.start()

    def respond_to_trigger(self):
        if self.is_active():
            self.stop()
            if self.allow_restart:
                self.start()
        else:
            self.start()

    # Call repeatedly in the main loop to keep the current action group playing.
    # Returns True while it is playing, False once it has finished
    def play(self):
        if self.current_group is None:
            return False
        else:
            return self.current_group.update()

    # Choose which action group plays next by its index in the action_groups list
    def set_current_group(self, index):
        if self.is_active():
            raise AssertionError("cannot change action group while active")
        if index < 0 or index >= len(self.action_groups):
            raise IndexError("index out of range in action group list")
        self.group_index   = index
        self.current_group = self.action_groups[self.group_index]

    def get_current_group_data(self, key):
        result = None
        if self.current_group is not None:
            result = self.current_group.get_data(key)
        return result

    def set_start_callback(self, callback_func):
        self.start_callback = callback_func

    def set_stop_callback(self, callback_func):
        self.stop_callback = callback_func

    # --- Old names (version 1). They still work, but please use the new names.
    @property
    def current_action(self):
        report_old_name("current_action", "current_group")
        return self.current_group

    @property
    def action_index(self):
        report_old_name("action_index", "group_index")
        return self.group_index

    def set_random_action(self):
        report_old_name("set_random_action()", "set_random_group()")
        self.set_random_group()

    def set_current_action(self, index):
        report_old_name("set_current_action()", "set_current_group()")
        self.set_current_group(index)

    def get_current_action_data(self, key):
        report_old_name("get_current_action_data()", "get_current_group_data()")
        return self.get_current_group_data(key)
