import vlc
import cv2
import numpy as np
import time

class VLCPlayer:
    def __init__(self, rtsp_url):
        # Tạo instance của VLC
        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()
        
        # Thiết lập media từ RTSP URL
        media = self.instance.media_new(rtsp_url)
        self.player.set_media(media)
        
        # Tạo buffer để lưu frame
        self.frame = None
        
        # Liên kết hàm callback cho video output
        self.player.video_set_callbacks(self.lock, self.unlock, self.display)
        self.player.video_set_format("RV32", 1920, 1080, 1920 * 4)

    def lock(self, opaque, planes):
        # Hàm được gọi khi bắt đầu xử lý khung hình
        return self.frame_buffer.ctypes.data

    def unlock(self, opaque, picture, planes):
        # Hàm được gọi sau khi xử lý xong
        pass

    def display(self, opaque, picture):
        # Hàm được gọi để hiển thị khung hình
        self.frame = self.frame_buffer.copy()

    def start(self):
        # Bắt đầu phát
        self.player.play()
        time.sleep(1)  # Chờ camera ổn định

    def read(self):
        # Đọc frame hiện tại
        return self.frame