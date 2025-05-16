from PyQt6.QtCore import Qt, QEvent
from PyQt6.QtWidgets import QToolTip
from playback_control import play_video, pause_video, skip, toggle_half_speed
from clip_manager import start_clip, save_clip, toggle_loop, next_clip, previous_clip, play_favorite, navigate_tree, play_selected_clip
from ui_components import toggle_video_audio_mode


def eventFilter(self, source, event):
    """Handle events for the application."""
    if source is self.position_slider and event.type() == QEvent.Type.MouseMove:
        pos = event.position().x()
        value = self.position_slider.minimum() + (self.position_slider.maximum() - self.position_slider.minimum()) * pos / self.position_slider.width()
        tooltip_time = self.format_time(int(value))
        QToolTip.showText(event.globalPosition().toPoint(), tooltip_time, self.position_slider)
    # Check if the event is a key press event
    elif event.type() == QEvent.Type.KeyPress:
        # Handle left and right arrow keys globally
        if event.key() in [Qt.Key.Key_Right, Qt.Key.Key_K, Qt.Key.Key_F]:
            skip(self, 3)  # Fine-tuned seeking
            return True  # Event handled
        elif event.key() in [Qt.Key.Key_Left, Qt.Key.Key_J, Qt.Key.Key_D]:
            skip(self, -3)  # Fine-tuned seeking
            return True  # Event handled
    return super(self.__class__, self).eventFilter(source, event)


def keyPressEvent(self, event):
    """Handle key press events."""
    key = event.key()
    
    if key in (Qt.Key.Key_Delete, Qt.Key.Key_Backspace):
        self.delete_clip()
    elif key == Qt.Key.Key_Right:
        skip(self, 3)  # Fine-tuned seeking
    elif key == Qt.Key.Key_Left:
        skip(self, -3)  # Fine-tuned seeking
    elif key == Qt.Key.Key_Space:
        if self.is_playing:
            pause_video(self)
        else:
            play_video(self)
    elif key == Qt.Key.Key_S:
        start_clip(self)
    elif key == Qt.Key.Key_E:
        save_clip(self)
    elif key == Qt.Key.Key_L:
        toggle_loop(self)
    elif key in (Qt.Key.Key_N, Qt.Key.Key_Down):
        if self.single_video_mode:
            next_clip(self)
        else:
            navigate_tree(self, 1)  # Move down in the tree
    elif key in (Qt.Key.Key_P, Qt.Key.Key_Up):
        if self.single_video_mode:
            previous_clip(self)
        else:
            navigate_tree(self, -1)  # Move up in the tree
    elif key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
        if self.single_video_mode:
            play_favorite(self)
        else:
            current_item = self.video_clips_tree.currentItem()
            if current_item and not current_item.parent():  # Check if it's a top-level item (video)
                if current_item.isExpanded():
                    self.video_clips_tree.collapseItem(current_item)
                else:
                    self.video_clips_tree.expandItem(current_item)
            else:
                play_selected_clip(self)  # Play the selected clip if it's not a video
    elif key == Qt.Key.Key_A:
        toggle_video_audio_mode(self)  # Toggle video/audio mode with 'A' key
    elif key == Qt.Key.Key_Q:
        toggle_half_speed(self)  # Toggle half speed with 'Q' key 