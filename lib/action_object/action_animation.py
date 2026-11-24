from action_object import Action

# An action class for an LED animation
class ActionAnimation(Action):
    def __init__(self, animation):
        self.animation = animation
        super().__init__(name=animation.__class__.__name__)

    def on_update(self):
        return self.animation.animate()

    # When animation is stopped, set pixels to black and reset animation
    def on_stop(self):
        self.animation.reset()
        self.animation.pixel_object.fill((0,0,0))
        self.animation.pixel_object.show()
