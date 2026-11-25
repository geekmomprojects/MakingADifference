from trigger_object.digital_pin_trigger import DigitalPinTrigger

# Trigger object is a push button connected between a pin and GND.
# Triggers when the button is pressed.
#
# Create it with:  ButtonTrigger(name, pin, action_groups)
# All the work is done by DigitalPinTrigger (see digital_pin_trigger.py)
class ButtonTrigger(DigitalPinTrigger):
    pass
