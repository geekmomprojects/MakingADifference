# Hardware tests

Scripts that check whether a toy's peripherals are wired correctly and working.
For example, one might print a message every time a button is pressed, or play
each track on the MP3 player in turn.

To run one, copy it to the Pico's CIRCUITPY drive and rename it `code.py`, then
watch its messages in the serial monitor.

When adding a test here:

- Name it after what it checks, like `test_buttons.py`.
- At the top, list the pins it uses, and say what you should see or hear if
  the hardware works.
- Print clear messages, like `Button A (GP16) pressed`, so a problem is easy
  to spot.
