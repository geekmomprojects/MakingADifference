# Import necessary libraries
import board
import busio
import time
import pwmio

# Import servo motor module(library). Only necessary if toy incorporates servos. 
from adafruit_motor import servo

# Import Sound Player module(library). Only necessary if toy plays sounds
from dyplayer import DYPlayer                              # Debra's library

# Import LED animation modules(libraries). Only necessary if toy contains LEDs
import neopixel
from adafruit_led_animation.animation.chase import Chase
from adafruit_led_animation.animation.rainbow import Rainbow
from adafruit_led_animation.animation.comet import Comet
from adafruit_led_animation.animation.colorcycle import ColorCycle

# Import modules(libraries) all action types used (can omit any that are not used)   # Debra's library
from action_object.action_servo import ActionServo         
from action_object.action_animation import ActionAnimation
from action_object.action_sound import ActionSound
from action_object.action_group import ActionGroup

# Import all triggers used (can omit any that are not used)                          # Debra's library
from trigger_object import TriggerObject
from trigger_object.button_trigger import ButtonTrigger
from trigger_object.toggle_trigger import ToggleTrigger
from trigger_object.ping_trigger import PingTrigger
from trigger_object.ir_trigger import IrTrigger



### --- Create the Neopixel object storing and defining the strip properties.
#  Replace num_pixels with thenumber of pixels corresponding to your hardware
num_pixels = 9
pixels = neopixel.NeoPixel(board.GP27, num_pixels, brightness = 0.2, auto_write=False)
pixels.fill((0,0,0))
pixels.show()

### --- Creating objects of type animation and specifying their properties. (pixels, which was defined on line 38, is the first argument of the animation object)

chase_blue = Chase(pixels, speed=0.3, size=1, spacing=2, color=(0,0,255))  ### creating a chase object that will run an animation stored in a variable called chase_blue
chase_red  = Chase(pixels, speed=0.3, size=1, spacing=1, color=(255,0,0))  ### creating a chase object that will run an animation stored in a variable called chase_red
rainbow    = Rainbow(pixels, speed=0.3)                                    ### creating a rainbow object that will run an animation stored in a variable called rainbow

### --- Create animation action objects for use in ActionGroups. These action objects take an animation as their argument. The ActionAnimation is a class inside the Action_Object library Debra wrote
chaseBlueAnimation  = ActionAnimation(chase_blue)
rainbowAnimation    = ActionAnimation(rainbow)
chaseRedAnimation   = ActionAnimation(chase_red)

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
songAction1 = ActionSound(player, 1)
songAction2 = ActionSound(player, 2)
songAction3 = ActionSound(player, 3)
songAction4 = ActionSound(player, 4)
songAction5 = ActionSound(player, 5)
songAction6 = ActionSound(player, 6)
songAction7 = ActionSound(player, 7)
songAction8 = ActionSound(player, 8)
songAction9 = ActionSound(player, 9)
songAction10 = ActionSound(player, 10)


### --- Create a TriggerObject object for each trigger in the toy. Each trigger object takes a
#  list of one or more ActionGroupObjects. An ActionGroup contains a time duration (in seconds) and an arbitrary
#  number of ActionObjects (e.g. ActionSound, ActionAnimation, ActionServo) that will occur simultaneously
#  when triggered, and persist for the time duration specified. You can have just one action.

# First we will create the properties for each trigger object. 

PIN_A       = board.GP16                                                # Pi Pico pin associated with Button A, This button can be pressed 3 times to execute 3 different action groups
ACTIONS_A   = [ ActionGroup(5, songAction1, chaseBlueAnimation),        # List of action groups associaciated with Button A
                ActionGroup(8, songAction2, rainbowAnimation),          # Each action group plays a sound and an LED animation
                ActionGroup(12, songAction3, chaseRedAnimation)]

PIN_B       = board.GP17                                                        # Pi Pico pin attached to Button B
ACTIONS_B   = [ ActionGroup(60, songAction3, chaseBlueAnimation, servoAction1), # List of action groups associated with Button B
                ActionGroup(60, songAction4, rainbowAnimation, servoAction1),   # Eacg action group plays a sound,
                ActionGroup(20, songAction5, chaseRedAnimation, servoAction1) ]

PIN_C       = board.GP18                                                        # Pi Pico pin attached to Toggle Switch C
ACTIONS_C   = [ ActionGroup(60, songAction3, rainbowAnimation) ]                # List (only containing one group) of action groups associated with toggle button C

PIN_IR      = board.GP19
ACTIONS_IR  = [ ActionGroup(5, songAction7, chaseRedAnimation) ]

ACTIONS_PING   = [  ActionGroup(6, songAction8, chaseBlueAnimation, servoAction2),  # List of action groups associated with the Ping Trigger
                    ActionGroup(6, songAction9, rainbowAnimation, servoAction2),
                    ActionGroup(6, songAction10, chaseRedAnimation, servoAction2) ]

#Create a Ping trigger object. The first property is the name, etc. 

Ping1 = PingTrigger ("Ping1", board.GP14, board.GP15, 8, ACTIONS_PING, allow_restart=True)  # Sonar sensor on pins

# Create button objects on Pins A and B. The "allow_restart" keyword determines what happens when the button is pushed
# twice sequentially. If "allow_restart" is True, the next action group will start from the beginning. Otherwise all actions will stop
# look in Debra's lib/trigger_object/button_trigger.py for arggument list

ButtonA = ButtonTrigger("Button A", PIN_A, ACTIONS_A, allow_restart=True, random_actions=True)  # Button A chooses its action groups randomly
ButtonB = ButtonTrigger("Button B", PIN_B, ACTIONS_B, allow_restart=True)                       # Button B iterates through its action groups sequentially (the default)

# Create IR Trigger objects
TriggerIR = IrTrigger("IR Trigger", PIN_IR, ACTIONS_IR, allow_restart=True)                     # IR Trigger craeted

# Create a toggle switch object. Like a button but has the "toggle_both" keyword which determines whether it triggers when flipped one way (False) or both ways (True)
ToggleC = ToggleTrigger("Toggle C", PIN_C, ACTIONS_C, allow_restart=False, toggle_both=True)


# Create a list of trigger objects
trigger_objects      = [ Ping1,
                         ButtonA,
                         ButtonB,
                         TriggerIR,
                         ToggleC ]


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

