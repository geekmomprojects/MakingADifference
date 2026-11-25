from trigger_object import TriggerObject

import time
import adafruit_hcsr04
from adafruit_debouncer import Debouncer


# Trigger object is an ultrasonic distance ("ping") sensor, like the HC-SR04.
# Triggers when something comes closer than cutoff_distance (in cm).
class PingTrigger(TriggerObject):
    NO_READINGS_WARNING_SECONDS = 5     # Print a message if there are no readings for this long

    def __init__(self, name, trigger_pin, echo_pin, cutoff_distance, action_groups, random_actions=False, allow_restart=True):
        self.name               = name
        self.sonar              = adafruit_hcsr04.HCSR04(trigger_pin=trigger_pin,echo_pin=echo_pin)
        self.last_read_time     = 0
        self.last_good_read_time  = time.monotonic()
        self.reported_no_readings = False
        self.last_trigger_time  = 0
        self.cutoff_distance    = cutoff_distance
        self.current_distance   = 100
        self.switch             = Debouncer(lambda: self.current_distance < self.cutoff_distance, interval=0.1)
        super().__init__(name, action_groups, random_actions=random_actions, allow_restart=allow_restart)

    def update(self):
        self.checkDistance()

    def is_triggered (self):
        response = False
        now = time.monotonic()
        if now - self.last_trigger_time > 0.3:
            response = self.switch.rose
        if response:
            self.last_trigger_time = now
        return response

    def checkDistance(self):
        now = time.monotonic()
        if now - self.last_read_time < 0.05:    # Limit how frequently distance is checked
            return
        self.last_read_time = now               # (also after a failed reading, so a failing sensor isn't re-read every loop)

        try:
            self.current_distance = self.sonar.distance
        except RuntimeError:
            # The sensor didn't hear an echo. That's normal now and then (for example
            # when nothing is in range), so only report it if it keeps happening.
            if not self.reported_no_readings and now - self.last_good_read_time > PingTrigger.NO_READINGS_WARNING_SECONDS:
                print(self.name, "has had no distance readings for", PingTrigger.NO_READINGS_WARNING_SECONDS,
                      "seconds. Nothing may be in range, or check the wiring.")
                self.reported_no_readings = True
            return

        self.last_good_read_time = now
        if self.reported_no_readings:
            print(self.name, "distance readings are working again")
            self.reported_no_readings = False
        self.switch.update()
