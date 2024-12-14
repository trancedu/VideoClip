import vlc
import sys

class VideoPlayer:
    def __init__(self):
        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()
        self.video_path = ""

    def load_video(self, video_path):
        self.video_path = video_path
        self.player.set_media(self.instance.media_new(self.video_path))

    def pause(self):
        self.player.pause()

    def play(self):
        self.player.play()

    def toggle_play_pause(self):
        if self.is_playing():
            self.pause()
        else:
            self.play()

    def is_playing(self):
        return self.player.is_playing()

    def fast_forward(self, second=3):
        self.set_position(self.get_position() + second)

    def fast_backward(self, second=3):
        self.set_position(self.get_position() - second)

    def set_speed(self, speed):
        pass 

    def get_position(self):
        return self.player.get_position()

    def set_position(self, position):
        self.player.set_position(position)

    def set_output_widget(self, widget):
        if sys.platform == "win32":
            self.player.set_hwnd(widget.winId())
        elif sys.platform == "darwin":
            self.player.set_nsobject(int(widget.winId()))
        elif sys.platform.startswith('linux'):
            self.player.set_xwindow(widget.winId())
