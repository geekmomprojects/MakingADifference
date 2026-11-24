# Import statments
import board
import busio

# Import Sound Player module. Only necessary if toy plays sounds
from dyplayer import DYPlayer

# Import LED animation modules. Only necessary if toy contains LEDs
import neopixel
from adafruit_led_animation.animation.chase import Chase
from adafruit_led_animation.animation.rainbow import Rainbow


# Import modules all action types used (can omit any that are not used)
from action_object.action_animation import ActionAnimation
from action_object.action_sound import ActionSound
from action_object.action_group import ActionGroup

# Import all triggers used (can omit any that are not used)
from trigger_object.button_trigger import ButtonTrigger


### --- Create the Neopixel object and animation(s).
#  Replace num_pixels with thenumber of pixels corresponding to your hardware
num_pixels = 12
pixels = neopixel.NeoPixel(board.GP20, num_pixels, brightness = 0.2, auto_write=False)
pixels.fill((0,0,0))
pixels.show()

chase_blue      = Chase(pixels, speed=0.1, size=1, spacing=2, color=(0,0,255))
chase_red       = Chase(pixels, speed=0.2, size=1, spacing=1, color=(255,0,0))
chase_green     = Chase(pixels, speed=0.1, size=1, spacing=1, color=(0,255,0))

rainbow         = Rainbow(pixels, speed=0.04, period =.6)


### --- Create animation action objects for use in ActionGroups
chase_blue_animation      = ActionAnimation(chase_blue)
chase_red_animation       = ActionAnimation(chase_red)
chase_green_animation     = ActionAnimation(chase_green)
rainbow_animation        = ActionAnimation(rainbow)

### --- End Neopixel/animation initialization
print("Code is starting")

### --- Create the MP3 player object
# TX/RX pins to be connected to RX/TX on the MP3 player
# Pico UART2 TX (GP8) <-> MP3 Player RX
# Pico UART2 RX (GP9) <-> MP3 Player TX
player_uart = busio.UART(board.GP8, board.GP9, baudrate=9600)

# Create Player Object
player = DYPlayer(uart=player_uart)
#time.sleep(0.1)  #Leave time to initialize

# Query how many songs on SD card
#numsongs = player.queryNumSongs()
#print("number of songs in directory is ", numsongs)
#[time.sleep(0.2)
### --- End creating MP3 player object

### --- Create sound action objects to play different tracks

# Sound action objects for the instructions to the user to activate the different triggers
sound_press_b     = ActionSound(player, 13) # 3 seconds long - "Press button B"
sound_press_c     = ActionSound(player, 14) # 3 seconds long - "Press button C"

ACTIONS_A   = [ ActionGroup(5, sound_press_b),
                ActionGroup(5, sound_press_c)]

# Sound action objects for the response triggers
sound_touched_b   = ActionSound(player, 18) # 3 seconds long - "You pressed button B"
action_touched_b  = ActionGroup(5, sound_touched_b, chase_blue_animation)

sound_touched_c   = ActionSound(player, 19) # 3 seconds long - "You touched button C"
action_touched_c  = ActionGroup(5, sound_touched_c, chase_red_animation)

sound_try_again   = ActionSound(player, 10)  # 3 seconds long - "try again"
action_try_again  = ActionGroup(3, sound_try_again, rainbow_animation)


# In the action groups for buttons B and C, the action for an incorrect answer
# is the first item in the list and the action for a correct answer is
# the second item in the list
ACTION_INCORRECT    = 0
ACTION_CORRECT      = 1

ACTIONS_B = [action_try_again, action_touched_b]
ACTIONS_C = [action_try_again, action_touched_c]


# Button A is the button that gives the instructions to the user
PIN_A       = board.GP16
# Create the instructions TriggerObject
button_a = ButtonTrigger("Button A", PIN_A, ACTIONS_A, allow_restart=True, random_actions=True)  # Button A is the instructions button and selects random targets when pressed

# Button B
PIN_B       = board.GP17                # Pi Pico pin attached to button
button_b =   ButtonTrigger("Button B", PIN_B, ACTIONS_B)

PIN_C       = board.GP18                # Pi Pico pin attached to toggle switch
button_c =   ButtonTrigger("Button C", PIN_C, ACTIONS_C)

# Create Response Trigger Objects

# Since button_a is the "instructions" button, we are going to add a "target" trigger to each of its
# ActionGroup objects. That target is the specific trigger the instructions tell the child to press
ACTIONS_A[0].set_data("target", button_b)
ACTIONS_A[1].set_data("target", button_c)

# Create a list of trigger objects
trigger_objects      = [ button_a,
                         button_b,
                         button_c]


# Assign the value of the variable "instruction_trigger" to the trigger that provides instructions to the user
instruction_trigger = button_a

# Variables needed for the main look to track the correct button to press
current_trigger = None                  # button corresponding to the current song or animation playing (None if no song/animation playing)
focus_trigger   = instruction_trigger   # The trigger that currently has the focus. Should initialize with instruction trigger
instruction_index = 0                   # Index (in ACTIONS_A) of the instruction most recently given to the user



# Main loop. No need to change code here to change the number of buttons. To add new buttons, simply create new button objects
while True:
    # If a button is currently active, play its associated actions (song, animation, motor, etc...)
    if current_trigger is not None:
        if not current_trigger.play():                       # Play the current trigger's actions, but check to see if they have ended
            current_trigger.stop()
            current_trigger = None                           # No trigger actions currently playing

    # Update all triggers (updates debouncers)
    for trigger in trigger_objects:
        trigger.update()

    # check to see if the user activated any of the triggers.
    for trigger in trigger_objects:                                          # Iterate over all triggers
        if trigger.is_triggered():                                           # Was the trigger just activated?
            print("")
            print(trigger.name, "was triggered.")
            if current_trigger is not None:
                if trigger == current_trigger:
                    if current_trigger.is_active():                          # if user presses the current trigger while it is
                                                                             #  still playing, ignore it
                        continue
                else:                                                        # There is a currently a different active trigger
                    current_trigger.stop(set_next_action = False)                # Stop the current trigge
            current_trigger = trigger
            if current_trigger == focus_trigger:                                    # User selected the correct trigger
                print("the correct trigger was chosen.")
                if current_trigger == instruction_trigger:
                    current_trigger.advance()
                    instruction_index = current_trigger.group_index            # Remember which instruction is being given
                    focus_trigger = current_trigger.get_current_group_data("target")
                else:
                    current_trigger.set_current_group(ACTION_CORRECT)
                    focus_trigger = instruction_trigger                         # Correct answer, next press should be instructions
            else:
                print("expected trigger ", focus_trigger.name, " but user pressed ", current_trigger.name)
                if current_trigger.is_active():
                    current_trigger.stop()
                if current_trigger == instruction_trigger:                      # User pressed the instructions button instead of the target,
                    current_trigger.set_current_group(instruction_index)       #  so repeat the same instruction (the target hasn't changed)
                else:
                    current_trigger.set_current_group(ACTION_INCORRECT)

            current_trigger.respond_to_trigger()
            break                                                           # Don't allow more than one simultaneous trigger

