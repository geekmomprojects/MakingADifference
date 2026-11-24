from action_object.action_group import ActionGroup

# ConditionalActionGroup takes a condition function and a list of action groups
# The condition function must return a number which is the index of the list
# of action groups to play under the current conditions
class ActionGroupConditional(ActionGroup):
    def __init__(self, condition_fcn, action_groups):
        self.action_groups      = action_groups
        self.condition_fcn      = condition_fcn
        self.group_index        = 0
        self.current_group      = action_groups[self.group_index]

    def is_active(self):
        return self.current_group.is_active()

    # Ask the condition function which group to play, then start it
    def start(self):
        self.group_index = self.condition_fcn()
        self.current_group = self.action_groups[self.group_index]
        self.current_group.start()

    # must be called repeatedly in main loop while group is active
    # will update the actions in the current group
    def update(self):
        return self.current_group.update()

    def stop(self):
        self.current_group.stop()

    def set_data(self, key, value):
        self.current_group.set_data(key, value)

    def get_data(self, key):
        return self.current_group.get_data(key)
