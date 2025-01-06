# Import statments
import board
import busio
import time
import pwmio

# Import servo motor module. Only necessary if toy incorporates servos
#from adafruit_motor import servo

# Import Sound Player module. Only necessary if toy plays sounds
from dyplayer import DYPlayer

# Import LED animation modules. Only necessary if toy contains LEDs
import neopixel
from adafruit_led_animation.animation.chase import Chase
from adafruit_led_animation.animation.comet import Comet

# Import modules all action types used (can omit any that are not used)
#from action_object.action_servo import ActionServo
from action_object.action_animation import ActionAnimation
from action_object.action_sound import ActionSound
from action_object.action_group import ActionGroup

# Import all triggers used (can omit any that are not used)
from trigger_object import TriggerObject
from trigger_object.button_trigger import ButtonTrigger
#from trigger_object.toggle_trigger import ToggleTrigger
#from trigger_object.ping_trigger import PingTrigger
#from trigger_object.ir_trigger import IrTrigger


### --- Create the Neopixel object and animation(s).
### --- Create the Neopixel object and animation(s).
#  Replace num_pixels with thenumber of pixels corresponding to your hardware
num_pixels = 9
pixels = neopixel.NeoPixel(board.GP27, num_pixels, pixel_order=neopixel.GRB, brightness = 0.2, auto_write=False)
pixels.fill((0,0,0))
pixels.show()

chase_blue  = Chase(pixels, speed=0.3, size=1, spacing=2, color=(0,0,255))
chase_red   = Chase(pixels, speed=0.3, size=1, spacing=1, color=(255,0,0))
chase_green = Chase(pixels, speed=0.3, size=1, spacing=1, color=(0,255,0))

comet_blue  = Comet(pixels, speed=0.3, tail_length=4, color=(0,0,255))
comet_red   = Comet(pixels, speed=0.3, tail_length=4, color=(255,0,0))
comet_green = Comet(pixels, speed=0.3, tail_length=4, color=(0,255,0))

### --- Create animation action objects for use in ActionGroups
chaseBlueAnimation      = ActionAnimation(chase_blue)
chaseRedAnimation       = ActionAnimation(chase_red)
chaseGreenAnimation     = ActionAnimation(chase_green)

cometBlueAimation       = ActionAnimation(comet_blue)
cometRedAimation        = ActionAnimation(comet_red)
cometGreenAimation      = ActionAnimation(comet_green)

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
soundRedButton      = ActionSound(player, 1) # 3 seconds long - "Press the red button"
soundBlueButton     = ActionSound(player, 2) # 3 seconds long - "Press the blue button"
soundGreenButton    = ActionSound(player, 3) # 3 seconds long - "Press the green button"

# Sound action objects for the response triggers
soundPressedRed     = ActionSound(player, 4) # 3 seconds long - "You pressed the red button"
soundPressedBlue    = ActionSound(player, 5) # 3 seconds long - "You pressed the blue button"
soundPressedGreen   = ActionSound(player, 6) # 3 seconds long - "You pressed the green button"


### --- Create a TriggerObject object for each button and or toggle switch on the board.

# Button A is the button that gives the instructions to the user
PIN_A       = board.GP16
ACTIONS_A   = [ ActionGroup(5, soundRedButton, chaseRedAnimation),
                ActionGroup(5, soundBlueButton, chaseBlueAnimation),
                ActionGroup(5, soundGreenButton, chaseGreenAnimation)]

# Create the instructions TriggerObject
ButtonA = ButtonTrigger("Button A", PIN_A, ACTIONS_A, allow_restart=True, random_actions=False)  # Button A is the instructions button and selects random targets when pressed

# Red button parameters
PIN_RED       = board.GP17                # Pi Pico pin attached to button
ACTIONS_RED   = [ ActionGroup(5, soundPressedRed, cometRedAimation)]

# Blue button parameters
PIN_BLUE       = board.GP18                # Pi Pico pin attached to button
ACTIONS_BLUE   = [ ActionGroup(5, soundPressedBlue, cometBlueAimation)]

# Toggle switch C
PIN_GREEN       = board.GP19                # Pi Pico pin attached to toggle switch
ACTIONS_GREEN   = [ ActionGroup(5, soundPressedGreen, cometGreenAimation)]



# Create Response Trigger Objects
ButtonRed       = ButtonTrigger("Button Red", PIN_RED, ACTIONS_RED, allow_restart=True)
ButtonBlue      = ButtonTrigger("Button Blue", PIN_BLUE, ACTIONS_BLUE, allow_restart=True)
ButtonGreen     = ButtonTrigger("Button Green", PIN_GREEN, ACTIONS_GREEN, allow_restart=True)

# Since ButtonA is the "instructions" button, we are going to add a "target" trigger to each of its
# ActionGroup objects. That target is the specific trigger the instructions tell the child to press
ACTIONS_A[0].set_data("target", ButtonRed)
ACTIONS_A[1].set_data("target", ButtonBlue)
ACTIONS_A[2].set_data("target", ButtonGreen)

# Create a list of trigger objects
trigger_objects      = [ ButtonA,
                         ButtonRed,
                         ButtonBlue,
                         ButtonGreen]  # Toggle trigger has the option to toggle when flipped


# Assign the value of the variable "instruction_trigger" to the trigger that provides instructions to the user
instruction_trigger = ButtonA


# Main loop. No need to change code here to change the number of buttons. To add new buttons, simply create new button objects
current_trigger = None                  # button corresponding to the current song or animation playing (None if no song/animation playing)
focus_trigger   = instruction_trigger   # The trigger that currently has the focus. Should initialize with instruction trigger

while True:
    # If a button is currently active, play its associated actions (song, animation, motor, etc...)
    if current_trigger is not None:
        if not current_trigger.play():                       # Play the current trigger's actions, but check to see if they have ended
            if current_trigger == instruction_trigger:       # The trigger that just finished playing was the instrctions trigger
                current_trigger.stop(set_next_action=False)  #  Actions have ended. Actively stop trigger, but don't advance actions group until the focus trigger is selected
            else:                                            # The trigger was not the instructions trigger
                current_trigger.stop(set_next_action=True)   #  Actively stop focus trigger to advance its action group
            current_trigger = None                           # No trigger actions currently playing

    # Update all triggers (updates debouncers)
    for trigger in trigger_objects:
        trigger.update()

    # check to see if the user activated any of the triggers.
    for trigger in trigger_objects:                                          # Iterate over all triggers
        if trigger.is_triggered():                                           # Was the trigger just activated?
            print("")
            print(trigger.name, "was triggered.")
            if current_trigger is not None and trigger != current_trigger:   # There is a currently a different active trigger
                current_trigger.stop(set_next_action=False)                 # Dont advance action group unless it's the right response
            if trigger == focus_trigger:                                    # User selected the correct trigger
                print("the correct trigger was chosen.")
                trigger.start()                                             # New trigger responds to activation
                current_trigger = trigger
                if trigger == instruction_trigger:                          # Instructions trigger activated - figure out new target/focus trigger
                    new_focus = trigger.get_current_action_data("target")
                    if new_focus is not None:
                        focus_trigger = new_focus
                else:
                    focus_trigger = instruction_trigger                     # If target was activated - set focus back to instructions trigger
                    instruction_trigger.advance()                           # Advance instructions to the next target
            else:
                print("the wrong trigger was chosen. The correct trigger was", focus_trigger.name)
                if focus_trigger != instruction_trigger:
                    current_trigger = instruction_trigger                   # Wrong trigger was selected, so play instructions again
                    current_trigger.start()
            break                                                           # Don't allow more than one simultaneous trigger

