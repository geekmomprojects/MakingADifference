# MakingADifference

CircuitPython code for interactive toys built on a Raspberry Pi Pico.

When someone presses a button or waves a hand in front of a sensor, the toy
responds. It might play a sound, light up LEDs, or move a motor, or do several
of these at once.

## How it works

A toy is made of three kinds of objects:

```
Trigger            →   ActionGroup                →   Action
(something the         (actions that play together    (one thing a peripheral does:
 user activates:        for a set number of seconds)   play a track, run an LED
 button, sensor...)                                    animation, move a servo...)
```

- An **Action** is one thing a peripheral does, like "play track 3" or "run a
  rainbow animation".
- An **ActionGroup** is a set of actions that start together, play for a set
  number of seconds, then stop together.
- A **Trigger** is a button, switch or sensor. It has a list of action groups.
  Each time it is activated, it plays the next group in its list, or a random
  group if `random_actions=True`.
- A **Toy** watches all the triggers and plays the right action group when one
  is activated. Only one trigger plays at a time.

## A first toy

This toy plays track 1 and runs a rainbow animation for 5 seconds when the
button is pressed:

```python
import board
import busio
import neopixel
from adafruit_led_animation.animation.rainbow import Rainbow

from dyplayer import DYPlayer
from action_object.action_sound import ActionSound
from action_object.action_animation import ActionAnimation
from action_object.action_group import ActionGroup
from trigger_object.button_trigger import ButtonTrigger
from toy import Toy

# Set up the hardware
player = DYPlayer(uart=busio.UART(board.GP8, board.GP9, baudrate=9600))
pixels = neopixel.NeoPixel(board.GP27, 9, brightness=0.2, auto_write=False)

# Create the actions
song    = ActionSound(player, 1)
rainbow = ActionAnimation(Rainbow(pixels, speed=0.1))

# Create a trigger with one action group: play both actions for 5 seconds
button = ButtonTrigger("Button", board.GP16, [ActionGroup(5, song, rainbow)])

# Run the toy
toy = Toy([button])
toy.run()
```

## Getting started

1. **Install CircuitPython on the Pico.** Download it from
   [circuitpython.org/board/raspberry_pi_pico](https://circuitpython.org/board/raspberry_pi_pico/).
   Hold the BOOTSEL button while plugging the Pico in, then drag the `.uf2`
   file onto the `RPI-RP2` drive. The Pico restarts as a drive called
   **CIRCUITPY**.
2. **Copy this library to the Pico.** Copy everything in this repository's
   `lib` folder into the `lib` folder on CIRCUITPY.
3. **Copy the Adafruit libraries to the Pico.** Download the Adafruit library
   bundle that matches your CircuitPython version from
   [circuitpython.org/libraries](https://circuitpython.org/libraries). Copy these
   from the bundle's `lib` folder into CIRCUITPY's `lib` folder:

   | Library | Needed for |
   |---|---|
   | `adafruit_debouncer.mpy` and `adafruit_ticks.mpy` | buttons, switches, sensors |
   | `adafruit_hcsr04.mpy` | ping (distance) sensor |
   | `adafruit_motor` (folder) | servos |
   | `neopixel.mpy` | LED strips |
   | `adafruit_led_animation` (folder) | LED animations |

   If the Pico reports `ImportError: no module named ...`, find that name in
   the bundle and copy it too.
4. **Run an example.** Copy an example from `examples/toys` to CIRCUITPY and
   rename it `code.py`. The Pico runs `code.py` every time it starts, and again
   whenever a file on CIRCUITPY is saved.
5. **Watch the output.** Messages from `print()` and any error messages appear
   on the Pico's serial connection. You can see them in
   [Mu](https://codewith.mu/) or [Thonny](https://thonny.org/) (Serial / Shell
   button), or with the **Serial Monitor** extension in VS Code.

## What's in the library

### Triggers (`lib/trigger_object`)

Every trigger takes a name and a list of action groups. Two options are shared
by all triggers:

- `random_actions`: `True` plays a random group each time. `False` (the
  default) plays the groups in order.
- `allow_restart`: what happens if the trigger is activated while its actions
  are still playing. `True` stops them and starts the next group. `False`
  just stops them.

| Trigger | Create it with | Activates when |
|---|---|---|
| Push button | `ButtonTrigger(name, pin, action_groups)` | the button is pressed |
| Toggle switch | `ToggleTrigger(name, pin, action_groups, toggle_both=True)` | the switch is flipped (`toggle_both=False`: only one way) |
| IR sensor | `IrTrigger(name, pin, action_groups)` | the sensor's output goes low |
| Ping (distance) sensor | `PingTrigger(name, trigger_pin, echo_pin, cutoff_distance, action_groups)` | something comes closer than `cutoff_distance` (cm) |

### Actions (`lib/action_object`)

| Action | Create it with | What it does |
|---|---|---|
| Sound | `ActionSound(player, track_num)` | plays one track on the MP3 player |
| Sound sequence | `ActionSoundSequence(player, [tracks], [seconds])` | plays several tracks in a row, each for the number of seconds given |
| LED animation | `ActionAnimation(animation)` | runs an Adafruit LED animation, then turns the LEDs off |
| Servo | `ActionServo(name, servo, start_angle=20, end_angle=160, period=3)` | swings a servo back and forth; `period` is the seconds for one full swing |
| Single LED | `ActionLED(pin)` | turns an LED on while the action plays |

### Action groups (`lib/action_object/action_group.py`)

`ActionGroup(seconds, action1, action2, ...)` plays the actions together for
that many seconds. Use `ActionGroup.INFINITE` instead of a number to play until
the trigger is activated again or another trigger interrupts.

### Running the toy (`lib/toy.py`)

- `Toy(triggers)`: the standard toy. Call `toy.run()` to start it.
- `InstructionGame(instruction_trigger, triggers, wrong_answer_group=None)`: a
  game. The instruction trigger tells the user which trigger to activate (e.g.
  "Press the red button"). Each of the instruction trigger's action groups
  names its target with `group.set_data("target", trigger)`. A wrong answer
  plays `wrong_answer_group`, or repeats the instruction if there isn't one. See
  `examples/toys/simple_options_example.py`.

To add your own code to the main loop, call `toy.update()` in your own loop
instead of `toy.run()`:

```python
while True:
    toy.update()
    # ... your own code here ...
```

`examples/toys/custom_loop_example.py` shows the whole main loop written out
step by step.

### Creating the hardware: pins or objects?

- **Hardware that only one object uses** (a button, switch, IR sensor, ping
  sensor, single LED): pass the **pin**, like `board.GP16`. The trigger or
  action sets up the pin itself.
- **Hardware that several objects can share** (the MP3 player, an LED strip, a
  servo): **create the object yourself** and pass it in. That way, several
  actions can use the same device. For example, two `ActionServo` motions can
  share one servo, and several animations can share one LED strip.

## Wiring used by the examples

| Peripheral | Pico pin(s) | Notes |
|---|---|---|
| Button A | GP16 | Button between the pin and GND. No resistor needed (the Pico's internal pull-up is used). |
| Button B | GP17 | as above |
| Button / toggle switch C | GP18 | as above |
| IR sensor / 4th button | GP19 | |
| Ping sensor (HC-SR04) | GP14 = trigger, GP15 = echo | The Pico's pins are 3.3V. Use a 3.3V-compatible sensor (e.g. HC-SR04P), or a voltage divider on the echo pin. |
| Servo | GP12 | Power the servo from 5V (VBUS), not 3.3V |
| NeoPixel (WS2812) strip | GP27 (GP20 in `options_correct_incorrect_example.py`) | |
| MP3 player (DY-SV5W) | GP8 → player RX, GP9 ← player TX | Set the player's DIP switches to 1 = low, 2 = low, 3 = high |

The MP3 player's track numbers follow the order the files were saved to its SD
card. Naming the files `00001.mp3`, `00002.mp3`, … and copying them to the card
in that order keeps the numbers matched.

## Folder layout

| Folder | What's in it |
|---|---|
| `lib/` | The library. Copy it to the Pico. |
| `examples/toys/` | Complete toys that combine several triggers and actions |
| `examples/peripherals/` | Short examples that each use one peripheral on its own |
| `tests/hardware/` | Scripts that check a toy's wiring and peripherals |
| `tools/` | Scripts you run on your computer, not on the Pico |

## Making your own kinds of actions and triggers

**A new action:** create a child class of `Action` and fill in these methods:

```python
from action_object import Action

class ActionMyThing(Action):
    def on_start(self):      # called once when the action starts (optional)
        ...
    def on_update(self):     # called over and over while it plays (required)
        return True          # return True if it did something
    def on_stop(self):       # called once when the action stops (optional)
        ...
```

**A new trigger:** create a child class of `TriggerObject` and fill in
`update()`, which reads the sensor every time through the loop, and
`is_triggered()`, which returns `True` when the trigger was just activated.
`lib/trigger_object/button_trigger.py` is a short example to copy.

## Updating toys written for version 1

Version 2 renamed some methods (for example, `start_action()` is now
`start()`, and `set_current_action()` is now `set_current_group()`). Old toy
code still works with version 2, but it prints a `NOTE:` for each old name it
uses. To update a toy's code, run this on your computer:

```
python tools/update_to_v2.py --dry-run code.py    # see what would change
python tools/update_to_v2.py code.py              # change it (keeps a code.py.v1.bak copy)
```

Version 1 of the library is still available from the `v1.0` tag on GitHub.
