import vlc
import sys

class VideoPlayer:
    def __init__(self):
        self.instance = vlc.Instance()
        self.player: vlc.MediaPlayer = self.instance.media_player_new()
        self.video_path = ""
        self.current_clip_end = None

    def load_video(self, video_path):
        self.video_path = video_path
        self.player.set_media(self.instance.media_new(self.video_path))

    def pause(self):
        self.player.pause()

    def play(self, start=None):
        if start is not None:
            self.set_time(start)
        self.player.play()

    def toggle_play_pause(self):
        if self.is_playing():
            self.pause()
        else:
            self.play()

    def is_playing(self):
        return self.player.is_playing()

    def fast_forward(self, seconds=3):
        self.set_time(self.get_time() + seconds * 1000)

    def fast_backward(self, seconds=3):
        self.set_time(self.get_time() - seconds * 1000)

    def set_speed(self, speed):
        pass 

    def get_time(self):
        return self.player.get_time()

    def set_time(self, time):
        self.player.set_time(time)

    def set_output_widget(self, widget):
        if sys.platform == "win32":
            self.player.set_hwnd(widget.winId())
        elif sys.platform == "darwin":
            self.player.set_nsobject(int(widget.winId()))
        elif sys.platform.startswith('linux'):
            self.player.set_xwindow(widget.winId())

    def get_length(self):
        return self.player.get_length()

    def get_time(self):
        return self.player.get_time()
    
    def get_video_path(self):
        return self.video_path
    
    def set_video_path(self, video_path):
        self.video_path = video_path
