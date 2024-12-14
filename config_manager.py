import platform
import os

class ConfigManager:
    def __init__(self, video_path, clip_path, video_base_path):
        self.set_video_path(video_path)
        self.set_clip_path(clip_path)
        self.set_video_base_path(video_base_path)
    
    def get_video_path(self):
        return self.video_path
    
    def set_video_path(self, path):
        home_path = os.path.expanduser("~")
        self.video_path = os.path.join(home_path, path)
    
    def get_clip_path(self):
        return self.clip_path
    
    def set_clip_path(self, path):
        home_path = os.path.expanduser("~")
        self.clip_path = os.path.join(home_path, path)
    
    def get_video_base_path(self):
        return self.video_base_path
    
    def set_video_base_path(self, path):
        self.video_base_path = path
