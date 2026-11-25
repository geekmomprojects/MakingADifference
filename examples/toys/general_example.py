# Import necessary libraries
import board
import busio
import pwmio

# Import servo motor module(library). Only necessary if toy incorporates servos. 
from adafruit_motor import servo

# Import Sound Player module(library). Only necessary if toy plays sounds
from dyplayer import DYPlayer                              # Debra's library

# Import LED animation modules(libraries). Only necessary if toy contains LEDs
import neopixel
from adafruit_led_animation.animation.chase import Chase
from adafruit_led_animation.animation.rainbow import Rainbow

# Import modules(libraries) all action types used (can omit any that are not used)   # Debra's library
from action_object.action_servo import ActionServo         
from action_object.action_animation import ActionAnimation
from action_object.action_sound import ActionSound
from action_object.action_group import ActionGroup

# Import all triggers used (can omit any that are not used)                          # Debra's library
from trigger_object.button_trigger import ButtonTrigger
from trigger_object.toggle_trigger import ToggleTrigger
from trigger_object.ping_trigger import PingTrigger
from trigger_object.ir_trigger import IrTrigger

# Import the main loop for the toy
from toy import Toy

### --- Hardware settings. Change these to match how your toy is wired.
# board.GP16 means the pin labelled GP16 on the Pico (not the 16th physical pin)
BUTTON_A_PIN   = board.GP16  # Button A
BUTTON_B_PIN   = board.GP17  # Button B
TOGGLE_C_PIN   = board.GP18  # Toggle switch C
IR_PIN         = board.GP19  # IR sensor output
PING1_TRIG_PIN = board.GP4   # Ping sensor Trig
PING1_ECHO_PIN = board.GP5   # Ping sensor Echo
SERVO1_PIN     = board.GP12  # Servo signal (see the note about PWM pins where the servo is created)
PIXELS_PIN     = board.GP27  # NeoPixel strip data in
NUM_PIXELS     = 9           # Number of LEDs on the NeoPixel strip
MP3_TX_PIN     = board.GP8   # Pico TX -> MP3 player RX
MP3_RX_PIN     = board.GP9   # Pico RX <- MP3 player TX



### --- Create the Neopixel object storing and defining the strip properties.
pixels = neopixel.NeoPixel(PIXELS_PIN, NUM_PIXELS, brightness = 0.2, auto_write=False)
pixels.fill((0,0,0))
pixels.show()

### --- Creating objects of type animation and specifying their properties. (pixels, which was defined above, is the first argument of the animation object)

chase_blue = Chase(pixels, speed=0.3, size=1, spacing=2, color=(0,0,255))  ### creating a chase object that will run an animation stored in a variable called chase_blue
chase_red  = Chase(pixels, speed=0.3, size=1, spacing=1, color=(255,0,0))  ### creating a chase object that will run an animation stored in a variable called chase_red
rainbow    = Rainbow(pixels, speed=0.3)                                    ### creating a rainbow object that will run an animation stored in a variable called rainbow

### --- Create animation action objects for use in ActionGroups. These action objects take an animation as their argument. The ActionAnimation is a class inside the Action_Object library Debra wrote
chase_blue_animation  = ActionAnimation(chase_blue)
rainbow_animation    = ActionAnimation(rainbow)
chase_red_animation   = ActionAnimation(chase_red)

### --- End Neopixel/animation initialization

print("Code is starting")

### --- Create the MP3 player object
# TX/RX pins to be connected to RX/TX on the MP3 player
# (the pins are set at the top of this file)
player_uart = busio.UART(MP3_TX_PIN, MP3_RX_PIN, baudrate=9600)

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
servo1 = servo.Servo(pwmio.PWMOut(SERVO1_PIN, duty_cycle=2 ** 15, frequency=50))

### --- Create servo action object(s) that specifies a servo and its motion
# Different action objects can use the same servo with different movements
servo_action_1 = ActionServo("Servo1Motion1", servo1, start_angle=20, end_angle=160, period=3)   # Wide slow steep motion
servo_action_2 = ActionServo("Servo1Motion2", servo1, start_angle=90, end_angle=120, period=1)    # Shorter faster sweep motion

### --- Create sound action objects to play different tracks
song_action_1 = ActionSound(player, 1)
song_action_2 = ActionSound(player, 2)
song_action_3 = ActionSound(player, 3)
song_action_4 = ActionSound(player, 4)
song_action_5 = ActionSound(player, 5)
song_action_6 = ActionSound(player, 6)
song_action_7 = ActionSound(player, 7)
song_action_8 = ActionSound(player, 8)
song_action_9 = ActionSound(player, 9)
song_action_10 = ActionSound(player, 10)


### --- Create a TriggerObject object for each trigger in the toy. Each trigger object takes a
#  list of one or more ActionGroupObjects. An ActionGroup contains a time duration (in seconds) and an arbitrary
#  number of ActionObjects (e.g. ActionSound, ActionAnimation, ActionServo) that will occur simultaneously
#  when triggered, and persist for the time duration specified. You can have just one action.

##### First we must create and define properties for each trigger object. 


ACTIONS_A   = [ ActionGroup(5, song_action_1, chase_blue_animation),        # List of action groups associaciated with Button A
                ActionGroup(8, song_action_2, rainbow_animation),          # Each action group plays a sound and an LED animation
                ActionGroup(12, song_action_3, chase_red_animation)]

ACTIONS_B   = [ ActionGroup(60, song_action_3, chase_blue_animation, servo_action_1), # List of action groups associated with Button B
                ActionGroup(60, song_action_4, rainbow_animation, servo_action_1),   # Eacg action group plays a sound,
                ActionGroup(20, song_action_5, chase_red_animation, servo_action_1) ]

ACTIONS_C   = [ ActionGroup(60, song_action_3, rainbow_animation) ]                # List (only containing one group) of action groups associated with toggle button C

ACTIONS_IR  = [ ActionGroup(5, song_action_7, chase_red_animation) ]

ACTIONS_PING   = [  ActionGroup(6, song_action_8, chase_blue_animation, servo_action_2),  # List of action groups associated with the Ping Trigger
                    ActionGroup(6, song_action_9, rainbow_animation, servo_action_2),
                    ActionGroup(6, song_action_10, chase_red_animation, servo_action_2) ]

####### Now, create trigger objects using the properties we defined above. The first property is the name, etc. 

ping_1 = PingTrigger("Ping1", PING1_TRIG_PIN, PING1_ECHO_PIN, 8, ACTIONS_PING, allow_restart=True)  # Sonar sensor on pins

# Create button objects on Pins A and B. The "allow_restart" keyword determines what happens when the button is pushed
# twice sequentially. If "allow_restart" is True, the next action group will start from the beginning. Otherwise all actions will stop
# look in Debra's lib/trigger_object/button_trigger.py for arggument list

button_a = ButtonTrigger("Button A", BUTTON_A_PIN, ACTIONS_A, allow_restart=True, random_actions=True)  # Button A chooses its action groups randomly
button_b = ButtonTrigger("Button B", BUTTON_B_PIN, ACTIONS_B, allow_restart=True)                       # Button B iterates through its action groups sequentially (the default)

# Create IR Trigger objects
trigger_ir = IrTrigger("IR Trigger", IR_PIN, ACTIONS_IR, allow_restart=True)                     # IR Trigger craeted

# Create a toggle switch object. Like a button but has the "toggle_both" keyword which determines whether it triggers when flipped one way (False) or both ways (True)
toggle_c = ToggleTrigger("Toggle C", TOGGLE_C_PIN, ACTIONS_C, allow_restart=False, toggle_both=True)


# Create a list of trigger objects
trigger_objects      = [ ping_1,
                         button_a,
                         button_b,
                         trigger_ir,
                         toggle_c ]


# Run the toy. To add new buttons, create new trigger objects and add them to the list above.
# The main loop that runs the toy is in lib/toy.py
toy = Toy(trigger_objects)
toy.run()
