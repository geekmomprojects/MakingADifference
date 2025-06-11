from action_object import Action
import digitalio


# A simple action class for an LED that turns on for the duration of the action
class ActionLED(Action):
    def __init__(self, ledPin):
        self.led = digitalio.DigitalInOut(ledPin)
		self.led.direction = digitalio.Direction.OUTPUT
		self.led.value = False
        super().__init__(name="LEDPin" + str(ledPin.__hash__))
		
	# Turn the LED on when action starts
    def on_start(self):
		self.led.value = True


	# Turn the LED off when action stops
    def on_stop(self):
        self.led.value = False
		
	# No action needed - LED turns on/off with on_start, on_stop functions
	# but still must override this function for the class to work
	def action(self):
		return True