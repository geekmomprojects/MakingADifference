# Import statments
import board
import busio
import time
import pwmio
import random

# Import servo motor module. Only necessary if toy incorporates servos
from adafruit_motor import servo

# Import Sound Player module. Only necessary if toy plays sounds
from dyplayer import DYPlayer

# Import LED animation modules. Only necessary if toy contains LEDs
import neopixel
from adafruit_led_animation.animation.chase import Chase
from adafruit_led_animation.animation.rainbow import Rainbow
from adafruit_led_animation.animation.blink import Blink
from adafruit_led_animation.animation.colorcycle import ColorCycle
from adafruit_led_animation.helper import PixelSubset

# Import modules all action types used (can omit any that are not used)
from action_object.action_servo import ActionServo
from action_object.action_animation import ActionAnimation
from action_object.action_sound import ActionSound
from action_object.action_group import ActionGroup
from action_object.action_group_conditional import ActionGroupConditional

# Import all triggers used (can omit any that are not used)
from trigger_object import TriggerObject
from trigger_object.button_trigger import ButtonTrigger


### --- Create the Neopixel object and animation(s).
### --- Create the Neopixel object and animation(s).
#  Replace num_pixels with thenumber of pixels corresponding to your hardware
num_pixels = 12
pixels = neopixel.NeoPixel(board.GP27, num_pixels, brightness = 0.2, auto_write=False)
pixels.fill((0,0,0))
pixels.show()
pixels_first    = PixelSubset(pixels, 0, 4)  #This is a pixel object that only displays animations on LEDs 0-1 (inclusive) in the pixel string
pixels_second   = PixelSubset(pixels, 4, 8) #This is a pixel object that only displays animations on LEDs 2-3 (inclusive) in the pixel string
pixels_third    = PixelSubset(pixels,8,12) #This is a pixel object that only displays animations on LEDs 4-5 (inclusive) in the pixel string
chase_blue      = Chase(pixels_first, speed=0.1, size=1, spacing=2, color=(0,0,255))
chase_red       = Chase(pixels_second, speed=0.2, size=1, spacing=1, color=(255,0,0))
chase_green     = Chase(pixels_third, speed=0.1, size=1, spacing=1, color=(0,255,0))
blink_blue      = Blink(pixels_first, speed=0.1,  color=(0,0,255))
blink_red       = Blink(pixels_second, speed=0.1,  color=(255,0,0))
blink_green     = Blink(pixels_third, speed=0.1,  color=(0,255,0))
rainbow    = Rainbow(pixels, speed=0.05)

### --- Create animation action objects for use in ActionGroups
chaseBlueAnimation      = ActionAnimation(chase_blue)
chaseRedAnimation       = ActionAnimation(chase_red)
chaseGreenAnimation     = ActionAnimation(chase_green)
blinkBlueAnimation      = ActionAnimation(blink_blue)
blinkRedAnimation       = ActionAnimation(blink_red)
blinkGreenAnimation     = ActionAnimation(blink_green)
rainbowAnimation        = ActionAnimation(rainbow)
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

### --- Create Servo object
# create a PWMOut object on the specified pin. The Raspberry Pi Pico can
# use any pin for PWM, but it is best to use one of the four dedicated
# hardware PWM pins (GPIO 12, GPIO 13, GPIO 18, GPIO 19) because they
# are wired to reduce jitter. Pins 12/18 and 13/19 share some of the same
# resources, so if you plan to have more than one servo moving at a given time,
# then its best to place them on 12/13 or 18/19
SERVO_PIN_1 = board.GP12
servo1 = servo.Servo(pwmio.PWMOut(SERVO_PIN_1, duty_cycle=2 ** 15, frequency=50))

### --- Create servo action object(s) that specifies a servo and its motion
# Different action objects can use the same servo with different movements
servoAction1 = ActionServo("Servo1Motion1", servo1, start_angle=20, end_angle=160, period=3)   # Wide slow steep motion
servoAction2 = ActionServo("Servo1Motion2", servo1, start_angle=90, end_angle=120, period=1)    # Shorter faster sweep motion

### --- Create sound action objects to play different tracks

# Sound action objects for the instructions to the user to activate the different triggers
soundPressB     = ActionSound(player, 13) # 3 seconds long - "Press button B"
soundPressC    = ActionSound(player, 14)  # 3 seconds long - "Press button C"

ACTIONS_A   = [ ActionGroup(5, soundPressB, chaseBlueAnimation),
                ActionGroup(5, soundPressC, chaseGreenAnimation)]

# Create action groups for when the user presses buttons B and C correctly
soundTouchedB   = ActionSound(player, 18) # 3 seconds long - "You pressed button B"
actionTouchedB  = ActionGroup(5, soundTouchedB, chaseBlueAnimation)

soundTouchedC   = ActionSound(player, 19) # 3 seconds long - "You touched button C"
actionTouchedC  = ActionGroup(5, soundTouchedC, chaseRedAnimation)

# Create an action group that tells the user to try again
soundTryAgain   = ActionSound(player, 2)  # 3 seconds long - "try again"
actionTryAgain  = ActionGroup(3, soundTryAgain, rainbowAnimation)

# Create a variable to determine which action in a conditional action group should be played
# the "is_correct_trigger" variable is True or False depending on whether the coorrect
# trigger was selected
is_correct_trigger = False

# If it's the correct button do the first action group, otherwise do the second
def get_action_index():
    if is_correct_trigger:
        return 0
    else:
        return 1

# Create conditional Action Groups that will play a response that tells the
# user they pressed the correct button, or tells the user to try again
ACTIONS_B = ActionGroupConditional(get_action_index, [actionTouchedB, actionTryAgain])
ACTIONS_C = ActionGroupConditional(get_action_index, [actionTouchedC, actionTryAgain])


# Button A is the button that gives the instructions to the user
PIN_A       = board.GP16
# Create the instructions TriggerObject
ButtonA = ButtonTrigger("Button A", PIN_A, ACTIONS_A, allow_restart=True, random_actions=True)  # Button A is the instructions button and selects random targets when pressed

# Button B
PIN_B       = board.GP17                # Pi Pico pin attached to button
ButtonB =   ButtonTrigger("Button B", PIN_B, [ACTIONS_B])

PIN_C       = board.GP18                # Pi Pico pin attached to toggle switch
ButtonC =   ButtonTrigger("Button B", PIN_C, [ACTIONS_C])

# Create Response Trigger Objects

# Since ButtonA is the "instructions" button, we are going to add a "target" trigger to each of its
# ActionGroup objects. That target is the specific trigger the instructions tell the child to press
ACTIONS_A[0].set_data("target", ButtonB)
ACTIONS_A[1].set_data("target", ButtonC)

# Create a list of trigger objects
trigger_objects      = [ ButtonA,
                         ButtonB,
                         ButtonC]


# Assign the value of the variable "instruction_trigger" to the trigger that provides instructions to the user
instruction_trigger = ButtonA

# Variables needed for the main look to track the correct button to press
current_trigger = None                  # button corresponding to the current song or animation playing (None if no song/animation playing)
focus_trigger   = instruction_trigger   # The trigger that currently has the focus. Should initialize with instruction trigger



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
            if current_trigger is not None and trigger != current_trigger:  # There is a currently a different active trigger
                current_trigger.stop(advance_action=False)                   # Stop the current trigge
            current_trigger = trigger
            if current_trigger == focus_trigger:                                    # User selected the correct trigger
                print("the correct trigger was chosen.")
                is_correct_trigger = True
                current_trigger.advance()
                if current_trigger == instruction_trigger:
                    focus_trigger = trigger.get_current_action_data("target")
                else:
                    focus_trigger = instruction_trigger                         # Correct answer, next press should be instructions
            else:
                print("expected trigger ", focus_trigger.name, " but user pressed ", current_trigger.name)
                is_correct_trigger = False

            current_trigger.respond_to_trigger()
            break                                                           # Don't allow more than one simultaneous trigger

