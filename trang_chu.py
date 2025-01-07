import tkinter as tk
from tkinter import messagebox
import subprocess
import webbrowser
import time

class ObjectDetectionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("NGHIÊN CỨU VÀ XÂY DỰNG HỆ THỐNG PHÁT HIỆN BẠO LỰC, HÚT THUỐC VÀ MŨ BẢO HIỂM BẰNG CÔNG NGHỆ DEEP LEARNING")
        self.root.geometry("1280x720")
        self.fullscreen = True
        self.root.attributes('-fullscreen', self.fullscreen)

        # Màu nền chính
        self.bg_color = "#32CD32"  # Xanh lá cây tươi
        self.button_color = "#228B22"  # Xanh lá cây đậm
        self.button_hover_color = "#7CFC00"  # Xanh lá cây sáng

        self.root.configure(bg=self.bg_color)

        # Tiêu đề
        self.label = tk.Label(
            root,
            text="NGHIÊN CỨU VÀ XÂY DỰNG HỆ THỐNG PHÁT HIỆN BẠO LỰC, HÚT THUỐC VÀ MŨ BẢO HIỂM BẰNG CÔNG NGHỆ DEEP LEARNING",
            bg=self.bg_color,
            fg="white",
            font=("Helvetica", 26, "bold"),
            justify=tk.CENTER,
            wraplength=1200,
        )
        self.label.place(relx=0.5, rely=0.12, anchor=tk.CENTER)

        # Khung hiển thị hình ảnh
        self.image_frame = tk.Frame(
            root,
            width=820,
            height=460,
            bg="white",
            highlightbackground="#228B22",
            highlightthickness=2,
        )
        self.image_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        # Hiển thị hình ảnh
        self.display_image()

        # Khung chứa các nút điều khiển
        button_frame = tk.Frame(root, bg=self.bg_color)
        button_frame.place(relx=0.5, rely=0.85, anchor=tk.CENTER)

        # Style cho nút bấm
        button_style = {"bg": self.button_color, "fg": "white", "font": ("Helvetica", 16), "height": 1, "bd": 0}
        button_width = 12

        self.btn_chedo1 = tk.Button(button_frame, text="Bạo lực", width=button_width, **button_style, command=self.chedo1)
        self.btn_chedo1.grid(row=0, column=0, padx=10, pady=5)

        self.btn_chedo2 = tk.Button(button_frame, text="Hút thuốc", width=button_width, **button_style, command=self.chedo2)
        self.btn_chedo2.grid(row=0, column=1, padx=10, pady=5)

        self.btn_chedo3 = tk.Button(button_frame, text="Mũ bảo hiểm", width=button_width, **button_style, command=self.chedo3)
        self.btn_chedo3.grid(row=0, column=2, padx=10, pady=5)

        self.btn_toggle_fullscreen = tk.Button(button_frame, text="Chế độ", width=button_width, **button_style, command=self.toggle_fullscreen)
        self.btn_toggle_fullscreen.grid(row=0, column=3, padx=10, pady=5)

        self.btn_quit = tk.Button(button_frame, text="Thoát", width=button_width, **button_style, command=self.quit_application)
        self.btn_quit.grid(row=0, column=4, padx=10, pady=5)

        # Hiệu ứng hover
        self.create_button_hover_effect(self.btn_chedo1)
        self.create_button_hover_effect(self.btn_chedo2)
        self.create_button_hover_effect(self.btn_chedo3)
        self.create_button_hover_effect(self.btn_toggle_fullscreen)
        self.create_button_hover_effect(self.btn_quit)

    def create_button_hover_effect(self, button):
        def on_enter(e):
            button['bg'] = self.button_hover_color
        def on_leave(e):
            button['bg'] = self.button_color

        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)

    def display_image(self):
        image_path = "anh_giao_dien/concuong02.jpg"
        try:
            from PIL import Image, ImageTk
            image = Image.open(image_path)
            image = image.resize((820, 460), Image.LANCZOS)
            self.image = ImageTk.PhotoImage(image)
            label = tk.Label(self.image_frame, image=self.image, bg="white")
            label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        except FileNotFoundError:
            error_label = tk.Label(
                self.image_frame,
                text="Không tìm thấy ảnh",
                bg="white",
                fg="red",
                font=("Helvetica", 16, "bold")
            )
            error_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

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

    def quit_application(self):
        self.root.quit()

# Chạy ứng dụng
def main():
    root = tk.Tk()
    app = ObjectDetectionApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
