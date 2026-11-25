# Tests an ultrasonic distance ("ping") sensor such as the HC-SR04, on its own.
#
# Wiring:
#   Sensor VCC  -> power (see the note about 3.3V in the README)
#   Sensor GND  -> Pico GND
#   Sensor Trig -> TRIG_PIN below
#   Sensor Echo -> ECHO_PIN below
#
# Note: board.GP4 means the pin labelled GP4, not the 4th physical pin.
# (Physical pins 4 and 5 are GP2 and GP3.)
#
# What you should see, about 5 times a second:
#   distance: 23.4 cm
# Move your hand in front of the sensor and the number should change. When the
# distance is less than TRIGGER_DISTANCE, the message says so and the Pico's
# built-in LED lights up. That's when a PingTrigger with the same distance
# would trigger.
#
# If you only see "no echo", the sensor isn't hearing anything back. Check:
#   - Trig and Echo aren't swapped (in this file and in the wiring)
#   - the sensor has power and GND
#   - nothing is too close (under ~2 cm) or too far away (over ~4 m)

import time
import board
import digitalio
import adafruit_hcsr04

TRIG_PIN         = board.GP4
ECHO_PIN         = board.GP5
TRIGGER_DISTANCE = 8            # cm - same as the cutoff_distance you give PingTrigger

sonar = adafruit_hcsr04.HCSR04(trigger_pin=TRIG_PIN, echo_pin=ECHO_PIN)

led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT

print("Testing ping sensor: Trig on", TRIG_PIN, " Echo on", ECHO_PIN)

while True:
    try:
        distance = sonar.distance
        if distance < TRIGGER_DISTANCE:
            print("distance:", round(distance, 1), "cm   <-- closer than", TRIGGER_DISTANCE, "cm, would trigger")
            led.value = True
        else:
            print("distance:", round(distance, 1), "cm")
            led.value = False
    except RuntimeError:
        print("no echo")
        led.value = False
    time.sleep(0.2)
