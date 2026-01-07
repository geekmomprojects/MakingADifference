from action_object import Action
from action_object.action_group import ActionGroup
import time

# ConditionalActionGroup takes a condition function and a list of action groups
# The condition function must return a number which is the index of the list
# of action groups to play under the current conditions
class ActionGroupConditional(ActionGroup):
    def __init__(self, condition_fcn, action_groups):
        # Validate arguments
        self.action_groups      = action_groups
        self.condition_fcn      = condition_fcn
        self.action_index       = 0
        self.current_action     = action_groups[self.action_index]

    # The value of action_start_time is -1 if group is not currently active
    def is_active(self):
        return self.current_action.is_active()

    # Start all the actions in the list
    def start(self):
        self.action_index = self.condition_fcn()
        self.current_action = self.action_groups[self.action_index]
        self.current_action.start()

    # must be called repeatedly in main loop while group is active
    # will update the actions in the list
    def do_action(self):
        return self.current_action.do_action()


    # Stop all the actions in the list
    def stop(self):
        self.current_action.stop()

    def set_data(self, key, value):
        self.current_action.set_data(key, value)

    def get_data(self, key):
        return self.current_action.get_data(key)
