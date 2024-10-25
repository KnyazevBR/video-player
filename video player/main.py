import json
import os
import sys

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QSlider, QLabel, QFileDialog, \
    QListWidget, QListWidgetItem, QMessageBox, QComboBox
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtCore import Qt, QUrl


class VideoPlayer(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Видеоплеер")
        self.setGeometry(600, 100, 800, 600)
        self.setWindowIcon(QIcon('youtube.ico'))
        self.setStyleSheet("background-color: black;")

        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.videoWidget = QVideoWidget()

        layout = QVBoxLayout()
        layout.addWidget(self.videoWidget)

        controlLayout = QHBoxLayout()

        button_style = """
        QPushButton {
            background-color: #404040;
            color: white;
            border: 1px solid black;
            border-radius: 10px;
            padding: 8px;
        }
        QPushButton:hover {
            background-color: #606060;
        }
        """

        self.openButton = QPushButton("Открыть видео")
        self.openButton.clicked.connect(self.openVideo)
        self.openButton.setStyleSheet(button_style)
        controlLayout.addWidget(self.openButton)

        self.rewindButton = QPushButton("◀️")
        self.rewindButton.clicked.connect(lambda: self.rewind(10000))  # 10 сек
        self.rewindButton.setStyleSheet(button_style)
        controlLayout.addWidget(self.rewindButton)

        self.playButton = QPushButton("ᐅ")
        self.playButton.clicked.connect(self.playPauseVideo)
        self.playButton.setStyleSheet(button_style)
        controlLayout.addWidget(self.playButton)

        self.fastForwardButton = QPushButton("▶️")
        self.fastForwardButton.clicked.connect(lambda: self.fastForward(10000))  # 10 сек
        self.fastForwardButton.setStyleSheet(button_style)
        controlLayout.addWidget(self.fastForwardButton)

        self.volumeSlider = QSlider(Qt.Horizontal)
        self.volumeSlider.setMinimum(0)
        self.volumeSlider.setMaximum(100)
        self.volumeSlider.setValue(100)
        self.volumeSlider.valueChanged.connect(self.setVolume)
        self.volumeSlider.valueChanged.connect(self.updateVolumeIcon)
        controlLayout.addWidget(self.volumeSlider)

        self.muteButton = QPushButton()
        self.updateVolumeIcon(self.volumeSlider.value())
        self.muteButton.clicked.connect(self.muteUnmute)
        self.muteButton.setStyleSheet(button_style)
        controlLayout.addWidget(self.muteButton)

        self.snapshotButton = QPushButton("📸")
        self.snapshotButton.clicked.connect(self.takeSnapshot)
        self.snapshotButton.setStyleSheet(button_style)
        controlLayout.addWidget(self.snapshotButton)

        self.fullScreenButton = QPushButton("🖥")
        self.fullScreenButton.clicked.connect(self.toggleFullScreen)
        self.fullScreenButton.setStyleSheet(button_style)
        controlLayout.addWidget(self.fullScreenButton)

        self.playbackSpeedComboBox = QComboBox()
        self.playbackSpeedComboBox.addItems(["0.5x", "1.0x", "1.5x", "2.0x"])
        self.playbackSpeedComboBox.setCurrentText("1.0x")
        self.playbackSpeedComboBox.currentIndexChanged.connect(self.setPlaybackSpeed)
        self.playbackSpeedComboBox.setStyleSheet("""
        QComboBox {
            background-color: #404040;
            color: white;
            border: 1px solid black;
            border-radius: 10px;
            padding: 8px;
        }
        QComboBox:hover {
            background-color: #606060;
        }
        QComboBox QAbstractItemView {
            background-color: #404040;
            color: white;
            selection-background-color: #606060;
        }
        """)
        controlLayout.addWidget(self.playbackSpeedComboBox)

        layout.addLayout(controlLayout)

        self.seekSlider = QSlider(Qt.Horizontal)
        self.seekSlider.setRange(0, 0)
        self.seekSlider.sliderMoved.connect(self.setPosition)
        layout.addWidget(self.seekSlider)

        self.setLayout(layout)

        self.mediaPlayer.setVideoOutput(self.videoWidget)
        self.videoWidget.mousePressEvent = self.playPauseVideo
        self.mediaPlayer.stateChanged.connect(self.updatePlayButton)
        self.mediaPlayer.positionChanged.connect(self.positionChanged)
        self.mediaPlayer.durationChanged.connect(self.durationChanged)

        self.settings_file = 'player_settings.json'
        self.history_file = 'video_history.json'
        self.current_file = None

        self.loadSettings()

    def closeEvent(self, event):
        self.mediaPlayer.stop()
        self.saveSettings()
        super(VideoPlayer, self).closeEvent(event)

    def saveSettings(self):
        settings = {
            'volume': self.mediaPlayer.volume(),
            'muted': self.mediaPlayer.isMuted(),
            'playbackRate': self.mediaPlayer.playbackRate(),
        }
        file_settings = self.loadSettings()
        file_settings[self.current_file] = settings
        with open(self.settings_file, 'w') as file:
            json.dump(file_settings, file)

    def loadSettings(self):
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r') as file:
                    return json.load(file)
            except json.JSONDecodeError as e:
                print(f"Ошибка при прочтении файла настроек: {e}")
        return {}

    def saveHistory(self):
        if self.current_file:
            history = self.loadHistory()
            video_info = {
                'file': self.current_file,
                'position': self.mediaPlayer.position(),
                'volume': self.mediaPlayer.volume(),
                'playbackRate': self.mediaPlayer.playbackRate(),
                'muted': self.mediaPlayer.isMuted()
            }
            # Удалить предыдущую запись, если она существует
            history = [v for v in history if v['file'] != self.current_file]
            # Добавить обновленную запись
            history.append(video_info)
            with open(self.history_file, 'w') as file:
                json.dump(history, file)

    def loadHistory(self):
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r') as file:
                    history = json.load(file)
                    return history
            except json.JSONDecodeError as e:
                print(f"Ошибка при прочтении истории видео: {e}")
        return []

    def loadVideo(self, file_path):
        self.current_file = file_path
        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(file_path)))
        history = self.loadHistory()
        video_info = next((item for item in history if item['file'] == file_path), None)
        if video_info:
            self.mediaPlayer.setVolume(video_info.get('volume', 100))
            self.mediaPlayer.setPlaybackRate(video_info.get('playbackRate', 1.0))
            self.mediaPlayer.setMuted(video_info.get('muted', False))
            self.mediaPlayer.setPosition(video_info.get('position', 0))
        self.mediaPlayer.play()

    def resetSettingsToDefaults(self):
        self.mediaPlayer.setVolume(100)
        self.volumeSlider.setValue(100)

        self.mediaPlayer.setPlaybackRate(1.0)
        self.updatePlaybackSpeedComboBox(1.0)

        self.mediaPlayer.setMuted(False)
        self.muteButton.setText("🔇")

        self.mediaPlayer.setPosition(0)

    def openVideo(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "Открыть видеофайл", "",
                                                  "Video Files (*.mp4 *.avi *.mkv);;All Files (*)")
        if fileName:
            self.loadVideo(fileName)
            self.saveHistory()
    def playPauseVideo(self, event=None):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.mediaPlayer.pause()
        else:
            self.mediaPlayer.play()

    def stopVideo(self):
        self.mediaPlayer.stop()

    def fastForward(self, interval):
        current_position = self.mediaPlayer.position()
        new_position = current_position + interval
        self.mediaPlayer.setPosition(new_position)

    def rewind(self, interval):
        current_position = self.mediaPlayer.position()
        new_position = max(0, current_position - interval)
        self.mediaPlayer.setPosition(new_position)

    def updateVolumeIcon(self, value):
        if value == 0:
            self.muteButton.setText("🔇")
        elif 0 < value <= 30:
            self.muteButton.setText("🔈")
        elif 30 < value <= 70:
            self.muteButton.setText("🔉")
        else:
            self.muteButton.setText("🔊")

    def setVolume(self, value):
        self.mediaPlayer.setVolume(value)

    def muteUnmute(self):
        if self.mediaPlayer.isMuted():
            self.mediaPlayer.setMuted(False)
            self.updateVolumeIcon(self.volumeSlider.value())
        else:
            self.mediaPlayer.setMuted(True)
            self.muteButton.setText("🔇")

    def takeSnapshot(self):
        videoFrame = self.videoWidget.grab()
        fileName, _ = QFileDialog.getSaveFileName(self, "Сохранить скриншот", "", "PNG Files (*.png);;All Files (*)")
        if fileName:
            videoFrame.save(fileName)

    def toggleFullScreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def setPlaybackSpeed(self, index):
        speeds = {
            0: 0.5,
            1: 1.0,
            2: 1.5,
            3: 2.0
        }
        speed = speeds.get(index, 1.0)
        self.mediaPlayer.setPlaybackRate(speed)

    def setPosition(self, position):
        self.mediaPlayer.setPosition(position)

    def positionChanged(self, position):
        self.seekSlider.setValue(position)

    def durationChanged(self, duration):
        self.seekSlider.setRange(0, duration)

    def updatePlayButton(self, state):
        if state == QMediaPlayer.PlayingState:
            self.playButton.setText("⏸")
        else:
            self.playButton.setText("ᐅ")

    def updatePlaybackSpeedComboBox(self, playbackRate):
        for i in range(self.playbackSpeedComboBox.count()):
            if float(self.playbackSpeedComboBox.itemText(i).replace('x', '')) == playbackRate:
                self.playbackSpeedComboBox.setCurrentIndex(i)
                break

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()
        else:
            super(VideoPlayer, self).keyPressEvent(event)


class MainWindow(QWidget):
    def __init__(self, player):
        super().__init__()

        self.player = player

        self.setWindowTitle("Каталог")
        self.setGeometry(600, 100, 800, 600)
        self.setWindowIcon(QIcon('youtube.ico'))
        self.setStyleSheet("background-color: #202020; color: white;")

        layout = QVBoxLayout()

        self.videoListWidget = QListWidget()
        self.loadVideoHistory()
        self.videoListWidget.itemDoubleClicked.connect(self.playVideo)
        layout.addWidget(self.videoListWidget)

        buttonLayout = QHBoxLayout()

        # Стиль для кнопок
        button_style = """
            QPushButton {
                background-color: #404040;
                color: white;
                border: 1px solid black;
                border-radius: 10px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #606060;
            }
        """

        self.deleteButton = QPushButton("Удалить видео")
        self.deleteButton.setStyleSheet(button_style + "background-color: #ff0000;")
        self.deleteButton.clicked.connect(self.deleteVideo)
        buttonLayout.addWidget(self.deleteButton)

        self.openPlayerButton = QPushButton("Открыть видеоплеер")
        self.openPlayerButton.setStyleSheet(button_style + "background-color: #00ff00;")
        self.openPlayerButton.clicked.connect(self.openPlayer)
        buttonLayout.addWidget(self.openPlayerButton)

        layout.addLayout(buttonLayout)
        self.setLayout(layout)

    def loadVideoHistory(self):
        history = self.player.loadHistory()
        for video in history:
            item = QListWidgetItem(video['file'])
            item.setData(Qt.UserRole, video['position'])
            self.videoListWidget.addItem(item)

    def deleteVideo(self):
        selectedItems = self.videoListWidget.selectedItems()
        if not selectedItems:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, выберите видео для удаления.")
            return

        for item in selectedItems:
            self.videoListWidget.takeItem(self.videoListWidget.row(item))
            history = self.player.loadHistory()
            history = [video for video in history if video['file'] != item.text()]
            with open(self.player.history_file, 'w') as file:
                json.dump(history, file)

    def playVideo(self, item):
        try:
            file_path = item.text()
            self.player.loadVideo(file_path)
            self.player.show()
            self.player.saveHistory()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось воспроизвести видео: {e}")

    def openPlayer(self):
        self.player.show()
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()
        else:
            super(MainWindow, self).keyPressEvent(event)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    player = VideoPlayer()
    mainWindow = MainWindow(player)
    mainWindow.show()
    sys.exit(app.exec_())