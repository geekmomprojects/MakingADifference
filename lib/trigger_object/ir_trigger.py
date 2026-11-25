from trigger_object.digital_pin_trigger import DigitalPinTrigger

# Trigger object is an IR sensor whose output pin is connected to a Pico pin.
# Triggers when the sensor's output goes low (when it detects something).
#
# Create it with:  IrTrigger(name, pin, action_groups)
# All the work is done by DigitalPinTrigger (see digital_pin_trigger.py)
class IrTrigger(DigitalPinTrigger):
    pass
