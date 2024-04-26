import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QFileDialog, QSlider, QLabel
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtCore import Qt, QTimer

class VideoPlayer(QMainWindow):
    def __init__(self):
        super().__init__()

        # Initialize media player
        self.media_player = QMediaPlayer(self)
        self.media_player.setVolume(50)

        # Initialize buttons
        self.play_button = QPushButton('Play', self)
        self.pause_button = QPushButton('Pause', self)
        self.stop_button = QPushButton('Stop', self)
        self.forward_button = QPushButton('Forward', self)
        self.backward_button = QPushButton('Backward', self)

        # Initialize slider for video position
        self.position_slider = QSlider(Qt.Horizontal, self)
        self.position_slider.setRange(0, 0)

        # Initialize label for video duration
        self.duration_label = QLabel('00:00', self)

        # Set button positions
        self.play_button.move(10, 10)
        self.pause_button.move(80, 10)
        self.stop_button.move(150, 10)
        self.forward_button.move(220, 10)
        self.backward_button.move(290, 10)
        self.position_slider.move(10, 50)
        self.duration_label.move(310, 50)

        # Connect button signals
        self.play_button.clicked.connect(self.play_video)
        self.pause_button.clicked.connect(self.pause_video)
        self.stop_button.clicked.connect(self.stop_video)
        self.forward_button.clicked.connect(self.forward_video)
        self.backward_button.clicked.connect(self.backward_video)

        # Connect position slider signal
        self.media_player.positionChanged.connect(self.set_position)

        # Connect duration change signal
        self.media_player.durationChanged.connect(self.set_duration)

        # Initialize timer for forward/backward buttons
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.media_player.play)

        # Set window title and size
        self.setWindowTitle('Video Player')
        self.setGeometry(100, 100, 400, 300)

    def open_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, 'Open Video File', '', 'Video Files (*.mp4 *.avi *.mov)')
        if file_name:
            self.media_player.setMedia(QMediaContent(file_name))
            self.media_player.play()

    def play_video(self):
        if self.media_player.state() == QMediaPlayer.PlayingState:
            self.pause_video()
        elif self.media_player.state() == QMediaPlayer.PausedState:
            self.media_player.play()
        else:
            self.open_file()

    def pause_video(self):
        if self.media_player.state() == QMediaPlayer.PlayingState:
            self.media_player.pause()

    def stop_video(self):
        self.media_player.stop()

    def forward_video(self):
        position = self.media_player.position()
        duration = self.media_player.duration()
        if position + 5000 < duration:
            position += 5000
            self.media_player.setPosition(position)
            self.timer.start(5000)

    def backward_video(self):
        position = self.media_player.position()
        if position > 5000:
            position -= 5000
            self.media_player.setPosition(position)
            self.timer.start(5000)
        else:
            self.media_player.setPosition(0)

    def set_position(self, position):
        self.position_slider.setValue(position)

    def set_duration(self, duration):
        self.position_slider.setRange(0, duration)
        self.duration_label.setText(self.format_time(duration))

    def format_time(self, time):
        minutes, seconds = divmod(time / 1000, 60)
        return '{:02d}:{:02d}'.format(int(minutes), int(seconds))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    player = VideoPlayer()
    player.show()
    sys.exit(app.exec_())