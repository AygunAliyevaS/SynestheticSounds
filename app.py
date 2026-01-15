import os
import time
import base64
import logging
from io import BytesIO
import numpy as np
from scipy.io.wavfile import write as write_wav
from scipy import signal
from PIL import Image
from flask import Flask, request, render_template, jsonify, send_from_directory, session, redirect, url_for
from colorsys import rgb_to_hsv
from dotenv import load_dotenv
import msal
import requests
from flask_session import Session
from datetime import datetime
import pyodbc
import uuid
import string
import random
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


load_dotenv()
logger = logging.getLogger(__name__)


def send_user_confirmation(user_email: str, short_id: str, category: str, message: str) -> bool:
    """
    Send confirmation email via Gmail SMTP.
    The SportyBet-styled HTML template is unchanged.
    """
    # ---------- Gmail SMTP (hard-coded for testing) ----------
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT   = 587
    SMTP_USER   = "adamsamal28@gmail.com"          # your Gmail address
    SMTP_PASS   = "pyfmcdsquihyeemc"              # 16-char App Password
    SENDER_NAME = "Synesthetica Support"

    # Quick sanity check – if any of the hard-coded values are empty the function will fail early
    if not all([SMTP_SERVER, SMTP_USER, SMTP_PASS]):
        logger.error("Missing Gmail SMTP credentials")
        return False

    # ---------- Email Content (exactly the same as before) ----------
    subject = f"Ticket #{short_id} - We've Got You Covered!"

    plain_body = f"""We have received your report ticket number {short_id}. Our team will be with you shortly.
Ticket Details:
- ID: {short_id}
- Category: {category}
- Status: Open
Open Chat: https://synes.azurewebsites.net/support/{short_id}
Best regards,
{SENDER_NAME}
aygunaliyeva@anas.az
"""

    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{ font-family: 'Arial', sans-serif; margin: 0; padding: 0; background-color: #f4f4f4; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; background-color: #fff; }}
            .header {{ background: linear-gradient(135deg, #00C851, #00a651); padding: 20px; text-align: center; color: white; }}
            .header h1 {{ margin: 0; font-size: 28px; font-weight: bold; }}
            .header p {{ margin: 5px 0 0; font-size: 14px; opacity: 0.9; }}
            .content {{ padding: 30px 20px; }}
            .ticket-card {{ background: #fff; border: 2px solid #00C851; border-radius: 10px; padding: 20px; margin: 20px 0; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }}
            .ticket-card h2 {{ color: #00C851; margin-top: 0; font-size: 22px; display: flex; align-items: center; }}
            .ticket-card h2::before {{ content: 'Ticket'; margin-right: 10px; }}
            .ticket-details {{ list-style: none; padding: 0; }}
            .ticket-details li {{ padding: 8px 0; border-bottom: 1px solid #eee; display: flex; justify-content: space-between; }}
            .ticket-details li:last-child {{ border-bottom: none; }}
            .label {{ font-weight: bold; color: #FF5722; }}
            .value {{ color: #333; }}
            .cta {{ text-align: center; margin: 30px 0; }}
            .cta-button {{ background: #00C851; color: white; padding: 15px 30px; text-decoration: none; border-radius: 50px; font-weight: bold; font-size: 16px; display: inline-block; box-shadow: 0 4px 8px rgba(0,200,81,0.3); transition: background 0.3s; }}
            .cta-button:hover {{ background: #00a651; }}
            .footer {{ background: #333; color: white; padding: 20px; text-align: center; font-size: 12px; }}
            .footer a {{ color: #00C851; text-decoration: none; }}
            @media (max-width: 600px) {{ .content {{ padding: 20px 15px; }} .header h1 {{ font-size: 24px; }} }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Synesthetica Support</h1>
                <p>Turning Your Support Into Victory!</p>
            </div>
            <div class="content">
                <div class="ticket-card">
                    <h2>Ticket Confirmation</h2>
                    <p style="font-size: 16px; line-height: 1.5; margin-bottom: 20px;">
                        We have received your report ticket number <strong>{short_id}</strong>. Our team will be with you shortly.
                    </p>
                    <ul class="ticket-details">
                        <li><span class="label">Ticket ID:</span> <span class="value"><strong>{short_id}</strong></span></li>
                        <li><span class="label">Category:</span> <span class="value">{category}</span></li>
                        <li><span class="label">Status:</span> <span class="value" style="color: #00C851; font-weight: bold;">Open &amp; Active</span></li>
                    </ul>
                </div>
                <div class="cta">
                    <a href="https://synes.azurewebsites.net/support/{short_id}" class="cta-button">Open Chat Now</a>
                </div>
            </div>
            <div class="footer">
                <p>Best regards,<br><strong>{SENDER_NAME}</strong></p>
                <p><a href="mailto:aygunaliyeva@anas.az">aygunaliyeva@anas.az</a> | Questions? Reply to this email.</p>
                <p style="font-size: 10px; opacity: 0.8;">&copy; 2025 Synesthetica. All rights reserved. Support messages are confidential.</p>
            </div>
        </div>
    </body>
    </html>
    """

    # ---------- Compose & Send ----------
    msg = MIMEMultipart("alternative")
    msg["From"] = f"{SENDER_NAME} <{SMTP_USER}>"
    msg["To"]   = user_email
    msg["Subject"] = subject

    msg.attach(MIMEText(plain_body, "plain"))
    msg.attach(MIMEText(html_body, "html"))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)
        logger.info(f"Confirmation email sent to {user_email} (ticket {short_id})")
        return True
    except smtplib.SMTPAuthenticationError as e:
        logger.error(f"Gmail auth failed: {e}")
        logger.error("Double-check the Gmail address & 16-char App Password")
        return False
    except smtplib.SMTPRecipientsRefused:
        logger.error(f"Recipient refused: {user_email}")
        return False
    except Exception as e:
        logger.error(f"Email failed: {type(e).__name__}: {e}")
        return False


def _ensure_welcome_message(chat: list) -> list:
    """
    Guarantees that the first entry in `chat` is the support‑team welcome.
    If the list is empty or the first entry is not the welcome, prepend it.
    """
    WELCOME = {
        "sender": "support",
        "text": "Welcome to support! How can we help you today?",
        "timestamp": None  # will be filled by the client or left null
    }
    if not chat or chat[0].get("sender") != "support":
        chat.insert(0, WELCOME)
    return chat

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

app = Flask(__name__, static_folder='static')

# Session Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', os.urandom(24).hex())
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_FILE_DIR'] = os.getenv('SESSION_FILE_DIR', '/home/site/wwwroot/sessions')  # Azure-friendly path
app.config['SESSION_COOKIE_SECURE'] = True  # Ensure cookies are sent over HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True  # Prevent JavaScript access to cookies
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # Mitigate CSRF

# SQL Server Database Configuration
app.config['DB_SERVER'] = os.getenv('DB_SERVER')
app.config['DB_NAME'] = os.getenv('DB_NAME')
app.config['DB_USER'] = os.getenv('DB_USER')
app.config['DB_PASSWORD'] = os.getenv('DB_PASSWORD')
app.config['DB_DRIVER'] = os.getenv('DB_DRIVER', 'ODBC Driver 17 for SQL Server')


# Subscription and Billing Configuration
FREE_SUBMISSION_LIMIT = 10
ADDITIONAL_SUBMISSION_COST = 0.01  # $0.01 per additional submission
SUBSCRIBE_URL = os.getenv('SUBSCRIBE_URL', 'https://portal.azure.com/#create/1700007431.synesthetica')

Session(app)

# Microsoft Auth Configuration
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
AUTHORITY = os.getenv('AUTHORITY')
REDIRECT_URI = os.getenv('REDIRECT_URI')
SCOPE = ["User.Read"]  # Simplified scope for user profile access

# Log environment variables for debugging
logger.info(f"Environment variables - CLIENT_ID: {CLIENT_ID}, AUTHORITY: {AUTHORITY}, REDIRECT_URI: {REDIRECT_URI}")

# Build MSAL client
msal_client = msal.ConfidentialClientApplication(
    CLIENT_ID,
    authority=AUTHORITY,
    client_credential=CLIENT_SECRET
)

# Audio generation configuration
OUTPUT_DIR = "static/audio"
os.makedirs(OUTPUT_DIR, exist_ok=True)
SAMPLE_RATE = 44100
DURATION_PER_STEP = 60 / 1000

# Note-to-semitone mapping
NOTE_TO_SEMITONE = {
    'C': 0, 'C#': 1, 'D': 2, 'D#': 3,
    'E': 4, 'F': 5, 'F#': 6, 'G': 7,
    'G#': 8, 'A': 9, 'A#': 10, 'B': 11
}
note_names = list(NOTE_TO_SEMITONE.keys())

# Frequency-to-color mapping
freq_symbols = {
    "A0": {"frequency": 27.50, "color": [139, 0, 0], "range": [27.50, 29.14], "symbol": "♩"},
    "A#0/Bb0": {"frequency": 29.14, "color": [255, 69, 0], "range": [29.14, 30.87], "symbol": "♯"},
    "B0": {"frequency": 30.87, "color": [204, 204, 0], "range": [30.87, 32.70], "symbol": "♩"},
    "C1": {"frequency": 32.70, "color": [102, 152, 0], "range": [32.70, 34.65], "symbol": "♩"},
    "C#1/Db1": {"frequency": 34.65, "color": [0, 100, 0], "range": [34.65, 36.71], "symbol": "♯"},
    "D1": {"frequency": 36.71, "color": [0, 50, 69], "range": [36.71, 38.89], "symbol": "♩"},
    "D#1/Eb1": {"frequency": 38.89, "color": [0, 0, 139], "range": [38.89, 41.20], "symbol": "♯"},
    "E1": {"frequency": 41.20, "color": [75, 0, 130], "range": [41.20, 43.65], "symbol": "♩"},
    "F1": {"frequency": 43.65, "color": [112, 0, 171], "range": [43.65, 46.25], "symbol": "♩"},
    "F#1/Gb1": {"frequency": 46.25, "color": [148, 0, 211], "range": [46.25, 49.00], "symbol": "♯"},
    "G1": {"frequency": 49.00, "color": [157, 0, 106], "range": [49.00, 51.91], "symbol": "♩"},
    "G#1/Ab1": {"frequency": 51.91, "color": [165, 0, 0], "range": [51.91, 55.00], "symbol": "♯"},
    "A1": {"frequency": 55.00, "color": [210, 0, 128], "range": [55.00, 58.27], "symbol": "♩"},
    "A#1/Bb1": {"frequency": 58.27, "color": [255, 94, 0], "range": [58.27, 61.74], "symbol": "♯"},
    "B1": {"frequency": 61.74, "color": [221, 221, 0], "range": [61.74, 65.41], "symbol": "♩"},
    "C2": {"frequency": 65.41, "color": [111, 175, 0], "range": [65.41, 69.30], "symbol": "♩"},
    "C#2/Db2": {"frequency": 69.30, "color": [0, 128, 0], "range": [69.30, 73.42], "symbol": "♯"},
    "D2": {"frequency": 73.42, "color": [0, 64, 85], "range": [73.42, 77.78], "symbol": "♩"},
    "D#2/Eb2": {"frequency": 77.78, "color": [0, 0, 170], "range": [77.78, 82.41], "symbol": "♯"},
    "E2": {"frequency": 82.41, "color": [92, 0, 159], "range": [82.41, 87.31], "symbol": "♩"},
    "F2": {"frequency": 87.31, "color": [119, 0, 96], "range": [87.31, 92.50], "symbol": "♩"},
    "F#2/Gb2": {"frequency": 92.50, "color": [159, 0, 226], "range": [92.50, 98.00], "symbol": "♯"},
    "G2": {"frequency": 98.00, "color": [175, 0, 113], "range": [98.00, 103.83], "symbol": "♩"},
    "G#2/Ab2": {"frequency": 103.83, "color": [191, 0, 0], "range": [103.83, 110.00], "symbol": "♯"},
    "A2": {"frequency": 110.00, "color": [223, 59, 128], "range": [110.00, 116.54], "symbol": "♩"},
    "A#2/Bb2": {"frequency": 116.54, "color": [255, 119, 0], "range": [116.54, 123.47], "symbol": "♯"},
    "B2": {"frequency": 123.47, "color": [238, 238, 0], "range": [123.47, 130.81], "symbol": "♩"},
    "C3": {"frequency": 130.81, "color": [119, 159, 0], "range": [130.81, 138.59], "symbol": "♩"},
    "C#3/Db3": {"frequency": 138.59, "color": [0, 160, 0], "range": [138.59, 146.83], "symbol": "♯"},
    "D3": {"frequency": 146.83, "color": [0, 80, 100], "range": [146.83, 155.56], "symbol": "♩"},
    "D#3/Eb3": {"frequency": 155.56, "color": [0, 0, 200], "range": [155.56, 164.81], "symbol": "♯"},
    "E3": {"frequency": 164.81, "color": [109, 0, 188], "range": [164.81, 174.61], "symbol": "♩"},
    "F3": {"frequency": 174.61, "color": [140, 0, 215], "range": [174.61, 185.00], "symbol": "♩"},
    "F#3/Gb3": {"frequency": 185.00, "color": [170, 0, 241], "range": [185.00, 196.00], "symbol": "♯"},
    "G3": {"frequency": 196.00, "color": [194, 0, 121], "range": [196.00, 207.65], "symbol": "♩"},
    "G#3/Ab3": {"frequency": 207.65, "color": [217, 0, 0], "range": [207.65, 220.00], "symbol": "♯"},
    "A3": {"frequency": 220.00, "color": [236, 72, 0], "range": [220.00, 233.08], "symbol": "♩"},
    "A#3/Bb3": {"frequency": 233.08, "color": [255, 144, 0], "range": [233.08, 246.94], "symbol": "♯"},
    "B3": {"frequency": 246.94, "color": [255, 255, 0], "range": [246.94, 261.63], "symbol": "♩"},
    "C4": {"frequency": 261.63, "color": [128, 224, 0], "range": [261.63, 277.18], "symbol": "♩"},
    "C#4/Db4": {"frequency": 277.18, "color": [0, 192, 0], "range": [277.18, 293.66], "symbol": "♯"},
    "D4": {"frequency": 293.66, "color": [0, 96, 115], "range": [293.66, 311.13], "symbol": "♩"},
    "D#4/Eb4": {"frequency": 311.13, "color": [0, 0, 230], "range": [311.13, 329.63], "symbol": "♯"},
    "E4": {"frequency": 329.63, "color": [126, 0, 217], "range": [329.63, 349.23], "symbol": "♩"},
    "F4": {"frequency": 349.23, "color": [159, 26, 236], "range": [349.23, 369.99], "symbol": "♩"},
    "F#4/Gb4": {"frequency": 369.99, "color": [191, 51, 255], "range": [369.99, 392.00], "symbol": "♯"},
    "G4": {"frequency": 392.00, "color": [217, 26, 128], "range": [392.00, 415.30], "symbol": "♩"},
    "G#4/Ab4": {"frequency": 415.30, "color": [243, 0, 0], "range": [415.30, 440.00], "symbol": "♯"},
    "A4": {"frequency": 440.00, "color": [249, 85, 0], "range": [440.00, 466.16], "symbol": "♩"},
    "A#4/Bb4": {"frequency": 466.16, "color": [255, 169, 0], "range": [466.16, 493.88], "symbol": "♯"},
    "B4": {"frequency": 493.88, "color": [255, 255, 51], "range": [493.88, 523.25], "symbol": "♩"},
    "C5": {"frequency": 523.25, "color": [153, 255, 51], "range": [523.25, 554.37], "symbol": "♩"},
    "C#5/Db5": {"frequency": 554.37, "color": [51, 255, 51], "range": [554.37, 587.33], "symbol": "♯"},
    "D5": {"frequency": 587.33, "color": [51, 204, 204], "range": [587.33, 622.25], "symbol": "♪"},
    "D#5/Eb5": {"frequency": 622.25, "color": [51, 51, 255], "range": [622.25, 659.25], "symbol": "♭"},
    "E5": {"frequency": 659.25, "color": [128, 51, 255], "range": [659.25, 698.46], "symbol": "𝅘𝅥𝅮"},
    "F5": {"frequency": 698.46, "color": [159, 87, 255], "range": [698.46, 739.99], "symbol": "♩"},
    "F#5/Gb5": {"frequency": 739.99, "color": [190, 123, 255], "range": [739.99, 783.99], "symbol": "♯"},
    "G5": {"frequency": 783.99, "color": [204, 87, 128], "range": [783.99, 830.61], "symbol": "♫"},
    "G#5/Ab5": {"frequency": 830.61, "color": [255, 51, 51], "range": [830.61, 880.00], "symbol": "♭"},
    "A5": {"frequency": 880.00, "color": [255, 128, 102], "range": [880.00, 932.33], "symbol": "𝅗𝅥"},
    "A#5/Bb5": {"frequency": 932.33, "color": [255, 204, 102], "range": [932.33, 987.77], "symbol": "♯"},
    "B5": {"frequency": 987.77, "color": [255, 255, 102], "range": [987.77, 1046.50], "symbol": "𝅘𝅥"},
    "C6": {"frequency": 1046.50, "color": [179, 255, 102], "range": [1046.50, 1108.73], "symbol": "♩"},
    "C#6/Db6": {"frequency": 1108.73, "color": [102, 255, 102], "range": [1108.73, 1174.66], "symbol": "♯"},
    "D6": {"frequency": 1174.66, "color": [102, 204, 204], "range": [1174.66, 1244.51], "symbol": "♪"},
    "D#6/Eb6": {"frequency": 1244.51, "color": [102, 102, 255], "range": [1244.51, 1318.51], "symbol": "♭"},
    "E6": {"frequency": 1318.51, "color": [153, 102, 255], "range": [1318.51, 1396.91], "symbol": "𝅘𝅥𝅮"},
    "F6": {"frequency": 1396.91, "color": [171, 128, 255], "range": [1396.91, 1479.98], "symbol": "♩"},
    "F#6/Gb6": {"frequency": 1479.98, "color": [201, 153, 255], "range": [1479.98, 1567.98], "symbol": "♯"},
    "G6": {"frequency": 1567.98, "color": [209, 128, 153], "range": [1567.98, 1661.22], "symbol": "♫"},
    "G#6/Ab6": {"frequency": 1661.22, "color": [255, 102, 102], "range": [1661.22, 1760.00], "symbol": "♭"},
    "A6": {"frequency": 1760.00, "color": [255, 153, 128], "range": [1760.00, 1864.66], "symbol": "𝅗𝅥"},
    "A#6/Bb6": {"frequency": 1864.66, "color": [255, 204, 153], "range": [1864.66, 1975.53], "symbol": "♯"},
    "B6": {"frequency": 1975.53, "color": [255, 255, 153], "range": [1975.53, 2093.00], "symbol": "𝅘𝅥"},
    "C7": {"frequency": 2093.00, "color": [204, 255, 153], "range": [2093.00, 2217.46], "symbol": "♩"},
    "C#7/Db7": {"frequency": 2217.46, "color": [153, 255, 153], "range": [2217.46, 2349.32], "symbol": "♯"},
    "D7": {"frequency": 2349.32, "color": [153, 204, 204], "range": [2349.32, 2489.02], "symbol": "♪"},
    "D#7/Eb7": {"frequency": 2489.02, "color": [153, 153, 255], "range": [2489.02, 2637.02], "symbol": "♭"},
    "E7": {"frequency": 2637.02, "color": [197, 153, 255], "range": [2637.02, 2793.83], "symbol": "𝅘𝅥𝅮"},
    "F7": {"frequency": 2793.83, "color": [222, 176, 255], "range": [2793.83, 2959.96], "symbol": "♩"},
    "F#7/Gb7": {"frequency": 2959.96, "color": [246, 198, 255], "range": [2959.96, 3135.96], "symbol": "♯"},
    "G7": {"frequency": 3135.96, "color": [255, 176, 204], "range": [3135.96, 3322.44], "symbol": "♫"},
    "G#7/Ab7": {"frequency": 3322.44, "color": [255, 153, 153], "range": [3322.44, 3520.00], "symbol": "♭"},
    "A7": {"frequency": 3520.00, "color": [255, 194, 176], "range": [3520.00, 3729.31], "symbol": "𝅗𝅥"},
    "A#7/Bb7": {"frequency": 3729.31, "color": [255, 234, 198], "range": [3729.31, 3951.07], "symbol": "♯"},
    "B7": {"frequency": 3951.07, "color": [255, 255, 204], "range": [3951.07, 4186.01], "symbol": "𝅘𝅥"},
    "C8": {"frequency": 4186.01, "color": [144, 238, 144], "range": [4186.01, 4434.92], "symbol": "♩"},
}

# Color-to-frequency mapping functions
def hue_to_note_name(hue):
    index = int((hue % 360) / 30)
    return note_names[index]

def brightness_to_octave(brightness):
    return int(3 + brightness * 3)

def color_to_frequency(r, g, b):
    h, s, v = rgb_to_hsv(r / 255, g / 255, b / 255)
    hue_deg = h * 360
    note_name = hue_to_note_name(hue_deg)
    octave = brightness_to_octave(v)
    midi_note = 12 + octave * 12 + NOTE_TO_SEMITONE[note_name]
    return 440 * 2 ** ((midi_note - 69) / 12)

def get_quickly_frequency_by_color(r, g, b):
    target = [r, g, b]
    for note, props in freq_symbols.items():
        if props["color"] == target:
            return props["frequency"]
    return None

def get_frequency_from_color(r, g, b, threshold=10000):
    closest_freq = None
    closest_dist = float('inf')
    for info in freq_symbols.items():
        rgb = info[1].get("color")
        if tuple(rgb) == (r, g, b):
            return info[1]["frequency"]
        if rgb:
            dist = color_distance((r, g, b), tuple(rgb))
            if dist < closest_dist:
                closest_dist = dist
                closest_freq = info[1]["frequency"]
    return closest_freq

def color_distance(c1, c2):
    return sum((a - b) ** 2 for a, b in zip(c1, c2)) ** 0.5

# Tone generation function
def generate_tone(frequencies, brush, duration=DURATION_PER_STEP):
    valid_brushes = {"spray", "star", "cross", "square", "triangle", "sawtooth", "round", "line"}
    if brush.lower() not in valid_brushes:
        raise ValueError(f"Invalid brush type: {brush}. Valid options are {valid_brushes}")

    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    
    if frequencies == 0:
        return np.zeros_like(t)

    if not isinstance(frequencies, (list, np.ndarray)) or len(frequencies) == 0:
        return np.zeros_like(t)

    frequencies = np.clip(frequencies, 20, 20000)
    waveform = np.zeros_like(t)

    for freq in frequencies:
        phase = 2 * np.pi * freq * t
        if brush.lower() == "spray":
            mod_ratio = 1.7 + 0.3 * np.sin(2 * np.pi * 0.2 * t)
            carrier = np.sin(phase + 3 * np.sin(mod_ratio * phase))
            tone = carrier * (0.6 + 0.4 * np.sin(2 * np.pi * 5 * t))
            noise = 0.15 * np.random.normal(0, 1, len(t))
            noise = signal.lfilter(*signal.butter(4, 1000/(SAMPLE_RATE/2)), noise)
            tone = tone * (0.7 + 0.3 * np.sin(2 * np.pi * 3 * t)) + noise
        elif brush.lower() == "star":
            harmonics = [(1, 0.6), (2, 0.4), (3, 0.3), (5, 0.2)]
            tone = sum(np.sin(h * phase) * amp for h, amp in harmonics)
            detune = 1 + 0.001 * np.sin(2 * np.pi * 0.1 * t)
            tone = tone * detune
        elif brush.lower() == "cross":
            distorted_phase = phase + 0.8 * np.sin(phase)
            tone = np.sin(distorted_phase) * np.sin(2 * distorted_phase)
        elif brush.lower() == "square":
            pw = 0.5 + 0.3 * np.sin(2 * np.pi * 0.5 * t)
            tone = signal.square(phase, duty=pw)
        elif brush.lower() == "triangle":
            tone = signal.sawtooth(phase, width=0.5)
            tone -= 0.25 * signal.sawtooth(2 * phase, width=0.5)
        elif brush.lower() == "sawtooth":
            detune = [0.99, 1.0, 1.01]
            tone = sum(0.4 * np.sin(2 * np.pi * d * freq * t) for d in detune)
        else:  # round or line
            vibrato = 0.1 * np.sin(2 * np.pi * 6 * t)
            tone = 0.9 * np.sin(phase + vibrato) + 0.1 * np.sin(3 * phase)
        
        waveform += tone

    envelope = np.ones_like(t)
    attack_len = int(0.1 * len(t))
    attack_len = max(1, attack_len)
    envelope[:attack_len] = np.linspace(0, 1, attack_len)
    envelope[attack_len:] = np.exp(-5 * np.linspace(0, 1, len(t) - attack_len))
    waveform *= envelope

    max_val = np.max(np.abs(waveform))
    if max_val > 0:
        waveform /= max_val

    return waveform


# Azure Marketplace Metered Billing
def report_metered_usage(subscription_id, quantity):
    try:
        marketplace_scope = ["https://marketplaceapi.microsoft.com/.default"]
        token_result = msal_client.acquire_token_for_client(scopes=marketplace_scope)
        if "access_token" not in token_result:
            logger.error(f"Failed to acquire token for Marketplace API: {token_result.get('error')}")
            return False

        headers = {
            "Authorization": f"Bearer {token_result['access_token']}",
            "Content-Type": "application/json"
        }
        metering_url = f"https://marketplaceapi.microsoft.com/api/usageEvent?api-version=2018-08-31"
        payload = {
            "resourceUri": f"/subscriptions/{subscription_id}",
            "quantity": quantity,
            "dimension": "additional_submission",
            "effectiveStartTime": datetime.utcnow().isoformat(),
            "planId": "basic-usage-based"
        }
        response = requests.post(metering_url, headers=headers, json=payload)
        if response.status_code == 200:
            logger.info(f"Reported metered usage: {quantity} submissions for {subscription_id}")
            return True
        else:
            logger.error(f"Failed to report metered usage: {response.status_code}, {response.text}")
            return False
    except Exception as e:
        logger.error(f"Error reporting metered usage: {str(e)}")
        return False

# Database connection
def get_db_connection():
    try:
        connection_string = f"DRIVER={app.config['DB_DRIVER']};SERVER={app.config['DB_SERVER']};DATABASE={app.config['DB_NAME']};UID={app.config['DB_USER']};PWD={app.config['DB_PASSWORD']}"
        connection = pyodbc.connect(connection_string)
        logger.info("Successfully connected to SQL Server database")
        return connection
    except pyodbc.Error as e:
        logger.error(f"Error connecting to SQL Server: {e}")
        return None

# Security headers
@app.after_request
def after_request(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    return response

# Webhook for Azure Marketplace
@app.route('/webhook', methods=['POST'])
def marketplace_webhook():
    logger.info("Received webhook request from Azure Marketplace")
    try:
        payload = request.get_json()
        if not payload:
            logger.error("No JSON payload provided in webhook request")
            return jsonify({"error": "No payload provided"}), 400

        logger.info(f"Webhook payload: {payload}")
        operation_id = payload.get('operationId')
        action = payload.get('action')
        subscription_id = payload.get('subscriptionId')
        plan_id = payload.get('planId')

        if not all([operation_id, action, subscription_id]):
            logger.error("Missing required fields in webhook payload")
            return jsonify({"error": "Missing required fields"}), 400

        connection = get_db_connection()
        if not connection:
            logger.error("Database connection failed")
            return jsonify({"error": "Database connection failed"}), 500

        try:
            cursor = connection.cursor()
            insert_query = """
                INSERT INTO marketplace_events (operation_id, action, subscription_id, plan_id, event_timestamp)
                VALUES (?, ?, ?, ?, ?)
            """
            cursor.execute(insert_query, (
                operation_id,
                action,
                subscription_id,
                plan_id,
                datetime.now()
            ))
            connection.commit()
            logger.info(f"Stored webhook event: {action} for subscription {subscription_id}")
        except pyodbc.Error as e:
            logger.error(f"Database error: {str(e)}")
            return jsonify({"error": "Failed to store webhook event"}), 500
        finally:
            cursor.close()
            connection.close()
            logger.info("Database connection closed")

        if action == "Subscribed":
            logger.info(f"Processing subscription activation for {subscription_id}")
            # Optionally resolve subscription here
        elif action == "Unsubscribed":
            logger.info(f"Processing subscription cancellation for {subscription_id}")
        else:
            logger.warning(f"Unhandled action: {action}")

        return jsonify({"status": "success", "operationId": operation_id}), 200
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        return jsonify({"error": f"Webhook processing failed: {str(e)}"}), 500

# Resolve Azure Marketplace subscription
def resolve_subscription(operation_id):
    try:
        marketplace_scope = ["https://marketplaceapi.microsoft.com/.default"]
        token_result = msal_client.acquire_token_for_client(scopes=marketplace_scope)
        if "access_token" not in token_result:
            logger.error(f"Failed to acquire token for Marketplace API: {token_result.get('error')}")
            return False

        headers = {"Authorization": f"Bearer {token_result['access_token']}"}
        resolve_url = f"https://marketplaceapi.microsoft.com/api/saas/subscriptions/resolve?api-version=2018-08-31"
        response = requests.post(resolve_url, headers=headers, json={"operationId": operation_id})
        
        if response.status_code == 200:
            logger.info(f"Subscription resolved: {response.json()}")
            return True
        else:
            logger.error(f"Failed to resolve subscription: {response.status_code}, {response.text}")
            return False
    except Exception as e:
        logger.error(f"Error resolving subscription: {str(e)}")
        return False

# Routes
@app.route("/")
def home():
    logger.info("Rendering front page")
    user = session.get('user')
    show_welcome = session.get('show_welcome', False)
    if show_welcome:
        session.pop('show_welcome')  # Clear the flag after rendering
    return render_template("index.html", user=user, show_welcome=show_welcome)

@app.route("/auth")
def auth():
    logger.info(f"Generating auth URL with redirect_uri: {REDIRECT_URI}")
    try:
        auth_url = msal_client.get_authorization_request_url(
            SCOPE,
            redirect_uri=REDIRECT_URI,
            response_type="code"
        )
        logger.info(f"Auth URL: {auth_url}")
        return redirect(auth_url)
    except Exception as e:
        logger.error(f"Error generating auth URL: {str(e)}")
        return render_template("error.html", error=f"Failed to initiate authentication: {str(e)}"), 500

@app.route("/getAToken")
def authorized():
    logger.info(f"Received callback: {request.url}")
    code = request.args.get('code')
    logger.info(f"Received auth code: {'present' if code else 'missing'}")
    if not code:
        logger.error("No code provided in callback")
        return render_template("error.html", error="Authentication failed: No code provided"), 400
    try:
        logger.info(f"Attempting token acquisition with redirect_uri: {REDIRECT_URI}, scopes: {SCOPE}")
        token_result = msal_client.acquire_token_by_authorization_code(
            code,
            scopes=SCOPE,
            redirect_uri=REDIRECT_URI
        )
        logger.info(f"Token result: {token_result}")
        if "error" in token_result:
            logger.error(f"Auth error: {token_result['error']}, Description: {token_result.get('error_description')}")
            return render_template("error.html", error=f"Authentication failed: {token_result['error']} - {token_result.get('error_description')}"), 400
        session['access_token'] = token_result['access_token']
        logger.info("Token acquired successfully")
        graph_endpoint = "https://graph.microsoft.com/v1.0/me"
        headers = {"Authorization": f"Bearer {session['access_token']}"}
        logger.info("Fetching user profile from Microsoft Graph")
        user_response = requests.get(graph_endpoint, headers=headers)
        if user_response.status_code == 200:
            user_data = user_response.json()
            session['user'] = {
                'name': user_data.get('displayName', 'Unknown User'),
                'email': user_data.get('mail') or user_data.get('userPrincipalName', 'Unknown Email')
            }
            session['show_welcome'] = True
            logger.info(f"User logged in: {session['user']['name']} ({session['user']['email']})")
        else:
            logger.error(f"Failed to fetch user profile: {user_response.status_code}, {user_response.text}")
            session.pop('access_token', None) # Clear token on failure
            return render_template("error.html", error="Failed to fetch user profile"), 400
        session.modified = True # Ensure session is marked as modified
        return redirect(url_for('home'))
    except Exception as e:
        logger.error(f"Unexpected error in auth: {str(e)}", exc_info=True)
        return render_template("error.html", error=f"Authentication failed: {str(e)}"), 500
@app.route("/logout")
def logout():
    session.clear()
    session['show_welcome'] = False
    logger.info("User logged out")
    return redirect(url_for('home'))
@app.route('/about')
def about():
    user = session.get('user') # Retrieve user from session for authentication
    return render_template('about.html', user=user)
@app.route("/pricing")
def pricing():
    logger.info("Rendering Pricing page")
    user = session.get('user')
    return render_template("pricing.html", user=user)
@app.route("/privacy")
def privacy():
    logger.info("Rendering Privacy Policy page")
    user = session.get('user')
    return render_template("privacy.html", user=user)
@app.route("/support")
def support():
    logger.info("Rendering Support page")
    user = session.get('user')
    return render_template("support.html", user=user)
@app.route("/admin")
def admin():
    conn = get_db_connection()
    if not conn:
        return "Database error", 500
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT short_id, ticket_uuid, user_email, category, status, created_at
            FROM SupportTickets
            ORDER BY created_at DESC
        """)
        tickets = []
        for row in cur.fetchall():
            tickets.append({
                "short_id": row[0],
                "uuid": str(row[1]),
                "email": row[2],
                "category": row[3],
                "status": row[4],
                "created": row[5].strftime("%b %d, %Y %I:%M %p") if row[5] else "Unknown"
            })
        return render_template("admin.html", tickets=tickets)
    except Exception as e:
        logger.error(f"Admin page error: {e}")
        return "Server error", 500
    finally:
        cur.close()
        conn.close()
@app.route("/api/support", methods=['POST'])
def create_ticket():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data"}), 400
    category = data.get('category')
    user_email = data.get('user_email')
    user_message = data.get('user_message')
    if not all([category, user_email, user_message]):
        return jsonify({"error": "category, user_email, user_message required"}), 400
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "DB error"}), 500
    try:
        cur = conn.cursor()
        ticket_uuid = str(uuid.uuid4())
        now = datetime.utcnow().isoformat() + "Z"
        messages = [{"time": now, "sender": "user", "user": user_message, "assistant": None}]
        messages_json = json.dumps(messages)
        sql = """
            INSERT INTO SupportTickets
                (ticket_uuid, user_email, category, messages, status, created_at)
            VALUES (?, ?, ?, ?, 'Open', GETDATE())
        """
        cur.execute(sql, (ticket_uuid, user_email, category, messages_json))
        conn.commit()
        # Get short_id
        cur.execute("SELECT short_id FROM SupportTickets WHERE ticket_uuid = ?", (ticket_uuid,))
        short_id = cur.fetchone()[0]
        # SEND CONFIRMATION EMAIL TO USER
        send_user_confirmation(user_email, short_id, category, user_message)
        return jsonify({
            "ticket_uuid": ticket_uuid,
            "short_id": short_id,
            "message": "We have received your ticket. Our team will reply soon.",
            "chat": messages,
            "chat_url": url_for('chat_page', short_id=short_id, _external=True)
        }), 201
    except Exception as e:
        logger.error(f"Error: {e}")
        return jsonify({"error": "Failed to create ticket"}), 500
    finally:
        cur.close()
        conn.close()
@app.route("/api/support", methods=['GET'])
def list_tickets():
    user_email = session.get('user', {}).get('email')
    if not user_email: return jsonify({"error": "Login required"}), 401
    conn = get_db_connection()
    if not conn: return jsonify({"error": "DB error"}), 500
    try:
        cur = conn.cursor()
        sql = "SELECT ticket_uuid, title, category, status, created_at, messages FROM SupportTickets WHERE user_email = ? ORDER BY created_at DESC"
        cur.execute(sql, (user_email,))
        tickets = []
        for row in cur.fetchall():
            chat = json.loads(row.messages) if row.messages else []
            tickets.append({
                "ticket_uuid": row.ticket_uuid,
                "title": row.title,
                "category": row.category,
                "status": row.status,
                "created_at": row.created_at.isoformat(),
                "chat": chat # Full conversation
            })
        return jsonify({"tickets": tickets}), 200
    except Exception as e:
        logger.error(f"Error: {e}")
        return jsonify({"error": "Failed"}), 500
    finally:
        cur.close()
        conn.close()



@app.route("/support/<short_id>")
def chat_page(short_id):
    user = session.get('user')
    ticket_uuid = short_to_uuid(short_id)

    logger.info(f"[DEBUG] short_id: {short_id}, ticket_uuid: {ticket_uuid}")

    if not ticket_uuid:
        return render_template("error.html", error=f"Invalid short_id: {short_id}"), 404

    conn = get_db_connection()
    if not conn:
        return render_template("error.html", error="Database connection failed"), 500

    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT ticket_uuid, user_email, category, status, messages FROM SupportTickets WHERE ticket_uuid = ?",
            (ticket_uuid,)
        )
        row = cur.fetchone()
        if not row:
            return render_template("error.html", error=f"Ticket not found: {ticket_uuid}"), 404

        logger.info(f"[DEBUG] Raw messages: {repr(row[4])}")

        # FIXED: Handle double-encoded JSON
        chat = []
        if row[4]:
            try:
                parsed = json.loads(row[4])
                if isinstance(parsed, list):
                    for item in parsed:
                        if isinstance(item, str):
                            try:
                                msg = json.loads(item)
                                if isinstance(msg, dict) and msg.get("sender") in ["user", "support"]:
                                    chat.append(msg)
                            except json.JSONDecodeError:
                                continue
                        elif isinstance(item, dict) and item.get("sender") in ["user", "support"]:
                            chat.append(item)
                else:
                    logger.warning(f"messages is not a list: {parsed}")
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode failed: {e}")
                chat = []

        logger.info(f"[DEBUG] Final chat: {chat}")

        # Add welcome
        if not any(m.get("sender") == "support" for m in chat):
            chat.insert(0, {
                "sender": "support",
                "assistant": "Welcome to support! How can we help you today?",
                "time": datetime.utcnow().isoformat() + "Z"
            })

        return render_template(
            "support_chat.html",
            user=user,
            short_id=short_id,
            category=row[2] or "General",
            status=row[3] or "Open",
            chat=chat
        )

    except Exception as e:
        logger.error(f"chat_page crash: {e}")
        return render_template("error.html", error="Server error"), 500
    finally:
        cur.close()
        conn.close()


@app.route("/admin/support/<short_id>")
def admin_chat_page(short_id):
    ticket_uuid = short_to_uuid(short_id)
    logger.info(f"[ADMIN] short_id: {short_id} → {ticket_uuid}")

    if not ticket_uuid:
        return render_template("error.html", error=f"Invalid short_id: {short_id}"), 404

    conn = get_db_connection()
    if not conn:
        return render_template("error.html", error="Database connection failed"), 500

    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT ticket_uuid, user_email, category, status, messages FROM SupportTickets WHERE ticket_uuid = ?",
            (ticket_uuid,)
        )
        row = cur.fetchone()
        if not row:
            return render_template("error.html", error=f"Ticket not found: {ticket_uuid}"), 404

        logger.info(f"[ADMIN] Raw messages: {repr(row[4])}")

        chat = []
        if row[4]:
            try:
                parsed = json.loads(row[4])
                if isinstance(parsed, list):
                    for item in parsed:
                        if isinstance(item, str):
                            try:
                                msg = json.loads(item)
                                if isinstance(msg, dict) and msg.get("sender") in ["user", "support"]:
                                    chat.append(msg)
                            except json.JSONDecodeError:
                                continue
                        elif isinstance(item, dict) and item.get("sender") in ["user", "support"]:
                            chat.append(item)
                else:
                    logger.warning(f"messages not a list: {parsed}")
            except json.JSONDecodeError as e:
                logger.error(f"JSON error: {e}")
                chat = []

        logger.info(f"[ADMIN] Final chat: {chat}")

        return render_template(
            "admin_chat.html",
            short_id=short_id,
            category=row[2] or "General",
            status=row[3] or "Open",
            chat=chat
        )

    except Exception as e:
        logger.error(f"admin_chat_page crash: {e}")
        return render_template("error.html", error="Server error"), 500
    finally:
        cur.close()
        conn.close()

# ========================================
# ADD THIS FUNCTION: short_to_uuid()
# ========================================
def short_to_uuid(short_id: str):
    """
    Convert 8-char short_id (first 8 chars of UUID without dashes) to full UUID.
    Example: 'BB9D2634' → 'BB9D2634-3540-4411-B9DA-D7E555788364'
    """
    if not short_id or len(short_id) != 8:
        logger.warning(f"Invalid short_id length: {short_id}")
        return None

    try:
        conn = get_db_connection()
        if not conn:
            logger.error("DB connection failed in short_to_uuid")
            return None

        cur = conn.cursor()
        # Query: Find ticket where first 8 chars of UUID (no dashes) match short_id
        cur.execute("""
            SELECT ticket_uuid 
            FROM SupportTickets 
            WHERE LEFT(REPLACE(CAST(ticket_uuid AS varchar(36)), '-', ''), 8) = ?
        """, (short_id.upper(),))
        row = cur.fetchone()
        cur.close()
        conn.close()

        if row:
            full_uuid = str(row[0])
            logger.info(f"Resolved short_id {short_id} → {full_uuid}")
            return full_uuid
        else:
            logger.warning(f"short_id {short_id} not found in DB")
            return None
    except Exception as e:
        logger.error(f"Error in short_to_uuid: {e}")
        return None

@app.route("/api/support/<short_id>/reply", methods=['POST'])
def add_reply(short_id):
    data = request.get_json()
    if not data or 'reply' not in data:
        return jsonify({"error": "reply required"}), 400

    reply_text = data['reply'].strip()
    if not reply_text:
        return jsonify({"error": "Empty reply"}), 400

    ticket_uuid = short_to_uuid(short_id)
    if not ticket_uuid:
        return jsonify({"error": "Ticket not found"}), 404

    new_message = {
        "sender": "user",
        "user": reply_text,
        "time": datetime.utcnow().isoformat() + "Z"
    }

    logger.info(f"[REPLY] Adding: {new_message}")

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "DB error"}), 500

    try:
        cur = conn.cursor()

        # BEFORE
        cur.execute("SELECT messages FROM SupportTickets WHERE ticket_uuid = ?", (ticket_uuid,))
        old = cur.fetchone()
        logger.info(f"[REPLY] Before: {repr(old[0]) if old else None}")

        # FINAL: json.dumps + CAST
        sql = """
            UPDATE SupportTickets 
            SET messages = JSON_MODIFY(messages, 'append $', CAST(? AS NVARCHAR(MAX))) 
            WHERE ticket_uuid = ?
        """
        cur.execute(sql, (json.dumps(new_message), ticket_uuid))
        affected = cur.rowcount
        conn.commit()

        logger.info(f"[REPLY] Rows affected: {affected}")

        # AFTER
        cur.execute("SELECT messages FROM SupportTickets WHERE ticket_uuid = ?", (ticket_uuid,))
        new = cur.fetchone()
        logger.info(f"[REPLY] After: {repr(new[0]) if new else None}")

        if affected == 0:
            return jsonify({"error": "No update"}), 500

        return jsonify({"status": "saved", "message": new_message}), 200

    except Exception as e:
        logger.error(f"[REPLY ERROR] {e}")
        return jsonify({"error": "Failed"}), 500
    finally:
        cur.close()
        conn.close()

@app.route("/admin/api/support/<short_id>/reply", methods=['POST'])
def admin_add_reply(short_id):
    # === TEMPORARILY DISABLE AUTH FOR TESTING ===
    # if not session.get('is_admin'):
    #     return jsonify({"error": "Unauthorized"}), 403

    data = request.get_json()
    reply = data.get('reply', '').strip()
    if not reply:
        return jsonify({"error": "reply required"}), 400

    ticket_uuid = short_to_uuid(short_id)
    if not ticket_uuid:
        return jsonify({"error": "Ticket not found"}), 404

    new_message = {
        "sender": "support",
        "assistant": reply,
        "time": datetime.utcnow().isoformat() + "Z"
    }

    logger.info(f"[ADMIN REPLY] Adding: {new_message}")

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "DB error"}), 500

    try:
        cur = conn.cursor()

        # BEFORE
        cur.execute("SELECT messages FROM SupportTickets WHERE ticket_uuid = ?", (ticket_uuid,))
        old = cur.fetchone()
        logger.info(f"[ADMIN REPLY] Before: {repr(old[0]) if old else None}")

        # FIXED: Use CAST + json.dumps
        cur.execute(
            "UPDATE SupportTickets SET messages = JSON_MODIFY(messages, 'append $', CAST(? AS NVARCHAR(MAX))) WHERE ticket_uuid = ?",
            (json.dumps(new_message), ticket_uuid)
        )
        affected = cur.rowcount
        conn.commit()

        logger.info(f"[ADMIN REPLY] Rows affected: {affected}")

        # AFTER
        cur.execute("SELECT messages FROM SupportTickets WHERE ticket_uuid = ?", (ticket_uuid,))
        new = cur.fetchone()
        logger.info(f"[ADMIN REPLY] After: {repr(new[0]) if new else None}")

        if affected == 0:
            return jsonify({"error": "No update"}), 500

        return jsonify({"status": "saved", "message": new_message}), 200

    except Exception as e:
        logger.error(f"[ADMIN REPLY ERROR] {e}")
        return jsonify({"error": "Failed"}), 500
    finally:
        cur.close()
        conn.close()
        
@app.route("/submit", methods=['POST'])
def submit():
    connection = get_db_connection()
    if not connection:
        logger.error("Database connection failed")
        return jsonify({"error": "Database connection failed"}), 500
    try:
        cursor = connection.cursor()
        # Get submission key (user email or IP address)
        today = datetime.now().strftime('%Y-%m-%d')
        submission_key = request.remote_addr
        is_authenticated = 'user' in session
        if is_authenticated:
            submission_key = session['user']['email']
        # Count submissions for the day
        query = """
            SELECT COUNT(*) as count
            FROM submissions
            WHERE CAST(submission_date AS DATE) = ?
            AND (user_email = ? OR ip_address = ?)
        """
        cursor.execute(query, (today, submission_key if is_authenticated else None, submission_key if not is_authenticated else None))
        submission_count = cursor.fetchone()[0]
        # Check subscription status
        is_subscribed = False
        subscription_id = None
        if is_authenticated:
            cursor.execute("""
                SELECT subscription_id
                FROM subscriptions
                WHERE user_email = ? AND status = 'active' AND expiry_date > GETDATE()
            """, (submission_key,))
            result = cursor.fetchone()
            if result:
                is_subscribed = True
                subscription_id = result[0]
        # Define limits
        UNAUTHENTICATED_LIMIT = 5
        AUTHENTICATED_LIMIT = 10
        # Check submission limits
        if not is_authenticated and submission_count >= UNAUTHENTICATED_LIMIT:
            logger.warning(f"Submission limit exceeded for unauthenticated user (IP: {request.remote_addr})")
            return jsonify({
                "error": "You've reached your limit today. Try again after 24 hours or log in to continue."
            }), 403
        elif is_authenticated and not is_subscribed and submission_count >= AUTHENTICATED_LIMIT:
            logger.warning(f"Submission limit exceeded for authenticated user: {submission_key}")
            return jsonify({
                "error": "You've reached your submission limit for today. Subscribe to continue.",
                "subscribe": True,
                "subscribe_url": SUBSCRIBE_URL
            }), 403
        elif is_authenticated and is_subscribed and submission_count >= FREE_SUBMISSION_LIMIT:
            # Metered billing for additional submissions
            additional_submissions = submission_count - FREE_SUBMISSION_LIMIT + 1
            cost = additional_submissions * ADDITIONAL_SUBMISSION_COST
            cursor.execute("""
                INSERT INTO billing_records (subscription_id, user_email, submission_id, amount, created_at)
                VALUES (?, ?, ?, ?, GETDATE())
            """, (subscription_id, submission_key, None, ADDITIONAL_SUBMISSION_COST))
            logger.info(f"Charged ${ADDITIONAL_SUBMISSION_COST} for additional submission {submission_count + 1} by {submission_key}")
            report_metered_usage(subscription_id, 1) # Report 1 additional submission
        data = request.json
        if 'image' not in data:
            logger.error("No image provided in request")
            return jsonify({"error": "No image provided"}), 400
        brush = data.get('brush', 'round')
        image_data = data['image'].split(',')[1]
        try:
            img = Image.open(BytesIO(base64.b64decode(image_data))).convert('RGBA')
        except Exception as e:
            logger.error(f"Invalid image data: {str(e)}")
            return jsonify({"error": f"Invalid image data: {str(e)}"}), 400
        width, height = img.size
        logger.info(f"Received image size: {width}x{height}")
        timeline = {}
        colors_found = set()
        for x in range(width):
            freqs = []
            for y in range(height):
                r, g, b, a = img.load()[x, y]
                if not (r == 0 and g == 0 and b == 0) and a > 200:
                    freq = get_quickly_frequency_by_color(r, g, b)
                    if freq is None:
                        freq = get_frequency_from_color(r, g, b)
                    if freq:
                        freqs.append(freq)
                        colors_found.add((r, g, b))
            if freqs:
                timeline[x] = list(np.unique(freqs))
        non_silent_columns = {x: freqs for x, freqs in timeline.items() if freqs}
        logger.info(f"Processed {len(non_silent_columns)} non-silent columns")
        logger.info(f"Colors detected: {colors_found}")
        stop = max((x for x, freqs in timeline.items() if freqs), default=0)
        timeline = {x: freqs if freqs else 0 for x in range(stop + 1)}
        if not non_silent_columns:
            logger.warning("No valid colors detected in image")
            return jsonify({"error": "No valid colors detected"}), 400
        audio_segments = []
        for x in range(stop + 1):
            segment = generate_tone(timeline.get(x, 0), brush)
            audio_segments.append(segment)
       
        audio = np.concatenate(audio_segments)
        audio = audio / np.max(np.abs(audio))
        audio_int16 = np.int16(audio * 32767)
        filename = f"sound_{int(time.time() * 1000)}.wav"
        filepath = os.path.join(OUTPUT_DIR, filename)
        write_wav(filepath, SAMPLE_RATE, audio_int16)
        logger.info(f"Generated audio file: {filename}")
        # Store submission in database
        insert_query = """
            INSERT INTO submissions (user_email, submission_date, image_data, audio_path, brush_type, ip_address)
            OUTPUT INSERTED.submission_id
            VALUES (?, ?, ?, ?, ?, ?)
        """
        cursor.execute(insert_query, (
            session['user']['email'] if is_authenticated else None,
            datetime.now(),
            image_data,
            filename,
            brush,
            request.remote_addr
        ))
        submission_id = cursor.fetchone()[0]
        connection.commit()
        logger.info(f"Submission {submission_id} stored in database for {submission_key}")
        # Update billing record with submission_id if applicable
        if is_authenticated and is_subscribed and submission_count >= FREE_SUBMISSION_LIMIT:
            cursor.execute("""
                UPDATE billing_records
                SET submission_id = ?
                WHERE submission_id IS NULL AND user_email = ? AND created_at = (SELECT MAX(created_at) FROM billing_records WHERE user_email = ?)
            """, (submission_id, submission_key, submission_key))
            connection.commit()
            logger.info(f"Updated billing record with submission_id {submission_id} for {submission_key}")
        return jsonify({"url": f"/static/audio/{filename}"})
    except Exception as e:
        logger.error(f"Error processing submission: {str(e)}")
        return jsonify({"error": f"Failed to process submission: {str(e)}"}), 500
    finally:
        if connection:
            cursor.close()
            connection.close()
            logger.info("Database connection closed")
@app.route('/static/audio/<path:filename>')
def serve_audio(filename):
    logger.info(f"Serving audio file: {filename}")
    return send_from_directory(OUTPUT_DIR, filename)
if __name__ == "__main__":
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    port = int(os.getenv('PORT', 8000))
    app.run(host="0.0.0.0", port=port, debug=debug, use_reloader=False, threaded=False)
else:
    application = app # For Gunicor















