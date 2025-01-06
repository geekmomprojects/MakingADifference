from action_object import Action

import math
from adafruit_motor import servo


# An action class that controls a servo. Can specify the start/end angle and the period
# for one complete back and forth motion
class ActionServo(Action):
    def __init__(self, name, servo_obj, start_angle=20, end_angle=160, period=3):
        self.servo_obj = servo_obj
        self.start_angle = start_angle
        self.end_angle = end_angle
        self.period = period
        self.sevo_pos = start_angle
        super().__init__(name=name)

    def action(self):
        if not self.is_active() or self.time_since_last_action() < 0.05:  #Don't update TOO frequently
            return False

        # Create periodic motion of the servo over the angle range with a bit of trig
        period_frac = (math.sin(6.28*self.active_duration()/self.period) + 1)/2
        self.servo_pos = self.start_angle + (self.end_angle - self.start_angle)*period_frac
        self.servo_obj.angle = self.servo_pos
        return True
