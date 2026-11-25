# Import statments
import board
import busio

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
from trigger_object.button_trigger import ButtonTrigger

# Import the main loop for the toy
from toy import InstructionGame
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
chase_blue_animation      = ActionAnimation(chase_blue)
chase_red_animation       = ActionAnimation(chase_red)
chase_green_animation     = ActionAnimation(chase_green)

comet_blue_animation       = ActionAnimation(comet_blue)
comet_red_animation        = ActionAnimation(comet_red)
comet_green_animation      = ActionAnimation(comet_green)

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
sound_red_button      = ActionSound(player, 1) # 3 seconds long - "Press the red button"
sound_blue_button     = ActionSound(player, 2) # 3 seconds long - "Press the blue button"
sound_green_button    = ActionSound(player, 3) # 3 seconds long - "Press the green button"

# Sound action objects for the response triggers
sound_pressed_red     = ActionSound(player, 4) # 3 seconds long - "You pressed the red button"
sound_pressed_blue    = ActionSound(player, 5) # 3 seconds long - "You pressed the blue button"
sound_pressed_green   = ActionSound(player, 6) # 3 seconds long - "You pressed the green button"


### --- Create a TriggerObject object for each button and or toggle switch on the board.

# Button A is the button that gives the instructions to the user
PIN_A       = board.GP16
ACTIONS_A   = [ ActionGroup(5, sound_red_button, chase_red_animation),
                ActionGroup(5, sound_blue_button, chase_blue_animation),
                ActionGroup(5, sound_green_button, chase_green_animation)]

# Create the instructions TriggerObject
button_a = ButtonTrigger("Button A", PIN_A, ACTIONS_A, allow_restart=True, random_actions=False)  # Button A is the instructions button and selects random targets when pressed

# Red button parameters
PIN_RED       = board.GP17                # Pi Pico pin attached to button
ACTIONS_RED   = [ ActionGroup(5, sound_pressed_red, comet_red_animation)]

# Blue button parameters
PIN_BLUE       = board.GP18                # Pi Pico pin attached to button
ACTIONS_BLUE   = [ ActionGroup(5, sound_pressed_blue, comet_blue_animation)]

# Toggle switch C
PIN_GREEN       = board.GP19                # Pi Pico pin attached to toggle switch
ACTIONS_GREEN   = [ ActionGroup(5, sound_pressed_green, comet_green_animation)]



# Create Response Trigger Objects
button_red       = ButtonTrigger("Button Red", PIN_RED, ACTIONS_RED, allow_restart=True)
button_blue      = ButtonTrigger("Button Blue", PIN_BLUE, ACTIONS_BLUE, allow_restart=True)
button_green     = ButtonTrigger("Button Green", PIN_GREEN, ACTIONS_GREEN, allow_restart=True)

# Since button_a is the "instructions" button, we are going to add a "target" trigger to each of its
# ActionGroup objects. That target is the specific trigger the instructions tell the child to press
ACTIONS_A[0].set_data("target", button_red)
ACTIONS_A[1].set_data("target", button_blue)
ACTIONS_A[2].set_data("target", button_green)

# Create a list of trigger objects
trigger_objects      = [ button_a,
                         button_red,
                         button_blue,
                         button_green]  # Toggle trigger has the option to toggle when flipped


# Run the game. Button A gives the instructions; the game waits for the user to activate
# the trigger the instruction asked for. A wrong answer repeats the instruction.
# The main loop that runs the game is in lib/toy.py
game = InstructionGame(button_a, trigger_objects)
game.run()
