# The main loop for a toy.
#
# A Toy watches a list of triggers (buttons, sensors...). When one is activated,
# it plays that trigger's actions (sounds, lights, motors...). Only one trigger
# plays at a time: activating a new trigger stops the one that was playing.
#
# Most toys just need:
#
#     toy = Toy([button_a, button_b, ping_1])
#     toy.run()
#
# To add your own code to the main loop, call update() yourself instead of run():
#
#     while True:
#         toy.update()
#         # ... your own code here ...

from trigger_object import TriggerObject


class Toy:
    def __init__(self, triggers):
        self.triggers        = list(triggers)
        self.current_trigger = None     # The trigger whose actions are playing (None if nothing is playing)

    # Run the main loop forever
    def run(self):
        while True:
            self.update()

    # One pass through the main loop. Call this over and over.
    def update(self):
        # 1. Keep the current trigger's actions playing, and notice when they finish
        if self.current_trigger is not None:
            if not self.current_trigger.play():
                finished_trigger = self.current_trigger
                self.current_trigger = None
                self.on_finished(finished_trigger)

        # 2. Read all the triggers (buttons, sensors...)
        for trigger in self.triggers:
            trigger.update()

        # 3. Respond to the first trigger that was activated
        for trigger in self.triggers:
            if trigger.is_triggered():
                print("")
                print(trigger.name, "was triggered.")
                self.on_triggered(trigger)
                break

    # Called when a trigger is activated. Child classes (like InstructionGame)
    # override this to make the toy behave differently.
    def on_triggered(self, trigger):
        if self.current_trigger is not None and trigger is not self.current_trigger:
            self.current_trigger.stop()         # A different trigger was playing, so stop it
        trigger.respond_to_trigger()
        if trigger.is_active():
            self.current_trigger = trigger
        else:
            self.current_trigger = None

    # Called when a trigger's actions finish playing on their own
    def on_finished(self, trigger):
        trigger.stop()                          # Stopping the trigger moves it on to its next action group

    # Start a trigger's actions, stopping whatever was playing before.
    # The stopped trigger does NOT move on to its next action group.
    def start_trigger(self, trigger):
        if self.current_trigger is not None:
            self.current_trigger.stop(set_next_action=False)
        trigger.start()
        self.current_trigger = trigger


# A game where one trigger (the "instruction trigger") tells the user which
# trigger to activate next. For example, Button A plays "Press the red button".
#
# Each of the instruction trigger's action groups names its target trigger:
#
#     ACTIONS_A[0].set_data("target", button_red)
#
# How the game plays:
#   - The user activates the instruction trigger to hear an instruction.
#   - Activating the right target plays that target's actions. The next time,
#     the instruction trigger gives the next instruction.
#   - Activating the wrong trigger plays wrong_answer_group if you gave one,
#     otherwise it repeats the instruction.
#   - Activating the instruction trigger again repeats the same instruction.
#   - Activating a trigger while its own actions are playing does nothing.
class InstructionGame(Toy):
    def __init__(self, instruction_trigger, triggers, wrong_answer_group=None):
        all_triggers = list(triggers)
        if instruction_trigger not in all_triggers:
            all_triggers.insert(0, instruction_trigger)
        super().__init__(all_triggers)

        self.instruction_trigger = instruction_trigger
        self.expected_trigger    = instruction_trigger      # The trigger the user should activate next

        # The wrong answer response is wrapped in a trigger so the game can
        # play it the same way as everything else. It is never activated directly.
        self.wrong_answer_trigger = None
        if wrong_answer_group is not None:
            self.wrong_answer_trigger = TriggerObject("Wrong answer", [wrong_answer_group])

        # If the instructions are chosen randomly, choose the first one randomly too
        if instruction_trigger.random_actions:
            instruction_trigger.set_random_group()

    def on_triggered(self, trigger):
        if trigger is self.current_trigger:
            print("still playing - ignoring", trigger.name)

        elif trigger is self.expected_trigger and trigger is self.instruction_trigger:
            # Give the instruction, and remember which trigger it asks for
            self.start_trigger(trigger)
            target = trigger.get_current_group_data("target")
            if target is not None:
                self.expected_trigger = target
                print("waiting for", target.name)

        elif trigger is self.expected_trigger:
            print("the correct trigger was chosen.")
            self.start_trigger(trigger)
            self.expected_trigger = self.instruction_trigger
            self.instruction_trigger.advance()          # Next time, give the next instruction

        elif self.expected_trigger is self.instruction_trigger:
            print("no instruction yet - activate", self.instruction_trigger.name, "first")

        else:
            print("expected", self.expected_trigger.name, "but", trigger.name, "was activated")
            if trigger is self.instruction_trigger or self.wrong_answer_trigger is None:
                self.start_trigger(self.instruction_trigger)    # Repeat the instruction
            else:
                self.start_trigger(self.wrong_answer_trigger)

    def on_finished(self, trigger):
        # The instruction trigger only moves on to its next instruction after a
        # correct answer, so don't let it advance here.
        trigger.stop(set_next_action=(trigger is not self.instruction_trigger))
