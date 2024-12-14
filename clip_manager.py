

class ClipManager:
    def __init__(self):
        self.clip_path = ""
        self.video_clips = {}
    
    def get_clip_path(self):
        return self.clip_path
    
    def set_clip_path(self, path):
        self.clip_path = path

    def get_clip_for_video(self, video_path):
        pass

    def populate_video_clips(self):
        pass

    def add_clip_to_video(self, video_path, clip):
        pass

    def remove_clip_from_video(self, video_path, clip):
        pass

    def save_video_clips(self):
        pass
