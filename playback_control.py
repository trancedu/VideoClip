from utils import format_time

def toggle_play_pause(self):
    """Toggle between play and pause states."""
    if self.is_playing:
        pause_video(self)
    else:
        play_video(self)


def update_position(self):
    """Update the position slider and duration label."""
    current_time = self.media_player.get_time()
    total_time = self.media_player.get_length()
    if total_time > 0:
        self.position_slider.setRange(0, total_time)
        self.position_slider.setValue(current_time)
        current_time_str = format_time(current_time)
        total_time_str = format_time(total_time)
        self.duration_label.setText(f"{current_time_str} / {total_time_str}")
    else:
        self.position_slider.setValue(0)
        self.duration_label.setText("0:00 / 0:00")


def set_position(self, position):
    """Set the media player position."""
    self.media_player.set_time(int(position))


def play_video(self):
    """Play the current video."""
    if self.video_path:
        try:
            if not self.media_player.get_media():
                media = self.instance.media_new(self.video_path)
                self.media_player.set_media(media)
            self.media_player.play()
            self.is_playing = True
            self.timer.start()
            self.feedback_label.setText("Playing video")
        except Exception as e:
            self.feedback_label.setText(f"Error playing video: {e}")


def pause_video(self):
    """Pause the current video."""
    if self.is_playing:
        self.media_player.pause()
        self.is_playing = False
        self.feedback_label.setText("Video paused")


def skip(self, seconds):
    """Skip forward or backward by the specified number of seconds."""
    if self.media_player.get_length() > 0:
        current_time = self.media_player.get_time()
        new_time = current_time + seconds * 1000  # milliseconds
        new_time = max(0, min(new_time, self.media_player.get_length()))
        self.media_player.set_time(int(new_time))
        direction = "forward" if seconds > 0 else "backward"
        self.feedback_label.setText(f"Skipped {direction} {abs(seconds)} seconds")


def return_to_main_video(self):
    """Return to the main video from a clip."""
    if self.video_path:
        # Ensure media is loaded
        if not self.media_player.get_media():
            media = self.instance.media_new(self.video_path)
            self.media_player.set_media(media)
        self.media_player.set_time(self.main_video_position)  # Resume from last position
        self.media_player.play()
        self.is_playing = True
        self.return_button.setEnabled(False)
        self.position_saved = False  # Reset the flag
        self.feedback_label.setText("Returned to main video")


def slider_clicked(self):
    """Handle slider click events."""
    # Reset the current clip end when the slider is clicked
    self.current_clip_end = None

    # Calculate the position based on the click
    value = self.position_slider.value()
    set_position(self, value)

    # If the video is paused, start playing from the new position
    if not self.is_playing:
        play_video(self)


def play_clip(self, start, end):
    """Play the video from start to end time."""
    if self.video_path:
        # Ensure media is loaded
        if not self.media_player.get_media():
            media = self.instance.media_new(self.video_path)
            self.media_player.set_media(media)

        # Set the media to the main video and play from the start to end positions
        self.current_clip_start = start
        self.current_clip_end = end
        self.media_player.set_time(int(start * 1000))  # Convert to milliseconds

        # Reapply the current playback speed
        self.media_player.set_rate(self.playback_speed)

        self.media_player.play()
        self.is_playing = True
        self.feedback_label.setText(f"Playing clip: {start:.2f}s - {end:.2f}s")
    else:
        self.feedback_label.setText("Video file not found!")


def change_speed(self):
    """Change the playback speed based on the combo box selection."""
    # Get the selected speed from the combo box
    speed_text = self.speed_combo.currentText()
    self.playback_speed = float(speed_text.replace("x", ""))
    self.media_player.set_rate(self.playback_speed)
    self.feedback_label.setText(f"Playback speed set to {self.playback_speed}x")


def toggle_half_speed(self):
    """Toggle between half speed and normal speed."""
    if self.playback_speed != 0.5:
        self.playback_speed = 0.5
    else:
        self.playback_speed = 1.0
    self.media_player.set_rate(self.playback_speed)
    self.speed_combo.setCurrentText(f"{self.playback_speed}x")
    self.feedback_label.setText(f"Playback speed set to {self.playback_speed}x")


def toggle_dark_mode(self):
    """Toggle between light and dark mode."""
    self.dark_mode = not self.dark_mode
    if self.dark_mode:
        self.setStyleSheet(self.dark_mode_stylesheet())
        self.toggle_dark_mode_button.setText("Disable Dark Mode")
        self.feedback_label.setText("Dark mode enabled.")
    else:
        self.setStyleSheet(self.light_mode_stylesheet())  # Apply light mode stylesheet
        self.toggle_dark_mode_button.setText("Enable Dark Mode")
        self.feedback_label.setText("Dark mode disabled.") 