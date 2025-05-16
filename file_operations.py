import os
from PyQt6.QtWidgets import QFileDialog
from clip_manager import load_clips_from_file


def load_video(self, video_path=None):
    """Load a video file."""
    if video_path and os.path.exists(video_path):
        self.video_path = video_path
    else:
        options = QFileDialog.Options()
        self.video_path, _ = QFileDialog.getOpenFileName(
            self, "Open Video File", "", "Video Files (*.mp4 *.avi)")

    if self.video_path and os.path.exists(self.video_path):
        # Create VLC media and set it to the player
        media = self.instance.media_new(self.video_path)
        self.media_player.set_media(media)

        # Update the paths for loading and saving clips
        update_clip_paths(self)

        self.play_button.setEnabled(True)
        self.pause_button.setEnabled(True)
        self.forward_button.setEnabled(True)
        self.backward_button.setEnabled(True)
        self.clip_button.setEnabled(True)
        self.save_clip_button.setEnabled(True)
        self.feedback_label.setText(f"Loaded video: {os.path.basename(self.video_path)}")

        # Load saved clip positions
        load_clips_from_file(self)

        # Automatically play the video after loading
        from playback_control import play_video
        play_video(self)

        # Set focus to the main window to prevent spacebar from triggering the button again
        self.setFocus()
    else:
        self.feedback_label.setText("Video file not found.")


def update_clip_paths(self):
    """Update the paths for loading and saving clips."""
    os.makedirs(self.config_dir, exist_ok=True)
    self.config_file = os.path.join(self.config_dir, f"{os.path.basename(self.video_path)}.json")


def scan_for_videos(self, base_dir):
    """Scan the base directory and subdirectories for .mp4 files."""
    video_paths = {}
    if not base_dir:
        return video_paths
        
    for root, _, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.mp4'):
                video_name = file
                video_path = os.path.join(root, file)
                video_paths[video_name] = video_path
    return video_paths 