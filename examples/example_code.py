
import board
import busio
import time
import neopixel
#import random
import pwmio
from adafruit_motor import servo

from dyplayer import DYPlayer
from adafruit_led_animation.animation.chase import Chase
from adafruit_led_animation.animation.rainbow import Rainbow
from adafruit_led_animation.animation.comet import Comet
from adafruit_led_animation.animation.colorcycle import ColorCycle

# Import all action types used
from action_object.action_servo import ActionServo
from action_object.action_animation import ActionAnimation
from action_object.action_sound import ActionSound
from action_object.action_group import ActionGroup

# Import all triggers used
from trigger_object import TriggerObject
from trigger_object.button_trigger import ButtonTrigger
from trigger_object.toggle_trigger import ToggleTrigger
from trigger_object.ping_trigger import PingTrigger



### --- Create the Neopixel object and animation(s).
#  Replace num_pixels with thenumber of pixels corresponding to your hardware
num_pixels = 9
pixels = neopixel.NeoPixel(board.GP27, num_pixels, brightness = 0.2, auto_write=False)
pixels.fill((0,0,0))
pixels.show()

chase_blue = Chase(pixels, speed=0.3, size=1, spacing=2, color=(0,0,255))
chase_red  = Chase(pixels, speed=0.3, size=1, spacing=1, color=(255,0,0))
rainbow    = Rainbow(pixels, speed=0.3)

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

### --- Create a servo action object that specifies a servo and its motion
servoAction1 = ActionServo("Servo1Motion1", servo1, start_angle=20, end_angle=160, period=3)

### --- Create sound action objects to play different tracks
songAction1 = ActionSound(player, 1)
songAction2 = ActionSound(player, 2)
songAction3 = ActionSound(player, 3)

### --- Create animation action objects
chaseBlueAnimation  = ActionAnimation(chase_blue)
rainbowAnimation    = ActionAnimation(rainbow)
chaseRedAnimation   = ActionAnimation(chase_red)

### --- Create a TriggerObject object for each button and or toggle switch on the board.
# Each button has a pin, duration, and animation
# Button B activates a motor as well

PIN_A       = board.GP16                # Pi Pico pin attached to button
ACTIONS_A   = [ ActionGroup(60, songAction1, chaseBlueAnimation),
                ActionGroup(20, songAction1, rainbowAnimation) ]

PIN_B       = board.GP17                # Pi Pico pin attached to button
ACTIONS_B   = [ ActionGroup(60, songAction2, chaseBlueAnimation, servoAction1),
                ActionGroup(60, songAction2, rainbowAnimation, servoAction1),
                ActionGroup(20, songAction2, chaseRedAnimation, servoAction1) ]

PIN_C       = board.GP18                # Pi Pico pin attached to button
ACTIONS_C   = [ ActionGroup(60, songAction3, rainbowAnimation) ]

#Create a Ping trigger object
Ping1 = PingTrigger ("Ping1", board.GP14, board.GP15, 8, ACTIONS_B)

ButtonA = ButtonTrigger("Button A", PIN_A, ACTIONS_A, allow_restart=False)
ButtonB = ButtonTrigger("Button B", PIN_B, ACTIONS_B, allow_restart=True)
ToggleC = ToggleTrigger("Toggle C", PIN_C, ACTIONS_C, allow_restart=False, toggle_both=True) # both ways or only when flipped one way (toggle_both keyword)

trigger_objects      = [ Ping1,
                         ButtonA,
                         ButtonB,
                         ToggleC ]  # Toggle trigger has the option to toggle when flipped


### --- End trigger creation			



# Main loop. No need to change code here to change the number of buttons. To add new buttons, simply create new button objects
current_trigger = None          # button corresponding to the current song or animation playing (None if no song/animation playing)

while True:
    # If a button is currently active, play its associated actions (song, animation, motor, etc...)
    if current_trigger is not None:
        if not current_trigger.play():   # Play the current trigger's actions, but check to see if they have ended
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
            trigger.respond_to_trigger()                                     # Trigger responds
            if trigger.is_active():
                current_trigger = trigger
            else:
                current_trigger = None


