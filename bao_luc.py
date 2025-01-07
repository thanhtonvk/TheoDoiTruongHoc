from flask import Flask, render_template, Response, request, redirect, url_for
import os
import cv2
from ultralytics import YOLO
import cv2
import threading
import time
from ultralytics import YOLO
import pygame
import requests
from modules.bao_luc import predict_baoluc
from scipy.spatial import distance
import numpy as np

# Initialize pygame for sound playback
pygame.init()
pygame.mixer.init()


def is_intersect(x_min1, y_min1, x_max1, y_max1, x_min2, y_min2, x_max2, y_max2):
    if x_max1 < x_min2 or x_max2 < x_min1:
        return False
    if y_max1 < y_min2 or y_max2 < y_min1:
        return False
    return True


frame_count = 0
start_time = time.time()
font = cv2.FONT_HERSHEY_SIMPLEX

font_scale = 1  # Kích thước font chữ
color = (0, 255, 0)  # Màu chữ (xanh lá cây)
thickness = 2
# Telegram bot configuration
TELEGRAM_BOT_TOKEN = "7233650823:AAGr1Cmpr56o4NBdJFyloFUDfltqjnA1dwA"
TELEGRAM_CHAT_ID = "7131930827"
# # Telegram bot configuration
TELEGRAM_BOT_TOKEN = "7651376320:AAHZwGFq1KOyqDfXRq1hjgPt8eeUpO_ZJiE"
TELEGRAM_CHAT_ID = "7877938970"
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
TELEGRAM_PHOTO_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"

bbox_color = (150, 0, 0)
bbox_thickness = 6
bbox_labelstr = {
    "font_size": 6,
    "font_thickness": 14,
    "offset_x": 0,
    "offset_y": -80,
}


def play_canh_bao_tu_cap():
    # cảnh bảo tụ tập quá 5 người
    print("Cảnh báo tụ tập quá 5 người")
    if not pygame.mixer.music.get_busy():
        pygame.mixer.music.load("Alarm/khongtutapdongnguoi.mp3")
        pygame.mixer.music.play()
        pygame.time.set_timer(pygame.USEREVENT, 3000)


def play_khong_duoc_dua_nhau():
    print("Canh bao khong duoc dua nhau")
    if not pygame.mixer.music.get_busy():
        pygame.mixer.music.load("Alarm/khongtutapdongnguoi.mp3")
        pygame.mixer.music.play()
        pygame.time.set_timer(pygame.USEREVENT, 3000)


def play_xo_sat():
    print("Cảnh báo xô sát")
    pygame.mixer.music.load("Alarm/khongduocduanhau.mp3")
    pygame.mixer.music.play()
    pygame.time.set_timer(pygame.USEREVENT, 3000)


def send_telegram_message(message):
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    requests.post(TELEGRAM_API_URL, data=data)


def send_telegram_photo(frame):
    _, img_encoded = cv2.imencode(".jpg", frame)
    files = {"photo": ("image.jpg", img_encoded.tobytes())}
    data = {"chat_id": TELEGRAM_CHAT_ID}
    requests.post(TELEGRAM_PHOTO_URL, data=data, files=files)


def group_keys_by_shared_values(d):
    groups = []
    visited = set()

    for key, values in d.items():
        if key not in visited:
            # Tạo một nhóm mới và bắt đầu thêm vào các khóa có giá trị chung
            group = {key}
            visited.add(key)

            for other_key, other_values in d.items():
                if other_key != key and other_key not in visited:
                    # Kiểm tra nếu có bất kỳ giá trị nào chung giữa hai khóa
                    if any(value in values for value in other_values):
                        group.add(other_key)
                        visited.add(other_key)

            # Thêm nhóm vừa tìm được vào danh sách các nhóm
            groups.append(group)
    return groups


def get_max_bbox(boxes):
    x_min = min([x1 for (x1, y1, x2, y2) in boxes])
    y_min = min([y1 for (x1, y1, x2, y2) in boxes])
    x_max = max([x2 for (x1, y1, x2, y2) in boxes])
    y_max = max([y2 for (x1, y1, x2, y2) in boxes])
    return x_min, y_min, x_max, y_max


def compute_centroids(bboxes):
    centroids = []
    for x, y, w, h in bboxes:
        cx = x + w / 2
        cy = y + h / 2
        centroids.append((cx, cy))
    return centroids


def predict(frame):
    result_predict = []
    results = model.predict(frame, verbose=False)
    bounding_boxes = results[0].boxes.xywh.cpu().detach().numpy().astype("int")
    boxes = results[0].boxes.xyxy.cpu().detach().numpy().astype("int")
    labels = results[0].boxes.cls.cpu().detach().numpy().astype("int")
    bounding_boxes = [bounding_boxes[i] for i in range(len(labels)) if labels[i] == 0]
    boxes = [boxes[i] for i in range(len(labels)) if labels[i] == 0]
    if (len(boxes)) > 0:
        centroids = compute_centroids(bounding_boxes)
        dist_matrix = distance.cdist(centroids, centroids, "euclidean")
        dict_nearly = {}
        for i, distances in enumerate(dist_matrix):
            dict_nearly[i] = []
            for j, dis in enumerate(distances):
                if dis < 150:
                    dict_nearly[i].append(j)
        grouped_keys = group_keys_by_shared_values(dict_nearly)
        for group in grouped_keys:
            if len(group) > 0:
                x_min, y_min, x_max, y_max = get_max_bbox([boxes[i] for i in group])
                result_predict.append((len(group), x_min, y_min, x_max, y_max))
        return result_predict
    return None


app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "static/uploads"
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# Load YOLO model
model = YOLO("models/yolo11m.pt")

camera_active = False
video_path = None
detect_mode = False  # Flag to activate detection mode


result = None
THOI_GIAN_XO_XAT = 2
THOI_GIAN_BAO_LUC = 6
is_play_danh_nhau = False
is_play_audio = True
TRANG_THAI = ""
is_normal_state = False

frames = []
count_frame = 0
count_bao_luc = 0
count_tu_tap = 0

import vlc
camera_source = "rtsp://admin:180683xo@192.168.1.2:554/onvif1"
instance = vlc.Instance()
media = instance.media_new(camera_source)
media_player = instance.media_player_new()
media_player.set_media(media)
media_player.play()
snapshot_path = "snapshot1.png"
media_player.video_take_snapshot(0, snapshot_path, 0, 0)
time.sleep(2)

def generate_frames():
    global camera_active, video_path, detect_mode
    global result, THOI_GIAN_BAO_LUC, THOI_GIAN_XO_XAT, is_play_audio, is_play_danh_nhau
    global TRANG_THAI, is_normal_state, count_frame, count_bao_luc, count_tu_tap
    global frames
    global camera_source
    global media_player
    global snapshot_path
    cap = None

    # Determine the video source (camera or uploaded video)
    if camera_active:
        if camera_source is None:
            cap = cv2.VideoCapture(0)
    elif video_path:
        cap = cv2.VideoCapture(video_path)

    while True:
        if camera_source is None:
            success, frame = cap.read()
            if not success:
                break
        else:
            media_player.video_take_snapshot(0, snapshot_path, 0, 0)
            frame = cv2.imread(snapshot_path)
            if frame is None:
                break
        image = frame.copy()
        results = predict(frame)
        if results is not None:
            for soluong, x_min, y_min, x_max, y_max in results:
                if soluong > 1:
                    cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)
                    cv2.putText(
                        frame,
                        f"So luong {soluong}",
                        (x_min, y_min),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1,
                        (255, 0, 0),
                        2,
                        cv2.LINE_AA,
                    )
                if soluong >= 5:
                    count_tu_tap += 1
                else:
                    count_tu_tap = 0
        frames.append(image)
        if len(frames) == 30:
            threading.Thread(target=predict_bao_luc, args=[frames]).start()
            frames = []
        if (
            count_tu_tap > 0
            and TRANG_THAI != "BAO LUC"
            and TRANG_THAI != "Xo xat"
            and TRANG_THAI != "Tu tap"
        ):
            TRANG_THAI = "Tu tap"
            threading.Thread(target=play_canh_bao_tu_cap).start()
            print("Cảnh bảo tụ tập")
        if result:
            if not is_normal_state:
                count_bao_luc += 1
                if (
                    count_bao_luc >= THOI_GIAN_XO_XAT
                    and count_bao_luc < THOI_GIAN_BAO_LUC
                    and count_bao_luc % THOI_GIAN_XO_XAT == 0
                ):
                    TRANG_THAI = "Xo xat"
                    threading.Thread(target=play_xo_sat).start()
                if count_bao_luc >= THOI_GIAN_BAO_LUC:
                    TRANG_THAI = "BAO LUC"
                    threading.Thread(target=play_canh_bao_danh_nhau).start()
                    threading.Thread(
                        target=send_telegram_message, args=("Xảy ra bạo lực",)
                    ).start()
                    threading.Thread(target=send_telegram_photo, args=(image,)).start()
            else:
                TRANG_THAI = "BINH THUONG"
                is_normal_state = True  # Kích hoạt trạng thái "BÌNH THƯỜNG"
                count_bao_luc = 0
            result = None

        frame = cv2.putText(
            frame,
            TRANG_THAI,
            (50, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 0, 0),
            2,
            cv2.LINE_AA,
        )

        _, buffer = cv2.imencode(".jpg", frame)
        frame = buffer.tobytes()

        yield (b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")

    cap.release()


def play_canh_bao_danh_nhau():
    global is_play_danh_nhau
    global is_play_audio
    print("Cảnh báo đánh nhau")
    if not pygame.mixer.music.get_busy() and is_play_audio:
        pygame.mixer.music.load("Alarm/alarm.wav")
        if not pygame.mixer.music.get_busy():
            pygame.mixer.music.play()
        pygame.time.set_timer(pygame.USEREVENT, 30000)


def stopAmThanh():
    global is_play_danh_nhau
    global is_play_audio
    is_play_danh_nhau = False
    pygame.mixer.music.stop()
    is_play_audio = False


def predict_bao_luc(frames):
    global result
    result = predict_baoluc(frames)
    print(result)


@app.route("/bao-luc")
def index():
    return render_template("bao_luc.html")


@app.route("/video_feed")
def video_feed():
    return Response(
        generate_frames(), mimetype="multipart/x-mixed-replace; boundary=frame"
    )


@app.route("/control", methods=["POST"])
def control():
    global camera_active, video_path, detect_mode,camera_source

    action = request.form.get("action")

    if action == "camera":
        camera_active = True
        detect_mode = True
        video_path = None
        camera_source = "rtsp://admin:180683xo@192.168.1.2:554/onvif1"
    elif action == "exit":
        camera_active = False
        detect_mode = False
        video_path = None
    elif "video_file" in request.files:
        file = request.files["video_file"]
        camera_source = None
        if file and file.filename:
            video_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
            print(video_path)
            file.save(video_path)
            detect_mode = True
            camera_active = False
        else:
            return "No video file uploaded!", 400
    elif action == "stop":
        stopAmThanh()

    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True, port=1111)
