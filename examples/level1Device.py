import board
import busio
import time
import neopixel
import random
import neopixel
from dyplayer import DYPlayer
from digitalio import DigitalInOut, Direction, Pull
from adafruit_debouncer import Debouncer
from adafruit_led_animation.animation.chase import Chase
from adafruit_led_animation.animation.rainbow import Rainbow

### --- Create the Neopixel object and animation(s).
#  Replace num_pixels with thenumber of pixels corresponding to your hardware
num_pixels = 8
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
#time.sleep(0.2)
### --- End creating MP3 player object

# This class stores the properties associated with each button the
# user pushes. Useful in keeping all the properties together. You could also
# add other properties later - e.g. a custom LED animation for each button
class ButtonObject:
    def __init__(self, name, pin, animation, track=None, duration=3):

        self.name = name                        # Text value for name - help with identifying button
        self.pin = pin
        self.animation = animation			    # animations
        self.track = track                      # File number or list of file numbers containing sounds
        self.track_index = 0                    # index of the current track
        self.duration = duration                # Duration (in seconds) or list of durations to play the sounds

        # Create a debounced button object
        self.pinobj = DigitalInOut(self.pin)
        self.pinobj.direction = Direction.INPUT
        self.pinobj.pull = Pull.UP
        self.switch = Debouncer(self.pinobj)

    # play_next_track returns the properties associated with the track
    # to be played when the button is pushed, then, if there are a list of
    # tracks associated with the button object, it advances the index of the
    # current track to the next track in the list, and wraps around if the
    # current track is the last track in the list
    def play_next_track(self):
        if type(self.track) is list:
            self.track_index = (self.track_index + 1) % len(self.track)
            t = self.track[self.track_index]
            d = self.duration[self.track_index]
            a = self.animation[self.track_index]
            return t,d,a
        else:
            return self.track

    # Returns the file number of the current track (global variable)associated with
    # this button. This function does NOT advance the track index
    def get_current_track(self):
        if type(self.track) is list:
            return self.track[self.track_index]
        else:
            return self.track


### --- Create a ButtonObject object for each button on the board. Each button has a pin, song, duration and animation

PIN_A       = board.GP16                # Pi Pico pin attached to button
SONG_A      = [1,3]                     # Track number(s) of the song(s): e.g. [2] or [1,2,3] to play
DURATION_A  = [60,20]                   # Duration in seconds of the song(s) to play: e.g. [45] or [60,45,30]
ANIMATION_A = [chase_blue,rainbow]      # animation(s) to play with song(s): e.g. [chase_blue] or [chase_blue, rainbow, chase_red]


PIN_B       = board.GP17                              # Pi Pico pin attached to button
SONG_B      = [2,4,5]                                 # Track number(s) of the song(s): e.g. [2] or [1,2,3] to play
DURATION_B  = [60,25,30]                              # Duration in seconds of the song(s) to play: e.g. [45] or [60,45,30]
ANIMATION_B = [chase_blue,rainbow,chase_red]          # animation(s) to play with song(s): e.g. [chase_blue] or [chase_blue, rainbow, chase_red]


# list of button objects. Add as many buttons as you want to the list, you will not have to change
# the code in the main loop to handle them
button_objects = [ ButtonObject("Button A", PIN_A, track=SONG_A, duration=DURATION_A, animation=ANIMATION_A),
                   ButtonObject("Button B", PIN_B, track=SONG_B, duration=DURATION_B, animation=ANIMATION_B)]

### --- End button creation

# Variables to track the state of the player.
			
sound_end_time = -1			# negative if no song is playing, or contains the start time of the currently playing song
is_playing = False			# boolean which indicates whether a sound is currently playing
current_track = None		# track number of the song being played by the mp3 player
current_animation = None	# currently displayed LED animation

def start_playing(num, duration, animation = None):
    global is_playing, sound_end_time, current_track, current_animation
    print("starting song ", num)
    is_playing = True
    player.playByNumber(num)
    current_track = num
    sound_end_time = time.monotonic() + duration
    if animation is not None:
        current_animation = animation

def stop_playing():
    global is_playing, sound_end_time
    print("ending song")
    is_playing = False
    pixels.fill((0,0,0))
    pixels.show()
    player.stop()
    current_track = -1
    sound_end_time = -1


# Main loop. No need to change code here to change the number of buttons. To add new buttons, simply create new button objects
while True:
    now = time.monotonic()
    if is_playing:
        current_animation.animate()

    # Update all debounced buttons at the beginning of the loop
    for button in button_objects:
        button.switch.update()

    # Check to see if there is a sound playing, and if it has exceeded the play duration
    if is_playing and now > sound_end_time:
        stop_playing()

    # check to see if the user pressed any of the buttons.
    for button in button_objects:
        if button.switch.fell:                                              # Check to see if any of the buttons have been pressed
            print(button.name, " was pressed.")
            if is_playing and button.get_current_track() == current_track:  # User pressed same button twice and it was playing, so stop. If is_playing is true
				stop_playing()												# i.e. sound is coming out of the MP3 player, check to see if it is the same song as
                                                                            # the one the current button would launch. If so stop the current song
            else:
                t,d,a = button.play_next_track()
                start_playing(t,d,a)

