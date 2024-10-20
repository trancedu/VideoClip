import tkinter as tk
from tkinter import filedialog
import threading
from moviepy.editor import VideoFileClip
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QListWidget

class VideoPlayerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("English Listening Practice")
        
        # Initialize variables
        self.video_path = None
        self.video_clip = None
        self.is_playing = False
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

        # Favorites
        self.favorites_list = QListWidget()
        layout.addWidget(self.favorites_list)

        self.play_favorite_button = QPushButton("Play Favorite")
        self.play_favorite_button.clicked.connect(self.play_favorite)
        layout.addWidget(self.play_favorite_button)

        self.setLayout(layout)

    def load_video(self):
        self.video_path = filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4 *.avi")])
        if self.video_path:
            self.video_clip = VideoFileClip(self.video_path)

    def play_video(self):
        if not self.is_playing and self.video_path:
            self.is_playing = True
            threading.Thread(target=self.playback).start()

    def playback(self):
        if self.video_clip:
            self.video_clip.preview()
        self.is_playing = False

    def pause_video(self):
        self.is_playing = False

    def skip(self, seconds):
        if self.video_clip:
            current_time = self.video_clip.reader.pos / self.video_clip.fps
            new_time = current_time + seconds
            if new_time > 0:
                self.video_clip.reader.seek(new_time)

    def start_clip(self):
        if self.video_clip:
            self.current_clip_start = self.video_clip.reader.pos / self.video_clip.fps

    def save_clip(self):
        if self.video_clip and self.current_clip_start is not None:
            self.current_clip_end = self.video_clip.reader.pos / self.video_clip.fps
            clip = self.video_clip.subclip(self.current_clip_start, self.current_clip_end)
            self.favorites.append(clip)
            self.favorites_list.insert(tk.END, f"Clip {len(self.favorites)}")

    def play_favorite(self):
        selected = self.favorites_list.curselection()
        if selected:
            clip = self.favorites[selected[0]]
            clip.preview()

if __name__ == "__main__":
    app = QApplication([])
    window = VideoPlayerApp()
    window.show()
    app.exec_()
