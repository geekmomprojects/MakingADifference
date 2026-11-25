# This example shows the main loop written out step by step, instead of using
# toy.run(). It does the same thing as the Toy class in lib/toy.py.
#
# Most toys don't need this - they can just use:
#     toy = Toy(trigger_objects)
#     toy.run()
#
# Write the loop out yourself when you want to see how it works, or want to
# change how the toy responds.
#
# Hardware: two push buttons on GP16 and GP17. The Pico's built-in LED lights up.

import board

from action_object.action_led import ActionLED
from action_object.action_group import ActionGroup
from trigger_object.button_trigger import ButtonTrigger


### --- Create the actions
# The Pico's built-in LED, used by both buttons
led_action = ActionLED(board.LED)

### --- Create the triggers
# Button A lights the LED for 2 seconds, Button B lights it for 5 seconds
button_a = ButtonTrigger("Button A", board.GP16, [ActionGroup(2, led_action)])
button_b = ButtonTrigger("Button B", board.GP17, [ActionGroup(5, led_action)])

trigger_objects = [button_a, button_b]


### --- The main loop
current_trigger = None      # The trigger whose actions are playing (None if nothing is playing)

while True:
    # 1. Keep the current trigger's actions playing, and notice when they finish.
    #    play() returns False once the action group's time is up.
    if current_trigger is not None:
        if not current_trigger.play():
            current_trigger.stop()          # Stopping the trigger moves it on to its next action group
            current_trigger = None

    # 2. Read all the triggers (buttons, sensors...)
    for trigger in trigger_objects:
        trigger.update()

    # 3. Respond to the first trigger that was activated
    for trigger in trigger_objects:
        if trigger.is_triggered():
            print(trigger.name, "was triggered.")

            # If a different trigger was playing, stop it
            if current_trigger is not None and trigger is not current_trigger:
                current_trigger.stop()

            # Start this trigger's actions (or stop/restart them if they were already playing)
            trigger.respond_to_trigger()
            if trigger.is_active():
                current_trigger = trigger
            else:
                current_trigger = None
            break                           # Only respond to one trigger at a time

    # 4. Add your own code here - it runs every time through the loop
