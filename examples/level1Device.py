import board
import busio
import time
import neopixel
from dyplayer import DYPlayer
from digitalio import DigitalInOut, Direction, Pull
import random
from adafruit_debouncer import Debouncer
import neopixel
from adafruit_led_animation.animation.chase import Chase

### --- Create the Neopixel object and animation(s)
num_pixels = 38
pixels = neopixel.NeoPixel(board.GP0, num_pixels, brightness = 0.2, auto_write=False)
pixels.fill((0,0,0))
pixels.show()

chase = Chase(pixels, speed=0.3, size=1, spacing=2, color=(220,120, 000))
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
#time.sleep(0.2)
### --- End creating MP3 player object

# This class stores the properties associated with each button the
# user pushes. Useful in keeping all the properties together. You could also
# add other properties later - e.g. a custom LED animation for each button
class ButtonObject:
    def __init__(self, name, pin, track=None, duration=3, color=None):

        self.name = name                             # Text value for name - help with identifying button
        self.pin = pin
        self.color = color							  # RGB Color value - used for LED animations
        self.track = track                            # File number of the sound
        self.duration = duration                      # Duration (in seconds) to play the sound

        # Create a debounced button object
        self.pinobj = DigitalInOut(self.pin)
        self.pinobj.direction = Direction.INPUT
        self.pinobj.pull = Pull.UP
        self.switch = Debouncer(self.pinobj)



### --- Create a ButtonObject object for each button on the board. Each button has a song, duration and 
###     color associated with it. 

PIN_A       = board.GP1      # Pi Pico pin attached to button
SONG_A      = 1              # Track number of the song to play
DURATION_A  = 5              # Duration in seconds of the song
COLOR_A     = (0, 255, 0)    # Color of the animation to play with this song

PIN_B       = board.GP2
SONG_B      = 2
DURATION_B  = 5
COLOR_B      = (255, 0, 0)

PIN_C       = board.GP4
SONG_C      = 3
DURATION_C  = 5
COLOR_C      = (0, 0, 255)

# list of button objects. Add as many buttons as you want to the list, you will not have to change
# the code in the main loop to handle them
button_objects = [ ButtonObject("Button A", PIN_A, track=SONG_A, duration=DURATION_A, color=COLOR_A),
                   ButtonObject("Button B", PIN_B, track=SONG_B, duration=DURATION_B, color=COLOR_B),
                   ButtonObject("Button C", PIN_C, track=SONG_C, duration=DURATION_C, color=COLOR_C)
                 ]
                 
### --- End button creation

# Variables to track the state of the player.
# Song_end_time is negative if no song is playing, or contains the value of the
# start time of the current song
sound_end_time = -1
is_playing = False
current_track = None

def start_playing(num, duration, color=None):
    global is_playing, sound_end_time, current_track
    print("starting song ", num)
    is_playing = True
    player.playByNumber(num)
    current_track = num
    sound_end_time = time.monotonic() + duration
    if color is not None:
        chase.color = color

def stop_playing():
    global is_playing, sound_end_time
    print("ending song")
    is_playing = False
    pixels.fill((0,0,0))
    pixels.show()
    player.stop()
    current_track = -1
    sound_end_time = -1


# Main loop. No need to change code here. To add new buttons, simply create new button objects 
while True:
    now = time.monotonic()
    if is_playing:
        chase.animate()
    
    # Update all debounced buttons at the beginning of the loop
    for button in button_objects:
        button.switch.update()
        
    # Check to see if there is a sound playing, and if it has exceeded the play duration
    if is_playing and now > sound_end_time:
        stop_playing()
        
    # check to see if the user pressed any of the buttons.
    for button in button_objects:
        if button.switch.fell:                                  # Check to see if any of the buttons have been pressed
            print(button.name, " was pressed.")
            if is_playing and button.track == current_track:    # User pressed same button twice and it was playing, so stop
                stop_playing()
            else:
                start_playing(button.track, button.duration, button.color)
            
