# Import statments
import board
import busio
import time
import pwmio


# Import Sound Player module. Only necessary if toy plays sounds
from dyplayer import DYPlayer

# Import all triggers used (can omit any that are not used)
from trigger_object import TriggerObject
from trigger_object.button_trigger import ButtonTrigger

from action_object.action_sound import ActionSound
from action_object.action_sound_sequence import ActionSoundSequence
from action_object.action_group import ActionGroup


print("Code is starting")

### --- Create the MP3 player object
# TX/RX pins to be connected to RX/TX on the MP3 player
# Pico UART2 TX (GP8) <-> MP3 Player RX
# Pico UART2 RX (GP9) <-> MP3 Player TX
player_uart = busio.UART(board.GP8, board.GP9, baudrate=9600)

# Create Player Object
player = DYPlayer(uart=player_uart)
#time.sleep(0.1)  #Leave time to initialize

### --- Create sound action objects to play different tracks
songAction1 = ActionSound(player, 1)
songAction2 = ActionSound(player, 2)
songAction3 = ActionSound(player, 3)
songAction4 = ActionSound(player, 4)

# ActionSoundSequences takes the dyplayer object as its first argument
# the second argument is a list of track numbers to play in the sequence specified
# the third argument is a list specifying the number of seconds to play each track for.
songSeq1  = ActionSoundSequence(player, [2,4,6],[5,7,6])


### --- Create a TriggerObject object for each trigger in the toy. Each trigger object takes a
#  list of one or more ActionGroupObjects. An ActionGroup contains a time duration (in seconds) and an arbitrary
#  number of ActionObjects (e.g. ActionSound, ActionAnimation, ActionServo) that will occur simultaneously
#  when triggered, and persist for the time duration specified.

PIN_A       = board.GP16                                                # Pi Pico pin associated with Button A
ACTIONS_A   = [ ActionGroup(songSeq1.get_duration(), songSeq1),         # get_duration() gives the length of a ActionSoundSequence object
                ActionGroup(5, songAction1),                            # List of action groups associaciated with Button A
                ActionGroup(3, songAction2)]

# Create button objects on Pins A and B. The "allow_restart" keyword determines what happens when the button is pushed
# twice sequentially. If "allow_restart" is True, the next action group will start from the beginning. Otherwise all actions will stop
ButtonA = ButtonTrigger("Button A", PIN_A, ACTIONS_A, allow_restart=True, random_actions=False)  # Button A chooses its action groups randomly

# Create a list of trigger objects
trigger_objects      = [
                         ButtonA
                       ]


# Main loop. No need to change code here to change the number of buttons. To add new buttons, simply create new button objects
current_trigger = None          # button corresponding to the current song or animation playing (None if no song/animation playing)

while True:
    # If a button is currently active, play its associated actions (song, animation, motor, etc...)
    if current_trigger is not None:
        if not current_trigger.play():   # Play the current trigger's actions, but check to see if they have ended
            current_trigger.stop()       # Need to actively stop the trigger to make sure it advances
            current_trigger = None

    # Update all triggers (updates debouncers)
    for trigger in trigger_objects:
        trigger.update()

    # check to see if the user activated any of the triggers.
    for trigger in trigger_objects:
        if trigger.is_triggered():                                           # Was the trigger activated?
            print("")
            print(trigger.name, "was triggered.")
            if current_trigger is not None and trigger != current_trigger:   # There is a currently a different active trigger
                print("")                                                    # so stop that one
                print("stopping trigger", current_trigger.name)
                print("")
                current_trigger.stop()
            trigger.respond_to_trigger()                                     # New trigger responds to activation
            if trigger.is_active():
                current_trigger = trigger
            else:
                current_trigger = None

