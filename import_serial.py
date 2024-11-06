import serial
import serial.tools.list_ports
import os
import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import time
from PIL import Image, ImageDraw, ImageTk  # Pillow modülünü içeri aktarıyoruz
import pystray

# settings.txt dosyasının yolu (programın bulunduğu dizinde olacak şekilde ayarlandı)
settings_file_path = os.path.join(os.path.dirname(__file__), "settings.txt")

# Maple Serial cihazını bul ve bağlan
ser = None  # Global değişkeni burada başlatıyoruz

def find_maple_serial_port():
    global ser  # 'ser' değişkenini global olarak kullanacağımızı belirtiyoruz
    ports = serial.tools.list_ports.comports()
    for port in ports:
        if "Maple Serial" in port.description:
            ser = serial.Serial(port.device, 9600)
            return port.device
    return None

# Uygulama dosyalarını tutacak bir sözlük
app_mapping = {0: '', 1: ''}

# settings.txt dosyasından uygulama yollarını oku
def load_app_paths():
    if os.path.exists(settings_file_path):
        with open(settings_file_path, 'r') as f:
            lines = f.readlines()
            for i, line in enumerate(lines):
                app_mapping[i] = line.strip()

# Uygulama yollarını settings.txt dosyasına kaydet
def save_app_paths():
    with open(settings_file_path, 'w') as f:
        for i in range(len(app_mapping)):
            f.write(app_mapping[i] + '\n')
    messagebox.showinfo("Bilgi", "Ayarlar kaydedildi.")

# Seri port verisi kontrolü ve buton işlemleri
def check_serial_data():
    while True:
        if ser and ser.in_waiting > 0:
            data = ser.readline().decode('utf-8').strip()
            if data == '0':
                run_app(0)
            elif data == '1':
                run_app(1)
        time.sleep(0.1)

# Sistem tepsisi simgesi için
def create_image(width, height, color1, color2):
    image = Image.new('RGB', (width, height), color1)
    dc = ImageDraw.Draw(image)
    dc.rectangle(
        (width // 2, 0, width, height // 2),
        fill=color2)
    dc.rectangle(
        (0, height // 2, width // 2, height),
        fill=color2)
    return image

# Tepsi simgesini oluştur ve göster
def setup_tray_icon():
    icon_image = create_image(64, 64, 'blue', 'white')

    # Menü seçenekleri (ayarları aç ve çıkış)
    menu = pystray.Menu(
        pystray.MenuItem("Ayarları Aç", show_app),
        pystray.MenuItem("Çıkış", on_exit)
    )

    icon = pystray.Icon("yeniliko_icon", icon_image, "Yeniliko", menu)
    icon.run()

# Ayarları göster (tepsiden çağrılır)
def show_app(icon=None, item=None):
    root.deiconify()  # Pencereyi tekrar görünür hale getir

# Çıkış yap (tepsiden çağrılır)
def on_exit(icon, item):
    icon.stop()
    root.quit()

# Uygulama seçme fonksiyonu
def select_app(button_num):
    file_path = filedialog.askopenfilename(filetypes=[("Executable Files", "*.exe")])
    if file_path:
        app_mapping[button_num] = file_path
        buttons[button_num].config(text=f"{button_num + 1}. Tuş: {os.path.basename(file_path)}")

# Uygulama başlatma fonksiyonu
def run_app(button_num):
    app_path = app_mapping.get(button_num)
    if app_path:
        os.startfile(app_path)

# GUI ayarları
root = tk.Tk()
root.title("Yeniliko.com")
root.geometry("400x350")
root.config(bg="#f0f0f0")

# Logo eklemek için (Logonun yolunu güncelle)
logo_image_path = "C:/Users/Yunus emre/Desktop/yeniliko v0.2/logo.png"  # Logo dosyanızın tam yolu burada
logo_image = Image.open(logo_image_path)
logo_image = logo_image.resize((50, 50))  # Logoyu uygun boyutlandır
logo_photo = ImageTk.PhotoImage(logo_image)

# Sağ üst köşeye logoyu yerleştirecek label
logo_label = tk.Label(root, image=logo_photo, bg="#f0f0f0")
logo_label.place(relx=1.0, rely=0.0, anchor="ne")  # Sağ üst köşe (x=1, y=0)

title_label = tk.Label(root, text="Yeniliko", font=("Helvetica", 18, "bold"), bg="#f0f0f0", fg="#333")
title_label.pack(pady=20)

# Butonlar ve işlevler
buttons_frame = tk.Frame(root, bg="#f0f0f0")
buttons_frame.pack(pady=10)
buttons = [
    tk.Button(buttons_frame, text="1. Tuş: Not Set", width=30, height=2, font=("Arial", 12), bg="#4CAF50", fg="white", command=lambda: select_app(0)),
    tk.Button(buttons_frame, text="2. Tuş: Not Set", width=30, height=2, font=("Arial", 12), bg="#2196F3", fg="white", command=lambda: select_app(1))
]

for button in buttons:
    button.pack(pady=5)

# Kaydet butonu
save_button = tk.Button(root, text="Kaydet", width=30, height=2, font=("Arial", 12), bg="#FF9800", fg="white", command=save_app_paths)
save_button.pack(pady=5)

# Uygulama yollarını yükle ve buton metinlerini güncelle
load_app_paths()
for i, button in enumerate(buttons):
    if app_mapping[i]:
        button.config(text=f"{i + 1}. Tuş: {os.path.basename(app_mapping[i])}")

# Seri port kontrolünü başlatacak arka plan thread’i
maple_port = find_maple_serial_port()  # maple_port değişkenini burada tanımlıyoruz
if maple_port is not None:
    serial_thread = threading.Thread(target=check_serial_data, daemon=True)
    serial_thread.start()

    # Tepsi simgesini çalıştıracak thread
    tray_thread = threading.Thread(target=setup_tray_icon, daemon=True)
    tray_thread.start()
else:
    messagebox.showerror("Cihazı Bulamadık", "Yan Klavyeyi Bulamadık Lütfen USB Port değişip Tekrar Deneyiniz.")
    root.quit()

root.protocol("WM_DELETE_WINDOW", lambda: root.withdraw())  # Pencereyi gizler, çıkmaz
root.mainloop()
