from action_object import Action

from adafruit_led_animation.animation import Animation

# An action class for an LED animation
class ActionAnimation(Action):
    def __init__(self, animation):
        self.animation = animation
        super().__init__(name=animation.__class__.__name__)
		
	# Converts an animation into an object	
	# object of the correct type
	@staticmethod
	def create_action(*args):
		if len(args) == 1 and isinstance(args[0], Animation):
			return ActionAnimation(args[0])
		else:
			return None

    def action(self):
        return self.animation.animate()

    # When animation is stopped, set pixels to black and reset animation
    def on_stop(self):
        self.animation.reset()
        self.animation.pixel_object.fill((0,0,0))
        self.animation.pixel_object.show()
