from action_object import Action

from dyplayer import DYPlayer

# An action class to play a sequence of tracks in a row.
# player is the sound player object
# track_list is a list of tracks to play in the order specified, e.g. [3,2,4] will
# play tracks 3, 2, and 4 in order
# duration_list is a list containing number of seconds to play each track for, e.g. [4.5, 3, 6]
class ActionSoundSequence(Action):
    def __init__(self, player, track_list, duration_list):


        if type(track_list) is not list:
            raise TypeError("parameter track_list must be a list with length > 1")
        if len(track_list) < 2:
            raise ValueError("ActionSoundSequence requires two or more tracks")


        if type(duration_list) is not list:
            raise TypeError("parameter duration list must be a list with length > 1")
        if len(duration_list) != len(track_list):
            raise ValueError("must specify exactly one duration for each track")

        self.player             = player
        self.tracks             = track_list        # List of track numbers to play sequentially in the order specified
        self.durations          = duration_list     # Length of time (seconds) to play each track. Must have the same
                                                # number of elements as the track_list
        self.track_index        = 0
        self.current_track_stop = self.durations[0]


        super().__init__(name="Tracks_" + "_".join(str(t) for t in track_list))

    def on_start(self):
        #print("starting track ", self.tracks[self.track_index])
        self.player.playByNumber(self.tracks[self.track_index])  #Current track will be zero

    def on_stop(self):
        self.track_index        = 0
        self.current_track_stop = self.durations[0]
        #print("stopping ", self.name, " at duration ", self.active_duration())
        self.player.stop()

    # Stop the player if the duration is specified and the song has played
    # for longer than the specified duration
    def action(self):
        if self.active_duration() > self.current_track_stop:  #Time to stop the current track
            self.track_index = self.track_index + 1
            if self.track_index >= len(self.tracks):        #We have played all tracks
                self.stop_action()
                return False
            else:
                self.player.stop()
                #print("stopping track ", self.tracks[self.track_index - 1], " at duration ", self.active_duration())
                self.player.playByNumber(self.tracks[self.track_index])
                #print("starting track ", self.tracks[self.track_index])
                self.current_track_stop = self.current_track_stop + self.durations[self.track_index]
        return True

    def get_duration(self):
        return sum(self.durations)
