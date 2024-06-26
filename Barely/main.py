import sys
import os
import time

from PyQt5.QtCore import QTimer, QUrl
from PyQt5.QtGui import QIcon, QPixmap, QKeySequence
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtWidgets import (
    QApplication,
    QFileDialog,
    QMainWindow
)

from barely_ui import Ui_Barely



class Barely(QMainWindow, Ui_Barely):
    def __init__(self):
        
        ### Setup and initialisations
        super().__init__()
        self.setupUi(self)
        
        self.current_files = []
        self.current_volume = 50

        self.player = QMediaPlayer()
        self.player.setVolume(self.current_volume)
        
        self.position_timer = QTimer(self)
        self.position_timer.start(1000)
        self.position_timer.timeout.connect(self.move_position_slider)
        

        ### OS agnostic shortcuts (other hotkeys defined in ui file)
        self.actionOpen.setShortcut(QKeySequence.Open)
        self.actionClose.setShortcut(QKeySequence.Quit)
        

        ### Connections
        self.actionOpen.triggered.connect(self.open_files)
        self.actionClose.triggered.connect(self.quit_application)
        self.actionRemove_selected.triggered.connect(self.remove_selected_files)
        self.actionRemove_all.triggered.connect(self.remove_all_files)
        self.actionPlay_pause.triggered.connect(self.play_pause)
        self.actionNext.triggered.connect(self.play_next_file)
        self.actionPrevious.triggered.connect(self.play_previous_file)
        
        self.player.stateChanged.connect(self.update_now_playing_label)
        self.player.stateChanged.connect(self.change_play_btn_icon)
        self.player.positionChanged.connect(self.move_position_slider)

        self.files_display.doubleClicked.connect(self.handle_file_double_click)
        
        self.position_slider.sliderMoved.connect(lambda: self.player.setPosition(self.position_slider.value()))
        self.volume_slider.valueChanged.connect(lambda: self.volume_changed())
        
        self.play_pause_btn.clicked.connect(self.actionPlay_pause.trigger)
        self.stop_btn.clicked.connect(self.stop_playback)
        self.next_btn.clicked.connect(self.actionNext.trigger)
        self.prev_btn.clicked.connect(self.actionPrevious.trigger)
        self.skip_back_btn.clicked.connect(self.skip_back)
        self.skip_forwards_btn.clicked.connect(self.skip_forwards)
        
        
    ##### FILE HANDLING #####
    def open_files(self):
        try:
            files, _ = QFileDialog.getOpenFileNames(
                parent = self,
                caption = "Select files",
                filter = "Sound files (*.wav *.mp3 *.mpeg *.ogg *.m4a *.MP3 *.wma *.acc *.amr)"
            )
            if files:
                for file in files:
                    self.current_files.append(file)
                    self.files_display.addItem(os.path.basename(file))
                    
        except Exception as e:
            print(f"Open files fail: {e}")
                

    def handle_file_double_click(self, index):
        try:
            selected_file = self.current_files[index.row()]
            self.player.setMedia(QMediaContent(QUrl.fromLocalFile(selected_file)))
            self.player.play()
            self.move_position_slider()
            
        except Exception as e:
            print(f"Files display double click fail: {e}")
            

    def remove_selected_files(self):
        try:
            current_selection = self.files_display.selectedIndexes()
            current_media = self.player.currentMedia()
            
            for i in reversed(current_selection):
                index = i.row()
                
                # Stop playback if removing currently playing file
                if QMediaContent(QUrl.fromLocalFile(self.current_files[index])) == current_media:
                    self.stop_playback()
                    
                self.current_files.pop(index)
                self.files_display.takeItem(index)
                
        except Exception as e:
            print(f"Remove files fail: {e}")


    def remove_all_files(self):
        try:
            self.stop_playback()
            self.files_display.clear()
            self.current_files.clear()
            
        except Exception as e:
            print(f"Remove all files fail: {e}")
            

    ##### SLIDERS & PLAYBACK INFO DISPLAY #####
    def move_position_slider(self):
        if self.player.state() == QMediaPlayer.StoppedState:
            self.position_slider.setValue(0)
            self.current_position_label.setText("--:--")
            self.duration_label.setText("--:--")
            self.now_playing_label.setText("---")
        else:    
            self.position_slider.setMinimum(0)
            self.position_slider.setMaximum(self.player.duration())
            self.position_slider.setValue(self.player.position())
            
            current_position_time = time.strftime("%M:%S", time.localtime(self.player.position() / 1000))
            duration_time = time.strftime("%M:%S", time.localtime(self.player.duration() / 1000))
            self.current_position_label.setText(f"{current_position_time}")
            self.duration_label.setText(f"{duration_time}")
            

    def volume_changed(self):
        try:
            self.current_volume = self.volume_slider.value()
            self.player.setVolume(self.current_volume)
            
        except Exception as e:
            print(f"Change volume fail: {e}")
            

    def update_now_playing_label(self):
        if self.player.currentMedia().isNull():
            self.now_playing_label.setText("---")
        else:
            self.now_playing_label.setText(self.player.currentMedia().canonicalUrl().fileName())


    def change_play_btn_icon(self, player_state):
        try:    
            if player_state == QMediaPlayer.PlayingState:
                self.play_pause_btn.setIcon(QIcon(QPixmap(":/icons/resources/pause.png")))
            else:
                self.play_pause_btn.setIcon(QIcon(QPixmap(":/icons/resources/play.png")))
                
        except Exception as e:
            print(f"Change play button icon fail: {e}")
            

    ##### MEDIA PLAYBACK CONTROLS #####
    def play_pause(self):
        try:   
            # If no files are currently loaded, load current selection and play
            if self.player.currentMedia().isNull(): 
                current_selection = self.files_display.currentRow()
                current_file = self.current_files[current_selection]
                file_url = QMediaContent(QUrl.fromLocalFile(current_file))
                self.player.setMedia(file_url)
                
                self.player.play()
                self.move_position_slider()
                return
            
            # Otherwise, handle play/pause
            if self.player.state() == QMediaPlayer.PlayingState:
                self.player.pause()
            else:
                self.player.play()
                self.move_position_slider()
                
        except Exception as e:
            print(f"Play file fail: {e}")
            

    def stop_playback(self):
        try:
            self.player.stop()
            self.player.setMedia(QMediaContent())   # Remove currently loaded file
            
        except Exception as e:
            print(f"Stop fail: {e}")
            

    def play_next_file(self):
        try:
            next_index = self.files_display.currentRow() + 1
            if next_index >= len(self.current_files):
                next_index = 0
            current_file = self.current_files[next_index]
            self.files_display.setCurrentRow(next_index)
        
            file_url = QMediaContent(QUrl.fromLocalFile(current_file))
            self.player.setMedia(file_url)
            self.player.play()
            self.move_position_slider()
            
        except Exception as e:
            print(f"Next file fail: {e}")
    
        
    def play_previous_file(self):
        try:
            previous_index = self.files_display.currentRow() - 1
            if previous_index < 0:
                previous_index = len(self.current_files) - 1
            current_file = self.current_files[previous_index]
            self.files_display.setCurrentRow(previous_index)
        
            file_url = QMediaContent(QUrl.fromLocalFile(current_file))
            self.player.setMedia(file_url)
            self.player.play()
            self.move_position_slider()
            
        except Exception as e:
            print(f"Previous file fail: {e}")
            

    def skip_forwards(self):
        try:
            new_position = self.player.position() + 10000
            if new_position > self.player.duration():   # Stop playback if trying to skip past end of file
                self.stop_playback()
            else:
                self.player.setPosition(new_position)
            self.move_position_slider()
            
        except Exception as e:
            print(f"Skip forwards fail: {e}")
            

    def skip_back(self):
        try:
            new_position = self.player.position() - 10000
            self.player.setPosition(max(0, new_position))
            self.move_position_slider()
            
        except Exception as e:
            print(f"Skip back fail: {e}")
            

    ##### SYSTEM #####
    def quit_application(self):
        sys.exit(0)
        
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Barely()
    window.show()
    app.exec()