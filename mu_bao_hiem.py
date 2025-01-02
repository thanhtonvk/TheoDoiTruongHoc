from flask import Flask, render_template, Response, request, redirect, url_for
import os
import cv2
import cv2
import threading
import time
import pygame
import requests
from modules.helmet_detection import predictHelmet
from modules.bicycle_detection import combineBoxes

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
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
TELEGRAM_PHOTO_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
classes = ["khong doi mu", "doi mu"]


def send_telegram_message(message):
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    requests.post(TELEGRAM_API_URL, data=data)


def send_telegram_photo(frame):
    _, img_encoded = cv2.imencode(".jpg", frame)
    files = {"photo": ("image.jpg", img_encoded.tobytes())}
    data = {"chat_id": TELEGRAM_CHAT_ID}
    requests.post(TELEGRAM_PHOTO_URL, data=data, files=files)
import pygame
pygame.init()
pygame.mixer.init()
def play_canh_bao():
    if not pygame.mixer.music.get_busy():
        pygame.mixer.music.load("Alarm/hoc_sinh_doi_mu_bao_hiem.mp3")
        pygame.mixer.music.play()
        pygame.time.set_timer(pygame.USEREVENT, 10000)
last_sent_time = 0  # Thời gian lần cuối gửi tin nhắn
DELAY = 10
app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "static/uploads"
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)


camera_active = False
video_path = None
detect_mode = False  # Flag to activate detection mode


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
    global last_sent_time
    global camera_source
    global media_player
    global snapshot_path
    cap = None

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
        resultBike = combineBoxes(frame)
        if resultBike is not None:
            boxes, labels = resultBike
            for box, label in zip(boxes, labels):
                x_min, y_min, x_max, y_max = box
                xmin1, ymin1, xmax1, ymax1 = box
                cropped = frame[y_min:y_max, x_min:x_max]
                resultHelmet = predictHelmet(cropped)
                if resultHelmet:
                    boxesHelmet, labelsHelmet = resultHelmet
                    for boxHelmet, labelHelmet in zip(boxesHelmet, labelsHelmet):
                        if labelHelmet == 0:
                            current_time = time.time()
                            if current_time - last_sent_time > DELAY:  # Kiểm tra nếu đủ 10 giây
                                last_sent_time = current_time
                                threading.Thread(target=play_canh_bao).start()
                                # Gửi tin nhắn và ảnh lên Telegram
                                threading.Thread(
                                    target=send_telegram_message, args=("Học sinh không đội mũ bảo hiểm",)
                                ).start()
                                threading.Thread(
                                    target=send_telegram_photo, args=(image,)
                                ).start()
                        xmin2, ymin2, xmax2, ymax2 = boxHelmet
                        w = xmax2 - xmin2
                        h = ymax2 - ymin2
                        xmin3 = xmin1 + xmin2
                        xmax3 = xmin3 + w
                        ymin3 = ymin1 + ymin2
                        ymax3 = ymin3 + h
                        cv2.rectangle(
                            frame,
                            (xmin3, ymin3),
                            (xmax3, ymax3),
                            (255, 255, 0),
                            2,
                        )
                        cv2.putText(
                            frame,
                            classes[labelHelmet],
                            (x_min, y_min),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            1,
                            (255, 0, 0),
                            2,
                            cv2.LINE_AA,
                        )
                cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)

        _, buffer = cv2.imencode(".jpg", frame)
        frame = buffer.tobytes()

        yield (b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")

    cap.release()


@app.route("/mu-bao-hiem")
def index():
    return render_template("mu_bao_hiem.html")


@app.route("/video_feed")
def video_feed():
    return Response(
        generate_frames(), mimetype="multipart/x-mixed-replace; boundary=frame"
    )


@app.route("/control", methods=["POST"])
def control():
    global camera_active, video_path, detect_mode

    action = request.form.get("action")

    if action == "camera":
        camera_active = True
        detect_mode = True
        video_path = None
    elif action == "exit":
        camera_active = False
        detect_mode = False
        video_path = None
    elif "video_file" in request.files:
        file = request.files["video_file"]
        if file and file.filename:
            video_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
            file.save(video_path)
            detect_mode = True
            camera_active = False
        else:
            return "No video file uploaded!", 400

    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True,port=3333)
