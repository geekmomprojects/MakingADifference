from action_object import Action

from dyplayer import DYPlayer

# An action class to play a track. Takes a DYPlayer object and track number
class ActionSound(Action):
    def __init__(self, player, track_num, track_duration=-1):
        self.player         = player
        self.track_num      = track_num
        self.track_duration = track_duration    # Length of time (seconds) to play track
        super().__init__(name="Track " + str(track_num))

    def on_start(self):
        self.player.playByNumber(self.track_num)

    def on_stop(self):
        self.player.stop()

    # Stop the player if the duration is specified and the song has played
    # for longer than the specified duration
    def action(self):
        if self.track_duration >= 0 and self.active_duration() > self.track_duration:
            self.stop_action()
            return False
        else:
            return True
