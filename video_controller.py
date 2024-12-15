from ui import MainWindow
from config_manager import ConfigManager
from clip_manager import ClipManager
from video_player import VideoPlayer
from PyQt5.QtCore import QObject, pyqtSlot

class VideoController(QObject):
    def __init__(self, video_player: VideoPlayer, clip_manager: ClipManager):
        super().__init__()
        self.video_player = video_player
        self.clip_manager = clip_manager

    @pyqtSlot()
    def toggle_play_pause(self):
        """Toggle play/pause."""
        self.video_player.toggle_play_pause()

    @pyqtSlot(str)
    def load_video(self, video_path):
        """Load a new video."""
        self.video_player.load_video(video_path)

    @pyqtSlot(int)
    def set_time(self, time_ms):
        """Set the playback time."""
        self.video_player.set_time(time_ms)

    @pyqtSlot()
    def fast_forward(self):
        """Fast forward the video."""
        self.video_player.fast_forward(3)

    @pyqtSlot()
    def fast_backward(self):
        """Rewind the video."""
        self.video_player.fast_backward(3)