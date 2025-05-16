import os
import json
from PyQt6.QtCore import Qt
from utils import parse_clip_text


def start_clip(self):
    """Set the start point for a clip."""
    if self.media_player.get_length() > 0:
        self.current_clip_start = max(0, self.media_player.get_time() / 1000.0 - 0.5) # seconds
        self.feedback_label.setText("Clip start point set.")


def save_clip(self):
    """Save the current clip."""
    if self.current_clip_start is not None:
        self.current_clip_end = self.media_player.get_time() / 1000.0  # seconds
        if self.current_clip_end > self.current_clip_start:
            clip_data = {
                'positions': (self.current_clip_start, self.current_clip_end),
            }
            self.favorites.append(clip_data)

            # Sort clips after adding a new one
            sort_clips(self)

            # Update the favorites list widget
            from ui_components import update_favorites_list
            update_favorites_list(self)

            # Save to JSON file
            save_clips_to_file(self)

            # Find the index of the newly added clip
            new_clip_index = self.favorites.index(clip_data)

            if not self.single_video_mode:
                # Update the video clips tree
                from ui_components import update_video_clips_tree, select_clip_in_tree
                update_video_clips_tree(self)

                # Select the newly added clip in the video clips tree
                select_clip_in_tree(self, new_clip_index)
            else:
                # Select the newly added clip in the favorites list
                self.favorites_list.setCurrentRow(new_clip_index)

            self.feedback_label.setText("Clip positions saved!")
        else:
            self.feedback_label.setText("Invalid clip duration.")
    else:
        self.feedback_label.setText("Set the clip start point first.")


def sort_clips(self):
    """Sort the favorites list by start time."""
    self.favorites.sort(key=lambda clip: clip['positions'][0])


def save_clips_to_file(self):
    """Save clips to a JSON file."""
    if self.video_path:
        # Use the updated config_file path
        clips_to_save = [{'positions': clip['positions']} for clip in self.favorites]

        with open(self.config_file, 'w') as f:
            json.dump(clips_to_save, f)

        # Update the favorites list widget
        from ui_components import update_favorites_list
        update_favorites_list(self)
        self.feedback_label.setText("Clip positions saved to file.")


def load_clips_from_file(self):
    """Load clips from a JSON file."""
    if self.video_path:
        self.favorites = []
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                loaded_clips = json.load(f)

            if isinstance(loaded_clips, list) and all(isinstance(clip, dict) for clip in loaded_clips):
                self.favorites = loaded_clips

            self.feedback_label.setText("Clip positions loaded from file.")
        else:
            self.feedback_label.setText("No saved clip positions found.")
        
        # Sort clips after loading
        sort_clips(self)

        # Update the favorites list widget
        from ui_components import update_favorites_list
        update_favorites_list(self)


def play_favorite(self):
    """Play the selected favorite clip."""
    selected_row = self.favorites_list.currentRow()
    if selected_row >= 0:
        clip_data = self.favorites[selected_row]
        # Save the current position of the main video only if not already saved
        if not self.position_saved:
            self.main_video_position = self.media_player.get_time()
            self.position_saved = True

        # Extract start and end positions from the clip data
        start, end = clip_data['positions']

        # Call play_clip with the start and end positions
        from playback_control import play_clip
        play_clip(self, start, end)

        self.return_button.setEnabled(True)
    else:
        self.feedback_label.setText("No clip selected.")


def check_loop_position(self):
    """Check if the current position is at the end of the clip and loop if needed."""
    current_position = self.media_player.get_time()
    if self.current_clip_end is not None:  # Ensure current_clip_end is set
        if current_position >= int(self.current_clip_end * 1000):  # Convert to milliseconds
            if self.loop_enabled:
                # Apply an additional 200ms buffer when looping
                adjusted_start = max(0, self.current_clip_start * 1000 - 100)
                self.media_player.set_time(int(adjusted_start))
                self.media_player.play()
            else:
                self.media_player.pause()
                self.is_playing = False  # Update the is_playing flag
                self.feedback_label.setText("Clip playback finished.")
                self.current_clip_end = None


def delete_clip(self):
    """Delete the selected clip."""
    if self.single_video_mode:
        # Get the selected row from the favorites list
        selected_row = self.favorites_list.currentRow()
        if selected_row >= 0:
            del self.favorites[selected_row]
            self.favorites_list.takeItem(selected_row)
            save_clips_to_file(self)
            from ui_components import update_favorites_list
            update_favorites_list(self)  # Update the favorites list widget
            self.feedback_label.setText(f"Deleted clip {selected_row + 1}")
            if self.favorites_list.count() > 0:
                self.favorites_list.setCurrentRow(max(selected_row - 1, 0))
        else:
            self.feedback_label.setText("No clip selected to delete.")
    else:
        # Get the selected item from the video clips tree
        current_item = self.video_clips_tree.currentItem()
        if current_item and current_item.parent():  # Ensure it's a clip, not a video
            parent_item = current_item.parent()
            clip_index = parent_item.indexOfChild(current_item)
            del self.favorites[clip_index]
            parent_item.takeChild(clip_index)
            save_clips_to_file(self)
            from ui_components import update_video_clips_tree
            update_video_clips_tree(self)  # Update the video clips tree
            self.feedback_label.setText(f"Deleted clip {clip_index + 1}")
            if parent_item.childCount() > 0:
                self.video_clips_tree.setCurrentItem(parent_item.child(max(clip_index - 1, 0)))
        else:
            self.feedback_label.setText("No clip selected to delete.")


def toggle_loop(self):
    """Toggle looping for clips."""
    self.loop_enabled = not self.loop_enabled
    status = "enabled" if self.loop_enabled else "disabled"
    self.feedback_label.setText(f"Looping {status}")


def next_clip(self):
    """Go to the next clip in the favorites list."""
    current_row = self.favorites_list.currentRow()
    next_row = 0
    if current_row < self.favorites_list.count() - 1:
        next_row = current_row + 1
    self.favorites_list.setCurrentRow(next_row)
    play_favorite(self)


def previous_clip(self):
    """Go to the previous clip in the favorites list."""
    current_row = self.favorites_list.currentRow()
    prev_row = self.favorites_list.count() - 1
    if current_row > 0:
        prev_row = current_row - 1
    self.favorites_list.setCurrentRow(prev_row)
    play_favorite(self)


def load_config_files(self):
    """Load all config files and list videos with their clips."""
    self.video_clips_tree.clear()  # Clear existing items
    self.video_clips = {}  # Reset the video clips dictionary

    # Get all JSON files in the config directory and sort them by name
    json_files = sorted([f for f in os.listdir(self.config_dir) if f.endswith('.json')])

    # Iterate over sorted JSON files
    for file_name in json_files:
        video_name = file_name[:-5]  # Remove the '.json' extension

        # Use the video_paths dictionary to find the video path
        video_path = self.video_paths.get(video_name)

        # Check if the video file exists
        if not video_path:
            continue  # Skip this config file if the video file does not exist

        file_path = os.path.join(self.config_dir, file_name)

        with open(file_path, 'r') as f:
            clips = json.load(f)

        # Add video and clips to the tree
        from PyQt6.QtWidgets import QTreeWidgetItem
        video_item = QTreeWidgetItem(self.video_clips_tree, [video_name])
        for clip in clips:
            start, end = clip['positions']
            clip_item = QTreeWidgetItem(video_item, [f"Clip: {start:.2f}s - {end:.2f}s"])
            video_item.addChild(clip_item)

        self.video_clips[video_name] = clips

    self.video_clips_tree.collapseAll()  # Collapse all items initially


def on_clip_selected(self, item, column):
    """Handle the event when a clip is selected in the tree."""
    parent = item.parent()
    if parent is not None:  # Ensure the item is a clip, not a video
        video_name = parent.text(0)
        clip_text = item.text(0)
        start, end = parse_clip_text(clip_text)

        # Use the video_paths dictionary to find the video path
        video_path = self.video_paths.get(video_name)

        # Check if the current video is the same as the new video
        if self.video_path != video_path:
            self.load_video(video_path=video_path)

        # Play the clip
        from playback_control import play_clip
        play_clip(self, start, end)


def navigate_tree(self, direction):
    """Navigate the video clips tree."""
    current_item = self.video_clips_tree.currentItem()
    if current_item:
        if direction > 0:  # Move down
            next_item = self.video_clips_tree.itemBelow(current_item)
        else:  # Move up
            next_item = self.video_clips_tree.itemAbove(current_item)

        if next_item:
            self.video_clips_tree.setCurrentItem(next_item)
            play_selected_clip(self)  # Play the clip after navigating


def play_selected_clip(self):
    """Play the currently selected clip in the tree."""
    current_item = self.video_clips_tree.currentItem()
    if current_item and current_item.parent():  # Ensure it's a clip, not a video
        on_clip_selected(self, current_item, 0) 