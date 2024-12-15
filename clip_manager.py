import os
import json

class ClipManager:
    def __init__(self, clip_directory: str, base_video_dir: str):
        self.clip_directory = clip_directory
        self.video_paths = self.scan_for_videos(base_video_dir)
        self.video_clips = self.populate_video_clips(clip_directory)

    def get_clip_for_video(self, video_path):
        return self.video_clips.get(video_path, [])

    def scan_for_videos(self, base_video_dir):
        """Scan the base directory and subdirectories for .mp4 files."""
        video_paths = {}
        
        for root, _, files in os.walk(base_video_dir):
            for file in files:
                if file.endswith('.mp4'):
                    video_name = file
                    video_path = os.path.join(root, file)
                    video_paths[video_name] = video_path
        return video_paths

    def get_video_path(self, video_name):
        return self.video_paths.get(video_name)

    def populate_video_clips(self, clip_directory):
        video_clips = {}
        # Get all JSON files in the config directory and sort them by name
        json_files = sorted([f for f in os.listdir(clip_directory) if f.endswith('.json')])
        # Iterate over sorted JSON files
        for file_name in json_files:
            video_name = file_name[:-5]  # Remove the '.json' extension

            # Use the video_paths dictionary to find the video path
            video_path = self.get_video_path(video_name)

            # Check if the video file exists
            if not video_path:
                continue  # Skip this config file if the video file does not exist

            file_path = os.path.join(clip_directory, file_name)

            with open(file_path, 'r') as f:
                clips = json.load(f)

            video_clips[video_name] = clips
        return video_clips

    def add_clip_to_video(self, video_path, clip):
        self.video_clips[video_path].append(clip)

    def remove_clip_from_video(self, video_path, clip):
        self.video_clips[video_path].remove(clip)

    def save_video_clips(self, video_path):
        with open(os.path.join(self.clip_directory, f"{video_path}.json"), 'w') as f:
            json.dump(self.video_clips[video_path], f)

    def save_all_video_clips(self):
        for video_path in self.video_clips:
            self.save_video_clips(video_path)