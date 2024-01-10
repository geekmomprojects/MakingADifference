#This code uses two ping sensors. When each ping sensor detects a certain distance
#a song file is triggered.

import time
import board
import busio
from digitalio import DigitalInOut, Direction, Pull
import board
import neopixel
import adafruit_hcsr04
from dyplayer import DYPlayer, PlayMode
from adafruit_debouncer import Debouncer
import random

### --- Create MP3 player object ---
print("Code Starting!")

# TX/RX pins to be connected to RX/TX on the MP3 player
# Pico UART2 TX (GP8) <-> MP3 Player RX
# Pico UART2 RX (GP9) <-> MP3 Player TX
player_uart = busio.UART(board.GP8, board.GP9, baudrate=9600)

# Create Player Object
player = DYPlayer(uart=player_uart)
time.sleep(0.2)

# set the volume to whatever level you want (0-30)
player.setVolume(24)
time.sleep(0.1)

# Set the default player behavior to repeat the current
# sound until told to stop
player.setCycleMode(PlayMode.REPEAT_ONE)
time.sleep(0.1)
# The song will repeat up to 32 times unless actively stopped
player.setCycleTimes(32)
time.sleep(0.1)
### --- End create MP3 player object

### --- Create NeoPixel object ---
num_pixels = 15     # Update this to match the number of NeoPixel LEDs connected to your board.
brightness = 0.5
pixels = neopixel.NeoPixel(board.GP3, num_pixels, brightness=brightness)
### --- End create NeoPixel object


# Class to hold properties of a button, including the pixels it controls
# and the colors they will turn
class ButtonObject:
    def __init__(self, name, pin, pixels, pixrange, color):
        self.name = name
        self.pixels = pixels
        self.pixrange = pixrange
        self.color = color

        # Create a debounced button object
        self.pin = pin
        self.pinobj = DigitalInOut(self.pin)
        self.pinobj.direction = Direction.INPUT
        self.pinobj.pull = Pull.UP
        self.switch = Debouncer(self.pinobj)



# Class to control the properties of a sonar sensor. When the sonar detects an object
# within a specified distance (in cm), it will play a specified song track until duation
# seconds aftger the object is removed, or until a a different sonar sensor is detected.
class SonarObject:
    def __init__(self, name, trigger_pin, echo_pin, cutoff_distance, mp3_player, track, duration):
        self.name               = name
        self.sonar              = adafruit_hcsr04.HCSR04(trigger_pin=trigger_pin,echo_pin=echo_pin)
        self.last_read_time     = 0
        self.cutoff_distance    = cutoff_distance
        self.current_distance   = 100
        self.switch             = Debouncer(lambda: self.current_distance < self.cutoff_distance)
        self.track              = track
        self.track_duration     = duration
        
    def checkDistance(self):
        now = time.monotonic()
        if now - self.last_read_time > 0.05:  # Limit how frequently distance is checked
            try:
                self.current_distance = self.sonar.distance
                self.switch.update()
                self.last_read_time = now
            except:
                print(self.name, "update failed")



### --- Properties of push buttons ---
# When a button is pressed, the subsection of pixels
# corresponding to that button will light up in the
# specified color. Set all the properties of the buttons
# here
PIN_BUTTON_A    = board.GP1
RANGE_A         = range(0,7)        # Subsection of pixels corresponding to this button
COLOR_A         = (255, 0, 119)     # Color to light the pixel section when button is pressed

PIN_BUTTON_B    = board.GP5
RANGE_B         = range(7,num_pixels)
COLOR_B         = (128,0,175)

# Create the button objects in a list. Add more buttons by adding them
# to this list
buttons = [ ButtonObject("Button A", PIN_BUTTON_A, pixels, RANGE_A, COLOR_A),
           ButtonObject("Button B", PIN_BUTTON_B, pixels, RANGE_B, COLOR_B)
           ]
### --- End push buttons ---


### --- Properties of sonar sensors  ---
# When a sonar sensor is triggered, a song will begin playing.
# specify the pins controling the sonar sensor, and the song
# track it should play here
ECHO_PIN_1          = board.GP17
TRIGGER_PIN_1       = board.GP14
SONAR_DISTANCE_1    = 20                # Distance at which to trigger the sonar
TRACK_1             = 1                 # Track to play when the sonar is triggered
DURATION_TRACK_1    = 5                 # Duration of the track in seconds

ECHO_PIN_2          = board.GP12
TRIGGER_PIN_2       = board.GP13
SONAR_DISTANCE_2    = 20
TRACK_2             = 2
DURATION_TRACK_2    = 5

# Create sonar objects by adding them to this list. Add additional sonar sensors by adding them to the list
sonars  = [SonarObject("Sonar 1", TRIGGER_PIN_1, ECHO_PIN_1, SONAR_DISTANCE_1, player, TRACK_1, DURATION_TRACK_1),
           SonarObject("Sonar 2", TRIGGER_PIN_2, ECHO_PIN_2, SONAR_DISTANCE_2, player, TRACK_2, DURATION_TRACK_2)
          ]
### --- End sonar sensors ---


# Global variables to keep track of whether a song is playing
is_playing = False
current_sonar = None
track_end_time = 0


# Main loop. You should not have to alter code in this loop to add new
# buttons or new ping sensors. Change the properties of existing
# sensors or buttons in the variables above.
while True:
    now = time.monotonic()

    # Update each button's debouncer
    # When triggered, each button fills a specified pixel
    # range in a different color
    for b in buttons:
        b.switch.update()                   # Update button debouncer
        if b.switch.fell:
            pixels.fill((0,0,0))            # Set all pixels to black
            for i in b.pixrange:            # Set pixel range to specific color
                pixels[i] = b.color
            pixels.show()

    # Update the values of all sonar objects, and the debouncer for each
    # will track when the measured distance is smaller than the cutoff_distance        
    for s in sonars:
        s.checkDistance()
        if s.switch.rose:
            print(s.name, "rose", s.current_distance)
            player.selectByNumber(s.track)
            player.play()
            is_playing = True
            track_end_time = now + s.track_duration
            current_sonar = s
        elif s.switch.fell:
            print(s.name, "fell", s.current_distance)
                

    # If the sound is playing, and an object is still within
    # range of the ping sensor, then extend the time that the
    # track will stop
    if is_playing:
        if current_sonar.switch.value:                  
            track_end_time = now + s.track_duration
        elif now > track_end_time:          # Ping sensor does not detect object
            print("stopping track")         # and play time for song has run out
            player.stop()
            is_playing = False
            current_sonar = None

    # Add small delay to make it easier to break into the loop with CTRL-c
    time.sleep(0.05)


