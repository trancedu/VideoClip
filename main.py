import tkinter as tk
from tkinter import filedialog
import threading
from moviepy.editor import VideoFileClip
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QListWidget, QFileDialog, QLabel
import time
import cv2

class VideoPlayerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("English Listening Practice")
        
        # Initialize variables
        self.video_path = None
        self.video_clip = None
        self.is_playing = False
        self.is_paused = False
        self.favorites = []
        self.current_clip_start = None
        self.current_clip_end = None

        # Create widgets
        self.create_widgets()

    def create_widgets(self):
        layout = QVBoxLayout()

        # Load Video Button
        self.load_button = QPushButton("Load Video")
        self.load_button.clicked.connect(self.load_video)
        layout.addWidget(self.load_button)

        # Video controls
        self.play_button = QPushButton("Play")
        self.play_button.clicked.connect(self.play_video)
        layout.addWidget(self.play_button)

        self.pause_button = QPushButton("Pause")
        self.pause_button.clicked.connect(self.pause_video)
        layout.addWidget(self.pause_button)

        self.forward_button = QPushButton("Forward 5s")
        self.forward_button.clicked.connect(lambda: self.skip(5))
        layout.addWidget(self.forward_button)

        self.backward_button = QPushButton("Backward 5s")
        self.backward_button.clicked.connect(lambda: self.skip(-5))
        layout.addWidget(self.backward_button)

        # Clip controls
        self.clip_button = QPushButton("Start Clip")
        self.clip_button.clicked.connect(self.start_clip)
        layout.addWidget(self.clip_button)

        self.save_clip_button = QPushButton("Save Clip")
        self.save_clip_button.clicked.connect(self.save_clip)
        layout.addWidget(self.save_clip_button)

        # Feedback label
        self.feedback_label = QLabel("")
        layout.addWidget(self.feedback_label)

        # Favorites
        self.favorites_list = QListWidget()
        layout.addWidget(self.favorites_list)

        self.play_favorite_button = QPushButton("Play Favorite")
        self.play_favorite_button.clicked.connect(self.play_favorite)
        layout.addWidget(self.play_favorite_button)

        self.setLayout(layout)

    def load_video(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        self.video_path, _ = QFileDialog.getOpenFileName(self, "Open Video File", "", "Video Files (*.mp4 *.avi)", options=options)
        if self.video_path:
            self.video_clip = VideoFileClip(self.video_path)

    def play_video(self):
        if not self.is_playing and self.video_path:
            self.is_playing = True
            self.is_paused = False
            threading.Thread(target=self.playback).start()

    def playback(self):
        if self.video_clip:
            cap = cv2.VideoCapture(self.video_path)
            while cap.isOpened():
                if not self.is_playing:
                    break
                if self.is_paused:
                    time.sleep(0.1)  # Wait while paused
                    continue
                
                ret, frame = cap.read()
                if not ret:
                    break
                
                cv2.imshow('Video', frame)
                if cv2.waitKey(25) & 0xFF == ord('q'):  # Press 'q' to quit
                    break
            
            cap.release()
            cv2.destroyAllWindows()
            self.is_playing = False

    def pause_video(self):
        if self.is_playing:  # Only pause if currently playing
            self.is_paused = True

    def skip(self, seconds):
        if self.video_clip:
            current_time = self.video_clip.reader.pos / self.video_clip.fps
            new_time = current_time + seconds
            if new_time > 0:
                self.video_clip.set_duration(new_time)

    def start_clip(self):
        if self.video_clip:
            self.current_clip_start = self.video_clip.reader.pos / self.video_clip.fps
            self.feedback_label.setText("Clip has started!")  # Feedback for starting a clip

    def save_clip(self):
        if self.video_clip and self.current_clip_start is not None:
            self.current_clip_end = self.video_clip.reader.pos / self.video_clip.fps
            clip = self.video_clip.subclip(self.current_clip_start, self.current_clip_end)
            self.favorites.append(clip)
            self.favorites_list.addItem(f"Clip {len(self.favorites)}")

    def play_favorite(self):
        selected_row = self.favorites_list.currentRow()  # Use currentRow instead of curselection
        if selected_row >= 0:
            self.pause_video()  # Pause the current video
            clip = self.favorites[selected_row]
            threading.Thread(target=self.play_favorite_clip, args=(clip,)).start()  # Play in a separate thread

    def play_favorite_clip(self, clip):
        clip.preview()  # Play the favorite clip
        self.is_playing = False  # Update the playing state after the clip finishes

if __name__ == "__main__":
    app = QApplication([])
    window = VideoPlayerApp()
    window.show()
    app.exec_()
