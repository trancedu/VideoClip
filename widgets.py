from PyQt5.QtWidgets import QWidget, QSlider, QListWidget, QTreeWidget, QStyle
from PyQt5.QtCore import Qt


class ClickableVideoWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_OpaquePaintEvent)
        self.setAttribute(Qt.WA_DontCreateNativeAncestors)
        self.setAttribute(Qt.WA_NativeWindow)

    def mousePressEvent(self, event):
        # Call the toggle play/pause method in the parent
        self.parent().toggle_play_pause()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.parent().media_player:
            self.parent().media_player.video_set_scale(0)


class ClickableSlider(QSlider):
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # Calculate the new position based on the click
            new_value = QStyle.sliderValueFromPosition(
                self.minimum(), self.maximum(), event.x(), self.width())
            self.setValue(new_value)
            self.parent().set_position(new_value)
        super().mousePressEvent(event)


class CustomListWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.itemDoubleClicked.connect(self.parent().play_favorite)  # Connect double-click to play_favorite

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_L:
            self.parent().toggle_loop()
        elif event.key() in (Qt.Key_Delete, Qt.Key_Backspace):
            self.parent().delete_clip()
        else:
            self.parent().keyPressEvent(event)


class CustomTreeWidget(QTreeWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

    def keyPressEvent(self, event):
        self.parent().keyPressEvent(event) 