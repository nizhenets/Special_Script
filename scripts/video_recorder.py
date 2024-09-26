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

# Configuration
script_dir = Path(__file__).resolve().parent
ffmpeg_path = Path('C:\\ffmpeg\\bin\\ffmpeg.exe') if platform.system() == 'Windows' else Path('/usr/bin/ffmpeg')
webhook_url = os.getenv('DISCORD_WEBHOOK_URL')  # Webhook URL'sini ortam değişkeninden al
clear_interval = 3600  # Clear old files every hour
video_duration = 60  # Duration of each screen recording
max_file_age = 86400  # Maximum file age in seconds (e.g., 1 day)

# Validate configurations
if not ffmpeg_path.exists():
    raise FileNotFoundError(f"FFmpeg bulunamadı: {ffmpeg_path}. Lütfen FFmpeg'in doğru yolda olduğundan emin olun.")

if not webhook_url:
    raise ValueError("Discord webhook URL'si ayarlanmadı. Lütfen 'DISCORD_WEBHOOK_URL' ortam değişkenini ayarlayın.")

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

previous_video_filename = None

def get_screen_resolution():
    # Return fixed resolution of 1280x720 for performance reasons
    return "1280x720"

def clear_old_files():
    while True:
        logger.info("Eski dosyaları temizlemeye başlandı.")
        current_time = time.time()
        for file in glob.glob(str(script_dir / '*.mp4')) + glob.glob(str(script_dir / '*.txt')):
            try:
                file_age = current_time - os.path.getmtime(file)
                if file_age > max_file_age:
                    os.remove(file)
                    logger.info(f"Silinen eski dosya: {file}")
            except Exception as e:
                logger.error(f"{file} dosyası silinirken hata oluştu: {e}")
        time.sleep(clear_interval)

def record_screen(duration, output_file):
    resolution = get_screen_resolution()
    audio_device = "Line 1 (Virtual Audio Cable)"  # Kullanıcıya uygun ses cihazını ayarlayın veya ortam değişkeni kullanın

    command = [
        str(ffmpeg_path), '-y', '-f', 'gdigrab' if platform.system() == 'Windows' else 'x11grab',
        '-framerate', '15', '-i', 'desktop',
        '-f', 'dshow' if platform.system() == 'Windows' else 'pulse', '-i', f'audio={audio_device}',
        '-s', resolution, '-t', str(duration),
        '-c:v', 'libx264', '-preset', 'fast', '-b:v', '2000k',
        '-c:a', 'aac', '-b:a', '128k',
        '-pix_fmt', 'yuv420p',
        output_file
    ]

    try:
        logger.info(f"Kaydediliyor: {output_file}")
        subprocess.run(command, capture_output=True, text=True, check=True)
        logger.info(f"Kaydedildi: {output_file}")
    except FileNotFoundError:
        logger.error("FFmpeg bulunamadı. Lütfen FFmpeg'in kurulu ve PATH'de olduğundan emin olun.")
    except subprocess.CalledProcessError as e:
        logger.error(f"FFmpeg komutu başarısız oldu: {e.stderr}")

def send_to_discord(file_path, webhook_url, retries=3, backoff_factor=2):
    attempt = 0
    while attempt < retries:
        try:
            with open(file_path, 'rb') as file:
                files = {'file': (os.path.basename(file_path), file, 'video/mp4')}
                response = requests.post(webhook_url, files=files)
                response.raise_for_status()
            logger.info("Yükleme başarılı.")
            delete_file(file_path)
            return True
        except requests.RequestException as e:
            attempt += 1
            logger.error(f"Discord'a dosya gönderme başarısız (deneme {attempt}/{retries}): {e}")
            time.sleep(backoff_factor ** attempt)  # Üssel geri çekilme
    logger.error(f"Dosya Discord'a gönderilemedi: {file_path}")
    return False

def delete_file(file_path):
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"Dosya silindi: {file_path}")
    except Exception as e:
        logger.error(f"Dosya silinirken hata oluştu {file_path}: {e}")

def capture_and_send_videos():
    global previous_video_filename
    while True:
        video_filename = script_dir / f"screenrecord-{int(time.time())}.mp4"
        
        # Kaydı başlat
        record_thread = threading.Thread(target=record_screen, args=(video_duration, str(video_filename)))
        record_thread.start()
        
        # Önceki videoyu yükle
        if previous_video_filename:
            upload_thread = threading.Thread(target=send_to_discord, args=(str(previous_video_filename), webhook_url))
            upload_thread.start()
        
        # Kaydın bitmesini bekle
        record_thread.join()
        
        # Bir sonraki döngü için önceki videoyu ayarla
        previous_video_filename = video_filename

def main():
    # Arka plan iş parçacıklarını başlat
    threading.Thread(target=clear_old_files, daemon=True).start()
    threading.Thread(target=capture_and_send_videos, daemon=True).start()
    
    # Ana iş parçacığını canlı tut
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Kullanıcı tarafından sonlandırıldı.")

if __name__ == "__main__":
    main()
