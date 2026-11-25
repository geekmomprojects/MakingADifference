from trigger_object.digital_pin_trigger import DigitalPinTrigger

# Trigger object is a toggle switch connected between a pin and GND.
# Triggers when the switch is flipped:
#   toggle_both=True  - flipping it either way triggers it
#   toggle_both=False - only flipping it so it disconnects from GND (pin goes high) triggers it
class ToggleTrigger(DigitalPinTrigger):

    def __init__(self, name, pin, action_groups, random_actions=False, allow_restart=False, toggle_both=True):
        self.toggle_both = toggle_both
        super().__init__(name, pin, action_groups, random_actions=random_actions, allow_restart=allow_restart)

    def is_triggered(self):
        if self.toggle_both:
            return (self.switch.fell or self.switch.rose)
        else:
            return self.switch.rose
