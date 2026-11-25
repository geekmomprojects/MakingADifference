# Import statments
import board
import busio
import pwmio

# Import servo motor module. Only necessary if toy incorporates servos
from adafruit_motor import servo

# Import Sound Player module. Only necessary if toy plays sounds
from dyplayer import DYPlayer

# Import LED animation modules. Only necessary if toy contains LEDs
import neopixel
from adafruit_led_animation.animation.chase import Chase
from adafruit_led_animation.animation.rainbow import Rainbow

# Import modules all action types used (can omit any that are not used)
from action_object.action_servo import ActionServo
from action_object.action_animation import ActionAnimation
from action_object.action_sound import ActionSound
from action_object.action_group import ActionGroup

# Import all triggers used (can omit any that are not used)
from trigger_object.button_trigger import ButtonTrigger
from trigger_object.toggle_trigger import ToggleTrigger
from trigger_object.ping_trigger import PingTrigger

# Import the main loop for the toy
from toy import InstructionGame
#from trigger_object.ir_trigger import IrTrigger


### --- Create the Neopixel object and animation(s).
### --- Create the Neopixel object and animation(s).
#  Replace num_pixels with thenumber of pixels corresponding to your hardware
num_pixels = 9
pixels = neopixel.NeoPixel(board.GP27, num_pixels, brightness = 0.2, auto_write=False)
pixels.fill((0,0,0))
pixels.show()

chase_blue = Chase(pixels, speed=0.3, size=1, spacing=2, color=(0,0,255))
chase_red  = Chase(pixels, speed=0.3, size=1, spacing=1, color=(255,0,0))
rainbow    = Rainbow(pixels, speed=0.3)

### --- Create animation action objects for use in ActionGroups
chase_blue_animation  = ActionAnimation(chase_blue)
rainbow_animation    = ActionAnimation(rainbow)
chase_red_animation   = ActionAnimation(chase_red)

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
servo_action_1 = ActionServo("Servo1Motion1", servo1, start_angle=20, end_angle=160, period=3)   # Wide slow steep motion
servo_action_2 = ActionServo("Servo1Motion2", servo1, start_angle=90, end_angle=120, period=1)    # Shorter faster sweep motion

### --- Create sound action objects to play different tracks

# Sound action objects for the instructions to the user to activate the different triggers
sound_press_b     = ActionSound(player, 13) # 3 seconds long - "Press button B"
sound_toggle_c    = ActionSound(player, 14) # 3 seconds long - "Toggle switch C"
song_activate_p   = ActionSound(player, 15) # 3 seconds long - "Activate the ping sensor"

# Sound action objects for the response triggers
sound_touched_b   = ActionSound(player, 18) # 3 seconds long - "You pressed button B"
sound_toggled_c   = ActionSound(player, 19) # 3 seconds long - "You toggled switch C"
sound_activated_p = ActionSound(player, 20) # 3 seconds long - "You activated the ping sensor"


### --- Create a TriggerObject object for each button and or toggle switch on the board.

# Button A is the button that gives the instructions to the user
PIN_A       = board.GP16
ACTIONS_A   = [ ActionGroup(5, sound_press_b, chase_blue_animation),
                ActionGroup(5, sound_toggle_c, rainbow_animation),
                ActionGroup(5, song_activate_p, chase_red_animation)]

# Create the instructions TriggerObject
button_a = ButtonTrigger("Button A", PIN_A, ACTIONS_A, allow_restart=True, random_actions=True)  # Button A is the instructions button and selects random targets when pressed

# Button B activates a motor when pressed
PIN_B       = board.GP17                # Pi Pico pin attached to button
ACTIONS_B   = [ ActionGroup(4, sound_touched_b, chase_blue_animation, servo_action_1),
                ActionGroup(4, sound_touched_b, rainbow_animation, servo_action_1),
                ActionGroup(4, sound_touched_b, chase_red_animation, servo_action_1) ]

# Toggle switch C
PIN_C       = board.GP18                # Pi Pico pin attached to toggle switch
ACTIONS_C   = [ ActionGroup(4, sound_toggled_c, rainbow_animation) ]

# Action groups triggered by the ping sensor
ACTIONS_PING   = [  ActionGroup(4, sound_activated_p, chase_blue_animation, servo_action_1),
                    ActionGroup(4, sound_activated_p, rainbow_animation, servo_action_1),
                    ActionGroup(4, sound_activated_p, chase_red_animation, servo_action_1) ]

# Create Response Trigger Objects
button_b = ButtonTrigger("Button B", PIN_B, ACTIONS_B, allow_restart=True)
toggle_c = ToggleTrigger("Toggle C", PIN_C, ACTIONS_C, allow_restart=True, toggle_both=False) # both ways or only when flipped one way (toggle_both keyword)
ping_1 = PingTrigger ("Ping1",board.GP14, board.GP15, 8, ACTIONS_PING, allow_restart=True)

# Since button_a is the "instructions" button, we are going to add a "target" trigger to each of its
# ActionGroup objects. That target is the specific trigger the instructions tell the child to press
ACTIONS_A[0].set_data("target", button_b)
ACTIONS_A[1].set_data("target", toggle_c)
ACTIONS_A[2].set_data("target", ping_1)

# Create a list of trigger objects
trigger_objects      = [ button_a,
                         button_b,
                         toggle_c,
                         ping_1]  # Toggle trigger has the option to toggle when flipped


# Run the game. Button A gives the instructions; the game waits for the user to activate
# the trigger the instruction asked for. A wrong answer repeats the instruction.
# The main loop that runs the game is in lib/toy.py
game = InstructionGame(button_a, trigger_objects)
game.run()
