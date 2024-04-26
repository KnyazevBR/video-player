from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QSlider, QLabel, QFileDialog
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5. QtCore import Qt, QUrl

class VideoPlayer(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Video Player")
        self.setGeometry(600, 100, 800, 600)
        self.setStyleSheet("background-color: black;")

        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.videoWidget = QVideoWidget()

        layout = QVBoxLayout()
        layout.addWidget(self.videoWidget)

        controlLayout = QHBoxLayout()

        self.openButton = QPushButton("Открыть видео")
        self.openButton.clicked.connect(self.openVideo)
        self.openButton.setStyleSheet("background-color: #404040; color: white; border: 50px solid black; border-radius: 10px; padding: 8px;")
        controlLayout.addWidget(self.openButton)

        self.rewindButton = QPushButton("◀️")
        self.rewindButton.clicked.connect(self.rewind)
        self.rewindButton.setStyleSheet("background-color: #404040; color: white; border: 1px solid black; border-radius: 10px; padding: 8px;")
        controlLayout.addWidget(self.rewindButton)

        self.playButton = QPushButton("Video Player")
        self.playButton.clicked.connect(self.playPauseVideo)
        self.playButton.setStyleSheet("background-color: #404040; color: white; border: 1px solid black; border-radius: 10px; padding: 10px;")
        controlLayout.addWidget(self.playButton)

        self.fastForwardButton = QPushButton("▶️")
        self.fastForwardButton.clicked.connect(self.fastForward)
        self.fastForwardButton.setStyleSheet("background-color: #404040; color: white; border: 1px solid black; border-radius: 10px; padding: 8px;")
        controlLayout.addWidget(self.fastForwardButton)

        layout.addLayout(controlLayout)
        self.setLayout(layout)

        self.mediaPlayer.setVideoOutput(self.videoWidget)
        self.videoWidget.mousePressEvent = self.playPauseVideo
        self.mediaPlayer.stateChanged.connect(self.updatePlayButton)

    def openVideo(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "Open Video File")
        if fileName:
            self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(fileName)))
            self.mediaPlayer.play()

    def playPauseVideo(self, event=None):
       if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
        self.mediaPlayer.pause()
       else:
        self.mediaPlayer.play()

    def stopVideo(self):
        self.mediaPlayer.stop()

    def fastForward(self):
        self.mediaPlayer.setPosition(self.mediaPlayer.position() + 10000)

    def rewind(self):
        self.mediaPlayer.setPosition(self.mediaPlayer.position() - 10000)

    def setVolume(self, value):
        self.mediaPlayer.setVolume(value)

    def updatePlayButton(self, state):
        if state == QMediaPlayer.PlayingState:
            self.playButton.setText("⏸")
        else:
            self.playButton.setText("ᐅ")

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    player = VideoPlayer()
    player.show()
    sys.exit(app.exec_())
