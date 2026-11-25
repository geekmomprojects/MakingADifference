# Import statments
import board
import busio


# Import Sound Player module. Only necessary if toy plays sounds
from dyplayer import DYPlayer

# Import all triggers used (can omit any that are not used)
from trigger_object.button_trigger import ButtonTrigger

# Import the main loop for the toy
from toy import Toy

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
song_action_1 = ActionSound(player, 1)
song_action_2 = ActionSound(player, 2)
song_action_3 = ActionSound(player, 3)
song_action_4 = ActionSound(player, 4)

# ActionSoundSequences takes the dyplayer object as its first argument
# the second argument is a list of track numbers to play in the sequence specified
# the third argument is a list specifying the number of seconds to play each track for.
song_seq_1  = ActionSoundSequence(player, [2,4,6],[5,7,6])


### --- Create a TriggerObject object for each trigger in the toy. Each trigger object takes a
#  list of one or more ActionGroupObjects. An ActionGroup contains a time duration (in seconds) and an arbitrary
#  number of ActionObjects (e.g. ActionSound, ActionAnimation, ActionServo) that will occur simultaneously
#  when triggered, and persist for the time duration specified.

PIN_A       = board.GP16                                                # Pi Pico pin associated with Button A
ACTIONS_A   = [ ActionGroup(song_seq_1.get_duration(), song_seq_1),         # get_duration() gives the length of a ActionSoundSequence object
                ActionGroup(5, song_action_1),                            # List of action groups associaciated with Button A
                ActionGroup(3, song_action_2)]

# Create button objects on Pins A and B. The "allow_restart" keyword determines what happens when the button is pushed
# twice sequentially. If "allow_restart" is True, the next action group will start from the beginning. Otherwise all actions will stop
button_a = ButtonTrigger("Button A", PIN_A, ACTIONS_A, allow_restart=True, random_actions=False)  # Button A chooses its action groups randomly

# Create a list of trigger objects
trigger_objects      = [
                         button_a
                       ]


# Run the toy. To add new buttons, create new trigger objects and add them to the list above.
# The main loop that runs the toy is in lib/toy.py
toy = Toy(trigger_objects)
toy.run()
