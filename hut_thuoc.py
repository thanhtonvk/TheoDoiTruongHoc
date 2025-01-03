from flask import Flask, render_template, Response, request, redirect, url_for
import os
import requests
import cv2
import threading
from modules.smoke_detection import predictPerson, predictSmoke
from modules.FaceDetector import FaceDetector
import time

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "uploads"

source = "camera"  # Mặc định là sử dụng camera

TELEGRAM_BOT_TOKEN = "7233650823:AAGr1Cmpr56o4NBdJFyloFUDfltqjnA1dwA"
TELEGRAM_CHAT_ID = "7131930827"
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
TELEGRAM_PHOTO_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"


faceDetector = FaceDetector()


def is_intersect(x_min1, y_min1, x_max1, y_max1, x_min2, y_min2, x_max2, y_max2):
    if x_max1 < x_min2 or x_max2 < x_min1:
        return False
    if y_max1 < y_min2 or y_max2 < y_min1:
        return False
    return True


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
        pygame.mixer.music.load("Alarm/hoc_sinh_khong_duoc_hut_thuoc.mp3")
        pygame.mixer.music.play()
        pygame.time.set_timer(pygame.USEREVENT, 10000)


app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "static/uploads"
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)


camera_active = False
video_path = None
detect_mode = False  # Flag to activate detection mode
font = cv2.FONT_HERSHEY_SIMPLEX

font_scale = 1  # Kích thước font chữ
color = (0, 255, 0)  # Màu chữ (xanh lá cây)
thickness = 2
count_smoke = 0
camera_source = 0
last_sent_time = 0  # Thời gian lần cuối gửi tin nhắn
DELAY = 10
camera_source = "rtsp://admin:180683xo@192.168.1.2:554/onvif1"

def generate_frames():
    global camera_active, video_path, detect_mode
    global last_sent_time
    global camera_source
    global camera_source
    global media_player
    global snapshot_path
    cap = None

    if camera_active:

        if str(camera_source).isdigit():
            cap = cv2.VideoCapture(camera_source)
        else:
            import vlc
            instance = vlc.Instance()
            media = instance.media_new(camera_source)
            media_player = instance.media_player_new()
            media_player.set_media(media)
            media_player.play()
            snapshot_path = "snapshot1.png"
            media_player.video_take_snapshot(0, snapshot_path, 0, 0)
            time.sleep(2)
    elif video_path:
        cap = cv2.VideoCapture(video_path)

    while True:
        if str(camera_source).isdigit() or camera_active or video_path is not None:
            success, frame = cap.read()
            if not success:
                break
        else:
            media_player.video_take_snapshot(0, snapshot_path, 0, 0)
            frame = cv2.imread(snapshot_path)
            if frame is None:
                break
        image = frame.copy()
        personBoxes = predictPerson(frame)
        for box in personBoxes:
            xmin, ymin, xmax, ymax = box
            cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), (0, 255, 0), 1)
        smokeBoxes = predictSmoke(frame, personBoxes)
        faceBoxes = faceDetector.detect(frame)
        for faceBox in faceBoxes:
            x_min2, y_min2, x_max2, y_max2 = faceBox
            cv2.rectangle(frame, (x_min2, y_min2), (x_max2, y_max2), (0, 255, 0), 1)
        for box, score in smokeBoxes:
            x_min1, y_min1, x_max1, y_max1 = box
            for faceBox in faceBoxes:
                x_min2, y_min2, x_max2, y_max2 = faceBox
                if is_intersect(
                    x_min1, y_min1, x_max1, y_max1, x_min2, y_min2, x_max2, y_max2
                ):
                    cv2.rectangle(
                        frame, (x_min1, y_min1), (x_max1, y_max1), (0, 255, 0), 1
                    )
                    text = f"Hut thuoc la {score}"
                    position = (x_min1, y_min1)
                    cv2.putText(
                        frame, text, position, font, font_scale, color, thickness
                    )
                    current_time = time.time()
                    if current_time - last_sent_time > DELAY:  # Kiểm tra nếu đủ 10 giây
                        last_sent_time = current_time
                        threading.Thread(target=play_canh_bao).start()
                        # Gửi tin nhắn và ảnh lên Telegram
                        threading.Thread(
                            target=send_telegram_message,
                            args=("Phát hiện học sinh hút thuốc",),
                        ).start()
                        threading.Thread(
                            target=send_telegram_photo, args=(image,)
                        ).start()

        _, buffer = cv2.imencode(".jpg", frame)
        frame = buffer.tobytes()

        yield (b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")

    cap.release()


@app.route("/hut-thuoc")
def index():
    return render_template("hut_thuoc.html")


@app.route("/video_feed")
def video_feed():
    return Response(
        generate_frames(), mimetype="multipart/x-mixed-replace; boundary=frame"
    )


@app.route("/control", methods=["POST"])
def control():
    global camera_active, video_path, detect_mode, camera_source

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
        camera_source = None
    elif "video_file" in request.files:
        camera_source = None
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
    app.run(debug=True, port=2222)
