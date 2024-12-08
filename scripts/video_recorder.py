import os
import time
import threading
import requests
import subprocess
import glob
import logging
from pathlib import Path
import json
import platform
import re
import ctypes
import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
from queue import Queue
from screeninfo import get_monitors

script_dir = Path(__file__).resolve().parent
ffmpeg_path = Path('C:\\ffmpeg\\bin\\ffmpeg.exe') if platform.system() == 'Windows' else Path('/usr/bin/ffmpeg')
webhook_url = os.environ.get("DISCORD_WEBHOOK_URL", "https://discord.com/api/webhooks/1246738691519676478/k2sl3zBuq3nQHcbHTg7oZTNW-YZFSSzguShau1-zi3w_tYnIgIO5er4fyUfjZO1Sm5i7")
if not webhook_url:
    raise ValueError("Discord webhook URL'si ayarlanmadı. Lütfen 'DISCORD_WEBHOOK_URL' ortam değişkenini ayarlayın.")
clear_interval = 3600
video_duration = 60
max_file_age = 86400
config_file = script_dir / "config.json"
if config_file.exists():
    with open(config_file, 'r', encoding='utf-8') as f:
        config_data = json.load(f)
else:
    config_data = {}
default_audio_device = config_data.get("audio_device", "Line 1 (Virtual Audio Cable)")
if not ffmpeg_path.exists():
    raise FileNotFoundError(f"FFmpeg bulunamadı: {ffmpeg_path}. Lütfen FFmpeg'in doğru yolda olduğundan emin olun.")
log_queue = Queue()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
logger.addHandler(console_handler)
previous_video_filename = None
last_uploaded_video = None
recording_in_progress = False
last_resolution = None
recording_thread = None
stop_requested = False
app = None
record_start_time = None
next_cleaning_time = None
current_recording_filename = None

def get_screen_resolution():
    system_name = platform.system()
    if system_name == 'Windows':
        user32 = ctypes.windll.user32
        user32.SetProcessDPIAware()
        width = user32.GetSystemMetrics(0)
        height = user32.GetSystemMetrics(1)
        return width, height
    elif system_name == 'Linux':
        try:
            output = subprocess.check_output(['xrandr']).decode('utf-8')
            match = re.search(r'(\d+)x(\d+)\s+\d+\.\d+\*', output)
            if match:
                width = int(match.group(1))
                height = int(match.group(2))
                return width, height
            else:
                return 1920, 1080
        except Exception:
            return 1920, 1080
    else:
        return 1920, 1080

def clean_old_files_now():
    global next_cleaning_time
    logger.info("Eski dosyaları (yaş kontrollü) temizlemeye başlandı.")
    current_time = time.time()
    files_deleted = 0
    for file in glob.glob(str(script_dir / '*.mp4')) + glob.glob(str(script_dir / '*.txt')):
        try:
            file_age = current_time - os.path.getmtime(file)
            if file_age > max_file_age:
                os.remove(file)
                logger.info(f"Silinen eski dosya: {file}")
                files_deleted += 1
        except Exception as e:
            logger.error(f"{file} dosyası silinirken hata oluştu: {e}")
    if files_deleted == 0:
        logger.info("Temizlenecek eski dosya bulunamadı.")
    next_cleaning_time = time.time() + clear_interval

def force_delete_unused_files():
    global current_recording_filename, previous_video_filename
    logger.info("Eski videoları şimdi (manuel) temizleme başlatıldı.")
    files_deleted = 0
    for file in glob.glob(str(script_dir / '*.mp4')) + glob.glob(str(script_dir / '*.txt')):
        if file == str(previous_video_filename) or file == str(current_recording_filename):
            continue
        try:
            os.remove(file)
            logger.info(f"Silinen dosya: {file}")
            files_deleted += 1
        except Exception as e:
            logger.error(f"{file} dosyası silinirken hata oluştu: {e}")
    if files_deleted == 0:
        logger.info("Silinecek kullanılmayan dosya bulunamadı.")

def clear_old_files_loop():
    global stop_requested
    while not stop_requested:
        clean_old_files_now()
        time.sleep(clear_interval)

def list_audio_devices():
    if platform.system() == 'Windows':
        try:
            cmd = [str(ffmpeg_path), '-list_devices', 'true', '-f', 'dshow', '-i', 'dummy']
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            output = result.stderr
            logger.info("FFmpeg cihaz listesi çıktısı:\n" + output)
            devices = []
            for line in output.split('\n'):
                line = line.strip()
                if '(audio)' in line:
                    match = re.search(r'"([^"]+)"', line)
                    if match:
                        devices.append(match.group(1))
            logger.info(f"BULUNAN SES CİHAZLARI: {devices}")
            return devices
        except Exception as e:
            logger.error(f"Ses cihazları listelenemedi: {e}")
            return []
    else:
        return []

def categorize_audio_devices(devices):
    input_keywords = ["Microphone", "Line"]
    output_keywords = ["Out"]
    input_devs = []
    output_devs = []
    for d in devices:
        if any(kw in d for kw in input_keywords):
            input_devs.append(d)
        elif any(kw in d for kw in output_keywords):
            output_devs.append(d)
        else:
            input_devs.append(d)
    return input_devs, output_devs

def record_screen(duration, output_file, input_device, output_device, monitor):
    global recording_in_progress, last_resolution, record_start_time, current_recording_filename
    full_width = monitor.width
    full_height = monitor.height
    offset_x = monitor.x
    offset_y = monitor.y
    last_resolution = (full_width, full_height)
    scale_filter = "scale=1280:720"
    recording_in_progress = True
    record_start_time = time.time()
    current_recording_filename = output_file
    base_cmd = [
        str(ffmpeg_path), '-y', '-f', 'gdigrab',
        '-framerate', '15',
        '-offset_x', str(offset_x), '-offset_y', str(offset_y),
        '-video_size', f'{full_width}x{full_height}',
        '-i', 'desktop'
    ]
    audio_inputs = []
    if input_device and input_device != "Cihaz bulunamadı":
        audio_inputs += ['-f', 'dshow', '-i', f'audio={input_device}']
    if output_device and output_device != "Cihaz bulunamadı":
        audio_inputs += ['-f', 'dshow', '-i', f'audio={output_device}']
    audio_filter = []
    map_options = []
    if input_device and input_device != "Cihaz bulunamadı" and output_device and output_device != "Cihaz bulunamadı":
        audio_filter = ['-filter_complex', '[1:a][2:a]amix=inputs=2[aout]', '-map', '0:v', '-map', '[aout]']
    elif input_device and input_device != "Cihaz bulunamadı" and (not output_device or output_device == "Cihaz bulunamadı"):
        map_options = ['-map', '0:v', '-map', '1:a']
    elif output_device and output_device != "Cihaz bulunamadı" and (not input_device or input_device == "Cihaz bulunamadı"):
        map_options = ['-map', '0:v', '-map', '1:a']
    else:
        map_options = ['-map', '0:v']
    common_opts = [
        '-t', str(duration),
        '-vf', scale_filter,
        '-c:v', 'libx264', '-preset', 'fast', '-b:v', '2000k',
        '-c:a', 'aac', '-b:a', '128k',
        '-pix_fmt', 'yuv420p',
        output_file
    ]
    command = base_cmd + audio_inputs
    if audio_filter:
        command += audio_filter + common_opts
    else:
        command += map_options + common_opts
    try:
        logger.info(f"Kaydediliyor: {output_file}")
        logger.info("FFmpeg Komutu: " + " ".join(command))
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            logger.error(f"FFmpeg komutu başarısız oldu: {result.stderr}")
        else:
            logger.info(f"Kaydedildi: {output_file}")
    except FileNotFoundError:
        logger.error("FFmpeg bulunamadı. Lütfen FFmpeg'in kurulu ve PATH'de olduğundan emin olun.")
    except subprocess.CalledProcessError as e:
        logger.error(f"FFmpeg komutu başarısız oldu: {str(e)}")
    recording_in_progress = False
    record_start_time = None
    current_recording_filename = None

def send_to_discord(file_path, webhook_url, retries=3, backoff_factor=2):
    global last_uploaded_video
    attempt = 0
    while attempt < retries and not stop_requested:
        try:
            with open(file_path, 'rb') as file:
                files = {'file': (os.path.basename(file_path), file, 'video/mp4')}
                response = requests.post(webhook_url, files=files)
                response.raise_for_status()
            logger.info("Yükleme başarılı.")
            delete_file(file_path)
            last_uploaded_video = os.path.basename(file_path)
            return True
        except requests.RequestException as e:
            attempt += 1
            logger.error(f"Discord'a dosya gönderme başarısız (deneme {attempt}/{retries}): {e}")
            time.sleep(backoff_factor ** attempt)
    logger.error(f"Dosya Discord'a gönderilemedi: {file_path}")
    return False

def delete_file(file_path):
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"Dosya silindi: {file_path}")
    except Exception as e:
        logger.error(f"Dosya silinirken hata oluştu {file_path}: {e}")

def capture_cycle():
    global previous_video_filename, stop_requested, next_cleaning_time
    next_cleaning_time = time.time() + clear_interval
    cleaner_thread = threading.Thread(target=clear_old_files_loop, daemon=True)
    cleaner_thread.start()
    while not stop_requested:
        video_filename = script_dir / f"screenrecord-{int(time.time())}.mp4"
        selected_monitor_index = app.monitor_combo.current()
        monitor = app.monitors_info[selected_monitor_index]
        input_device = app.input_audio_device_var.get()
        output_device = app.output_audio_device_var.get()
        record_thread = threading.Thread(target=record_screen, args=(video_duration, str(video_filename), input_device, output_device, monitor))
        record_thread.start()
        if previous_video_filename:
            send_to_discord(str(previous_video_filename), webhook_url)
        record_thread.join()
        previous_video_filename = video_filename

class TkinterTextHandler(logging.Handler):
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget
    def emit(self, record):
        msg = self.format(record) + '\n'
        self.text_widget.after(0, self.text_widget.insert, tk.END, msg)
        self.text_widget.after(0, self.text_widget.see, tk.END)

class StatusUI:
    def __init__(self, master):
        self.master = master
        master.title("Ekran Kaydı ve Ayarlar")
        self.monitors_info = get_monitors()
        self.selected_monitor = tk.StringVar()
        self.settings_frame = tk.LabelFrame(master, text="Ayarlar", padx=10, pady=10)
        self.settings_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        monitor_label = tk.Label(self.settings_frame, text="Kayıt Yapılacak Monitör Seçimi:")
        monitor_label.pack(anchor="w")
        monitor_names = [f"Monitör {i+1}: {m.width}x{m.height} @{m.x},{m.y}" for i,m in enumerate(self.monitors_info)]
        self.monitor_combo = ttk.Combobox(self.settings_frame, values=monitor_names, textvariable=self.selected_monitor, state="readonly")
        self.monitor_combo.current(0)
        self.monitor_combo.pack(fill=tk.X, pady=5)
        tk.Label(self.settings_frame, text="Ses Cihazları:").pack(anchor="w")
        all_devices = list_audio_devices()
        if not all_devices:
            all_devices = ["Cihaz bulunamadı"]
        input_devs, output_devs = categorize_audio_devices(all_devices)
        if not input_devs:
            input_devs = ["Cihaz bulunamadı"]
        if not output_devs:
            output_devs = ["Cihaz bulunamadı"]
        self.input_audio_device_var = tk.StringVar(value=input_devs[0])
        tk.Label(self.settings_frame, text="Input Ses Cihazı (Mikrofon):").pack(anchor="w")
        self.input_audio_combo = ttk.Combobox(self.settings_frame, values=input_devs, textvariable=self.input_audio_device_var, state="readonly")
        self.input_audio_combo.current(0)
        self.input_audio_combo.pack(fill=tk.X, pady=5)
        self.output_audio_device_var = tk.StringVar(value=output_devs[0])
        tk.Label(self.settings_frame, text="Output Ses Cihazı (Sistem Sesi):").pack(anchor="w")
        self.output_audio_combo = ttk.Combobox(self.settings_frame, values=output_devs, textvariable=self.output_audio_device_var, state="readonly")
        self.output_audio_combo.current(0)
        self.output_audio_combo.pack(fill=tk.X, pady=5)
        self.refresh_audio_button = ttk.Button(self.settings_frame, text="Ses Cihazlarını Yenile", command=self.refresh_audio_devices)
        self.refresh_audio_button.pack(fill=tk.X, pady=5)
        tk.Label(self.settings_frame, text=f"Webhook URL: {webhook_url}", anchor="w").pack(fill=tk.X)
        tk.Label(self.settings_frame, text=f"FFmpeg Path: {ffmpeg_path}", anchor="w").pack(fill=tk.X, pady=5)
        controls_frame = tk.Frame(master)
        controls_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.start_button = ttk.Button(controls_frame, text="Start", command=self.start_recording)
        self.start_button.pack(side=tk.LEFT, padx=5)
        self.stop_button = ttk.Button(controls_frame, text="Stop", command=self.stop_recording)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        status_frame = tk.LabelFrame(master, text="Durum Bilgileri", padx=10, pady=10)
        status_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.label_resolution = tk.Label(status_frame, text="Ekran Çözünürlüğü: Bilinmiyor")
        self.label_resolution.pack(anchor="w")
        self.label_recording_status = tk.Label(status_frame, text="Kayıt Durumu: Bekleniyor...")
        self.label_recording_status.pack(anchor="w")
        self.label_record_time = tk.Label(status_frame, text="Kayıt Süresi: ---")
        self.label_record_time.pack(anchor="w")
        self.label_upload_info = tk.Label(status_frame, text="Upload Durumu: Henüz yok")
        self.label_upload_info.pack(anchor="w")
        self.label_last_upload = tk.Label(status_frame, text="Son Yüklenen Video: Yok")
        self.label_last_upload.pack(anchor="w")
        self.label_cleaning_info = tk.Label(status_frame, text=f"Eski dosyalar {clear_interval} sn'de bir temizlenir.")
        self.label_cleaning_info.pack(anchor="w")
        self.label_next_cleaning = tk.Label(status_frame, text="Bir sonraki otomatik temizlik: Henüz bilinmiyor")
        self.label_next_cleaning.pack(anchor="w")
        logs_frame = tk.LabelFrame(master, text="Loglar", padx=10, pady=10)
        logs_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.log_text = ScrolledText(logs_frame, wrap=tk.WORD, height=10)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        logs_buttons_frame = tk.Frame(logs_frame)
        logs_buttons_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=5, pady=5)
        self.clear_logs_button = ttk.Button(logs_buttons_frame, text="Logları Temizle", command=self.clear_logs)
        self.clear_logs_button.pack(pady=5, fill=tk.X)
        self.clean_old_videos_button = ttk.Button(logs_buttons_frame, text="Eski Videoları Şimdi Temizle", command=self.clean_old_videos_now)
        self.clean_old_videos_button.pack(pady=5, fill=tk.X)
        self.handler = TkinterTextHandler(self.log_text)
        self.handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logger.addHandler(self.handler)
        self.update_ui()

    def refresh_audio_devices(self):
        all_devices = list_audio_devices()
        if not all_devices:
            all_devices = ["Cihaz bulunamadı"]
        input_devs, output_devs = categorize_audio_devices(all_devices)
        if not input_devs:
            input_devs = ["Cihaz bulunamadı"]
        if not output_devs:
            output_devs = ["Cihaz bulunamadı"]
        self.input_audio_combo['values'] = input_devs
        self.output_audio_combo['values'] = output_devs
        self.input_audio_combo.current(0)
        self.output_audio_combo.current(0)

    def start_recording(self):
        global stop_requested, recording_thread
        stop_requested = False
        if not recording_in_progress and (recording_thread is None or not recording_thread.is_alive()):
            recording_thread = threading.Thread(target=capture_cycle, daemon=True)
            recording_thread.start()

    def stop_recording(self):
        global stop_requested
        stop_requested = True

    def clear_logs(self):
        self.log_text.delete('1.0', tk.END)

    def clean_old_videos_now(self):
        force_delete_unused_files()

    def update_ui(self):
        global recording_in_progress, last_uploaded_video, last_resolution, record_start_time, previous_video_filename, video_duration, next_cleaning_time
        if last_resolution:
            self.label_resolution.config(text=f"Ekran Çözünürlüğü: {last_resolution[0]}x{last_resolution[1]}")
        else:
            self.label_resolution.config(text="Ekran Çözünürlüğü: Bilinmiyor")
        if recording_in_progress:
            self.label_recording_status.config(text="Kayıt Durumu: Kayıt Yapılıyor...")
        else:
            self.label_recording_status.config(text="Kayıt Durumu: Bekleniyor...")
        if recording_in_progress and record_start_time is not None:
            elapsed = int(time.time() - record_start_time)
            remaining = video_duration - elapsed
            self.label_record_time.config(text=f"Kayıt Süresi: {elapsed} sn geçti, {remaining} sn kaldı.")
        else:
            self.label_record_time.config(text="Kayıt Süresi: ---")
        if previous_video_filename and recording_in_progress and record_start_time is not None:
            elapsed = int(time.time() - record_start_time)
            remaining = video_duration - elapsed
            self.label_upload_info.config(text=f"Upload {remaining} sn sonra başlayacak (kayıt bittiğinde).")
        elif previous_video_filename and not recording_in_progress:
            self.label_upload_info.config(text="Upload sıradaki kaydın bitiminde yapılacak.")
        else:
            self.label_upload_info.config(text="Upload Durumu: Beklenmiyor")
        if last_uploaded_video:
            self.label_last_upload.config(text=f"Son Yüklenen Video: {last_uploaded_video}")
        else:
            self.label_last_upload.config(text="Son Yüklenen Video: Yok")
        if next_cleaning_time:
            remaining_clean = int(next_cleaning_time - time.time())
            if remaining_clean < 0:
                remaining_clean = 0
            self.label_next_cleaning.config(text=f"Bir sonraki otomatik temizlik {remaining_clean} sn sonra.")
        else:
            self.label_next_cleaning.config(text="Bir sonraki otomatik temizlik: Henüz bilinmiyor")
        self.master.after(1000, self.update_ui)

def main():
    global app
    root = tk.Tk()
    app = StatusUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
