import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import subprocess
import webbrowser
import time

class ObjectDetectionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("HỆ THỐNG TÍCH HỢP CẢNH BÁO BẠO LỰC HỌC ĐƯỜNG VÀ HÀNH VI HÚT THUỐC LÁ CỦA HỌC SINH")
        self.root.geometry("1280x720")
        self.fullscreen = True
        self.root.attributes('-fullscreen', self.fullscreen)  # Fullscreen

        # Load logo và background
        self.logo = Image.open("anh_giao_dien/logo.jpg")
        self.logo = self.logo.resize((100, 100), Image.LANCZOS)
        self.logo = ImageTk.PhotoImage(self.logo)

        self.background = Image.open("anh_giao_dien/giao dien.jpg")
        self.background = self.background.resize((1280, 720), Image.LANCZOS)
        self.background = ImageTk.PhotoImage(self.background)

        self.bg_label = tk.Label(self.root, image=self.background)
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        self.logo_label = tk.Label(self.root, image=self.logo, bg='white')
        self.logo_label.place(x=10, y=10)

        self.video_source = None

        self.canvas_width = 720
        self.canvas_height = 360

        # Tạo một canvas để hiển thị các khung hình video với kích thước cố định và khung màu trong suốt
        self.canvas_frame = tk.Frame(root, width=self.canvas_width + 20, height=self.canvas_height + 20, bg="white")
        self.canvas_frame.pack_propagate(0)  # Ngăn khung không thay đổi kích thước theo nội dung
        self.canvas_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        self.canvas = tk.Canvas(self.canvas_frame, width=self.canvas_width, height=self.canvas_height, bg="#3498DB", highlightthickness=0)  # Sử dụng màu xanh nước biển
        self.canvas.pack()

        # Thay đổi phần tiêu đề
        self.label = tk.Label(root, 
                            text="HỆ THỐNG TÍCH HỢP CẢNH BÁO BẠO LỰC HỌC ĐƯỜNG, HÚT THUÔC, HÀNH VI HÚT THUỐC LÁ CỦA HỌC SINH", 
                            bg="white", 
                            fg="blue", 
                            font=("Helvetica", 20, "bold"), 
                            justify=tk.CENTER,  # Căn giữa nội dung
                            wraplength=800)  # Đặt chiều rộng để xuống dòng
        self.label.place(relx=0.5, rely=0.15, anchor=tk.CENTER)  # Căn giữa



        # Tạo các nút điều khiển trong khung riêng để căn giữa
        button_frame = tk.Frame(root, bg="white")
        button_frame.place(relx=0.5, rely=0.85, anchor=tk.CENTER)

        button_style = {"bg": "white", "fg": "#C0392B", "font": ("Helvetica", 16), "height": 1, "anchor": "center", "bd": 0}  # Sử dụng màu đỏ đậm
        button_width = 10

        self.btn_chedo1 = tk.Button(button_frame, text="Bạo lực", width=button_width, **button_style, command=self.chedo1)
        self.btn_chedo1.grid(row=0, column=0, padx=5, pady=5)

        self.btn_chedo2 = tk.Button(button_frame, text="Hút thuốc", width=button_width, **button_style, command=self.chedo2)
        self.btn_chedo2.grid(row=0, column=1, padx=5, pady=5)

        self.btn_chedo3 = tk.Button(button_frame, text="Mũ bảo hiểm", width=button_width, **button_style, command=self.chedo3)
        self.btn_chedo3.grid(row=0, column=2, padx=5, pady=5)

        self.btn_toggle_fullscreen = tk.Button(button_frame, text="Windows", width=button_width, **button_style, command=self.toggle_fullscreen)
        self.btn_toggle_fullscreen.grid(row=0, column=4, padx=5, pady=5)

        self.btn_quit = tk.Button(button_frame, text="Exit", width=button_width, **button_style, command=self.quit_application)
        self.btn_quit.grid(row=0, column=5, padx=5, pady=5)

        # Thiết lập hiệu ứng khi rê chuột qua các nút button
        self.create_button_hover_effect(self.btn_chedo1)
        self.create_button_hover_effect(self.btn_chedo2)
        self.create_button_hover_effect(self.btn_chedo3)
        self.create_button_hover_effect(self.btn_toggle_fullscreen)
        self.create_button_hover_effect(self.btn_quit)

        # Thiết lập callback chuột để chọn các điểm
        self.canvas.bind("<Button-1>", self.mouse_callback)
        self.canvas.bind("<Button-3>", self.clear_polygon)  # Thêm sự kiện chuột phải

        # Hiển thị hình ảnh đẹp trên canvas
        self.display_image()

    def create_button_hover_effect(self, button):
        def on_enter(e):
            button['bg'] = '#E74C3C'  # Màu đỏ nhạt khi rê chuột
            button['fg'] = 'white'

        def on_leave(e):
            button['bg'] = 'white'
            button['fg'] = '#C0392B'  # Màu đỏ đậm

        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)

    def display_image(self):
        image_path = "anh_giao_dien/dinh01.jpg"  # Thay bằng đường dẫn tới hình ảnh đẹp của bạn
        image = Image.open(image_path)
        image = image.resize((self.canvas_width, self.canvas_height), Image.LANCZOS)
        self.image = ImageTk.PhotoImage(image)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.image)

    def chedo1(self):
        subprocess.Popen(["python", "bao_luc.py"])
        time.sleep(6)
        webbrowser.open('http://127.0.0.1:1111/bao-luc')

    def chedo2(self):
        subprocess.Popen(["python", "hut_thuoc.py"])
        time.sleep(6)
        webbrowser.open('http://127.0.0.1:2222/hut-thuoc')

    def chedo3(self):
        subprocess.Popen(["python", "mu_bao_hiem.py"])
        time.sleep(6)
        webbrowser.open('http://127.0.0.1:3333/mu-bao-hiem')


    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        self.root.attributes('-fullscreen', self.fullscreen)
        if not self.fullscreen:
            self.root.geometry("1280x720")
        else:
            self.root.attributes('-fullscreen', True)

    def mouse_callback(self, event):
        pass

    def clear_polygon(self, event):
        pass

    def quit_application(self):
        self.root.quit()

def main():
    root = tk.Tk()
    app = ObjectDetectionApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
