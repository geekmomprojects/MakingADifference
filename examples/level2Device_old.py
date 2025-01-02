import board
import busio
import time
from dyplayer import DYPlayer
from digitalio import DigitalInOut, Direction, Pull
import random
from adafruit_debouncer import Debouncer
import neopixel
from adafruit_led_animation.animation.chase import Chase

print("Code Starting!")

# TX/RX pins to be connected to RX/TX on the MP3 player
# Pico UART2 TX (GP8) <-> MP3 Player RX
# Pico UART2 RX (GP9) <-> MP3 Player TX
player_uart = busio.UART(board.GP8, board.GP9, baudrate=9600)

# Create Player Object
player = DYPlayer(uart=player_uart)

# set the volume to whatever level you want (0-30)
player.setVolume(15)  

#time.sleep(0.1)  #Leave time to initialize

# Query how many songs on SD card
#numsongs = player.queryNumSongs()
#print("number of songs in directory is ", numsongs)
#time.sleep(0.2)

### SET OUTPUT PINS FOR MP3 ###

### --- Create NeoPixel object and LED animation object -------------------
# Create the pixels object
num_pixels = 10 
pixels = neopixel.NeoPixel(board.GP1, num_pixels, brightness = 0.2, auto_write=False)
pixels.fill((0,0,0))
pixels.show()

# Create an animation object to play on the neopxiels
chase1 = Chase(pixels, speed=0.3, size=1, spacing=2, color=(220,120, 000))
### --- End create NeoPixel and LED animation objects------------------------



### --- Create objects to store properties of each push button ------------

# This class stores the properties associated with each color button the
# user pushes. Useful in keeping all the properties together. You could also
# add other properties later - e.g. a custom LED animation for each button
class ButtonObject:
    def __init__(self, name, pin, color=None, request_track=None, request_duration=0, 
                 success_track=None, success_duration=0):
                
        self.name = name                             # Text value for name - help with identifying button
        self.pin = pin
        self.color = color							  # RGB Color value - used for LED animations
        self.request_track = request_track            # File number of the track that plays the "push the (color) button" sound
        self.request_duration = request_duration      # Duration (in seconds) of the "push the button track"
        self.success_track = success_track            # File number of the track that plays the "you have pusshed the (color) button" sound 
        self.success_duration = success_duration      # Duration (in seconds) of the "you have pushed..." track
        
        # Create a debounced button object
        self.pinobj = DigitalInOut(self.pin)
        self.pinobj.direction = Direction.INPUT
        self.pinobj.pull = Pull.UP
        self.switch = Debouncer(self.pinobj)


# GPIO pin for each button
PIN_START = board.GP16
PIN_GREEN = board.GP17
PIN_BLACK = board.GP18
PIN_YELLOW = board.GP19

# RGB color value to display when each color button is pushed		
COLOR_GREEN = (0, 255, 0)
COLOR_BLACK = (100, 100, 100)  # (NOTE: made LED color dim white for the black button
COLOR_YELLOW = (255, 255, 0)

# File number of the "push the (color) button" audio file
TRACK_PRESS_GREEN = 1
TRACK_PRESS_BLACK = 2
TRACK_PRESS_YELLOW = 3

# Duration (in seconds) of each "push the (color) button" audio file
DURATION_PRESS_GREEN = 5
DURATION_PRESS_BLACK = 5
DURATION_PRESS_YELLOW = 5

# File number of the "you pressed the (color) button" audio file
TRACK_SUCCESS_GREEN = 4
TRACK_SUCCESS_BLACK = 5
TRACK_SUCCESS_YELLOW = 6

# Duration (in seconds) of each "you pressed the (color) button" audio file
DURATION_SUCCESS_GREEN = 5
DURATION_SUCCESS_BLACK = 5
DURATION_SUCCESS_YELLOW = 5

# Create one buttonObject per button, and store them in the list "button_objects".
# Make sure the "start" button is always the first button
button_objects = [
        ButtonObject("start", PIN_START),
        ButtonObject("green", PIN_GREEN, COLOR_GREEN, TRACK_PRESS_GREEN, DURATION_PRESS_GREEN, TRACK_SUCCESS_GREEN, DURATION_SUCCESS_GREEN),
        ButtonObject("black", PIN_BLACK, COLOR_BLACK, TRACK_PRESS_BLACK, DURATION_PRESS_BLACK, TRACK_SUCCESS_BLACK, DURATION_SUCCESS_BLACK),
        ButtonObject("yellow", PIN_YELLOW, COLOR_YELLOW, TRACK_PRESS_YELLOW, DURATION_PRESS_YELLOW, TRACK_SUCCESS_YELLOW, DURATION_SUCCESS_YELLOW) 
        ]
# Create a list of all button objects excluding the start button (i.e. only color buttons are in this list)
color_button_objects = button_objects[1:]

# At any given time, only one button is active and will respond when pressed.
# At the beginnin of the program, that will be the "start" button
active_button = button_objects[0]

### --- End create objects to store push button properties-------------------------------------


# Song_end_time is negative if no song is playing, or contains the value of the
# time the current sound will stop playing if it the user hasn't pushed a button
sound_end_time = -1
is_playing = False
do_animation = False


def start_playing(num, duration, start_animation=False):
    global is_playing, sound_end_time, do_animation
    print("starting sound ", num)
    is_playing = True
    do_animation = start_animation
    player.playByNumber(num)
    sound_end_time = time.monotonic() + duration

def stop_playing():
    global is_playing, sound_end_time, do_animation
    print("ending song")
    is_playing = False
    player.stop()
    sound_end_time = -1		    # Reset sound start timet to -1 to indicate no sound is playing
    
    do_animation = False		# Clear the pixels and stop any animation which is playing
    pixels.fill((0,0,0))		
    pixels.show()

# Main code loop here
while True:
    # Get the time at the beginning of each loop
    now = time.monotonic()
    
    # if appropriate, play an animation on the Neopixel strip
    if do_animation:
        chase1.animate()
        
    # check to see if there is a sound playing, and if it has exceeded the play duration
    if is_playing and now > sound_end_time:
        stop_playing()

    # update the debouncer for all the buttons (both start and color buttons)
    for button in button_objects:
        button.switch.update()

    # check to see if the user pressed any of the buttons. Only the active button
	# will produce a response
    for button in button_objects:
        if button.switch.fell:                                              # Check to see if any of the buttons have been pressed
            print(button.name, " was pressed.")
            if button == active_button:										# if pressed button is the active button, the correct choice was made
                if button == button_objects[0]: 							# the active button was the start button
                    active_button = random.choice(color_button_objects) 	# choose randomly from among the color buttons
                    print("press button ", active_button.name)
                    if active_button.color is not None:						# if button has a color set the animation color
                        chase1.color = active_button.color
                        start_playing(active_button.request_track, active_button.request_duration, start_animation = False)
                else:														# the active button was a color button
                    start_playing(active_button.success_track, active_button.success_duration, start_animation = True)
                    active_button = button_objects[0]						# set the active button back to the start button
            else:                                                           # the wrong button was pressed
                print(" Wrong button, try again.")
