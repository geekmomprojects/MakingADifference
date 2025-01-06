from action_object.action_group import ActionGroup
import random


# Abstract base class for all triggers. Can be a button/toggle switch/sensor or any input
# that changes state
class TriggerObject:

    # Instance functions
    def __init__(self, name, action_groups, allow_restart=True, random_actions=False):


        trigger_actions = []        # list of actions corresponding to trigger
        for a in action_groups:
            if type(a) is list:     # unpack any actions groups in list format
                for item in a:
                    if isinstance(item, ActionGroup):
                        trigger_actions.append(item)
                    else:
                        raise TypeError("Actions passed to TriggerObject must be part of an ActionGroup")
            elif isinstance(a, ActionGroup):
                trigger_actions.append(a)
            else:
                raise TypeError("Actions passed to TriggerObject must be part of an ActionGroup")


        self.name                   = name
        self.action_groups          = trigger_actions
        self.allow_restart          = allow_restart     # Determines whether a press while trigger is active
                                                        # will restart the action (True) or stop it (False)
        self.random_actions         = random_actions    # Determines whether the action groups play sequentially (False)
                                                        # or randomly (True)
        self.action_index           = 0
        self.current_action         = self.action_groups[self.action_index] if len(self.action_groups) > 0 else None


    # Must be overridden in child class
    def is_triggered(self):
        raise NotImplementedError()
        return False

    # Override this function with any updates that must be called repeatedly
    def update(self):
        pass

    # Move to the next item in the list of action groups
    def advance(self):
        #print("in advance trigger", self.name)
        if len(self.action_groups) > 1:
            if self.random_actions:
                self.set_random_action()
            else:
                self.action_index = (self.action_index + 1) % len(self.action_groups)
                self.current_action = self.action_groups[self.action_index]

    def set_random_action(self):
        #print("in set random action", self.name)
        self.action_index = random.randint(0, len(self.action_groups)-1)
        self.current_action = self.action_groups[self.action_index]

    def is_active(self):
        if self.current_action is not None:
            result = self.current_action.is_active()
            return result
        else:
            return False

    def start(self):
        print("starting trigger ", self.name)
        if self.current_action is not None:
            self.current_action.start()
        print("")

    def stop(self, set_next_action=True):
        print("stopping trigger ", self.name)
        if self.current_action is not None:
            self.current_action.stop()
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
            #print(" Trigger ", self.name, " pressed while active and self.allow_restart is ", self.allow_restart)
            self.stop()
            if self.allow_restart:
                self.start()
        else:
            self.start()

    def play(self):
        if self.current_action is None:
            return False
        else:
            return self.current_action.do_action()

    def get_current_action_data(self, key):
        result = None
        if self.current_action is not None:
            result = self.current_action.get_data(key)
        return result

'''
class TargetedTriggerObject(TriggerObject):
    def __init__(self, name, actions, targets, allow_restart=True, random_actions=False):
        super().__init__(name, actions, allow_restart, random_actions)



    def get_target(self):
        if self.action_index < 0:
            return None
        else:
            return self.targets[self.action_index]

'''







