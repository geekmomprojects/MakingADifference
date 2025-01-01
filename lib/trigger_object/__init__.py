from action_object.action_group import ActionGroup


# Abstract base class for all triggers. Can be a button/toggle switch/sensor or any input
# that changes state
class TriggerObject:
    # Static member variable
    restricted_triggers = None      # If not none, these are the only trigger(s) that will
                                    # be processed

    def __init__(self, name, actions):
        trigger_actions = []        # list of actions corresponding to trigger
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

    # Move to the next item in the list of action groups
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









