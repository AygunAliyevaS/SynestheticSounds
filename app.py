import matplotlib
matplotlib.use('Agg') 

import colorsys
import time
from flask import Flask, render_template, request,session,send_from_directory,jsonify
import numpy as np
import librosa
import librosa.display
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import io
import os
import base64
from music_visualizer import process_audio_to_gif

from io import BytesIO
from PIL import Image
from colorsys import rgb_to_hsv
from scipy.io.wavfile import write as write_wav


from PIL import Image, ImageDraw, ImageFont
import string
from docx import Document
import PyPDF2
import pdfplumber
import soundfile as sf
#import sounddevice as sd
from scipy.io.wavfile import write
import matplotlib.pyplot as plt
from scipy.fft import fft
import io
import base64
import pandas as pd
from pydub import AudioSegment
from werkzeug.utils import secure_filename
from dash import dcc, html
import dash_core_components as dcc
from dash import Dash, dcc, html, callback, Input, Output
import plotly.graph_objs as go
import plotly.express as px
global session

import numpy as np
from numpy.random import uniform
from scipy import signal

app = Flask(__name__)
app.secret_key = 'Lantop2333'  # Set a secret key session

app = Flask(__name__)
OUTPUT_DIR = "static/audio"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Assuming DURATION_PER_STEP and SAMPLE_RATE are defined globally or passed in
# For demonstration, let's define them here:
# DURATION_PER_STEP = 1  # seconds
SAMPLE_RATE = 44100      # Hz
DURATION_PER_STEP = (60)/1000  # seconds per X step (column)

NOTE_TO_SEMITONE = {
    'C': 0, 'C#': 1, 'D': 2, 'D#': 3,
    'E': 4, 'F': 5, 'F#': 6, 'G': 7,
    'G#': 8, 'A': 9, 'A#': 10, 'B': 11
}
note_names = list(NOTE_TO_SEMITONE.keys())


dash_app = Dash(__name__, server=app, url_base_pathname='/dash/')


Fs = 44100  # Sampling frequency

# Frequency ranges and names of piano notes
notes = ['A0', 'A#0/Bb0', 'B0', 'C1', 'C#1/Db1', 'D1', 'D#1/Eb1', 'E1', 'F1', 'F#1/Gb1', 'G1', 'G#1/Ab1', 'A1', 
         'A#1/Bb1', 'B1', 'C2', 'C#2/Db2', 'D2', 'D#2/Eb2', 'E2', 'F2', 'F#2/Gb2', 'G2', 'G#2/Ab2', 'A2', 
         'A#2/Bb2', 'B2', 'C3', 'C#3/Db3', 'D3', 'D#3/Eb3', 'E3', 'F3', 'F#3/Gb3', 'G3', 'G#3/Ab3', 'A3', 
         'A#3/Bb3', 'B3', 'C4', 'C#4/Db4', 'D4', 'D#4/Eb4', 'E4', 'F4', 'F#4/Gb4', 'G4', 'G#4/Ab4', 'A4', 
         'A#4/Bb4', 'B4', 'C5', 'C#5/Db5', 'D5', 'D#5/Eb5', 'E5', 'F5', 'F#5/Gb5', 'G5', 'G#5/Ab5', 'A5', 
         'A#5/Bb5', 'B5', 'C6', 'C#6/Db6', 'D6', 'D#6/Eb6', 'E6', 'F6', 'F#6/Gb6', 'G6', 'G#6/Ab6', 'A6', 
         'A#6/Bb6', 'B6', 'C7', 'C#7/Db7', 'D7', 'D#7/Eb7', 'E7', 'F7', 'F#7/Gb7', 'G7', 'G#7/Ab7', 'A7', 
         'A#7/Bb7', 'B7', 'C8']
freqs_org = [27.50, 29.14, 30.87, 32.70, 34.65, 36.71, 38.89, 41.20, 43.65, 46.25, 49.00, 51.91, 55.00, 58.27, 
         61.74, 65.41, 69.30, 73.42, 77.78, 82.41, 87.31, 92.50, 98.00, 103.83, 110.00, 116.54, 123.47, 
         130.81, 138.59, 146.83, 155.56, 164.81, 174.61, 185.00, 196.00, 207.65, 220.00, 233.08, 246.94, 
         261.63, 277.18, 293.66, 311.13, 329.63, 349.23, 369.99, 392.00, 415.30, 440.00, 466.16, 493.88, 
         523.25, 554.37, 587.33, 622.25, 659.25, 698.46, 739.99, 783.99, 830.61, 880.00, 932.33, 987.77, 
         1046.50, 1108.73, 1174.66, 1244.51, 1318.51, 1396.91, 1479.98, 1567.98, 1661.22, 1760.00, 
         1864.66, 1975.53, 2093.00, 2217.46, 2349.32, 2489.02, 2637.02, 2793.83, 2959.96, 3135.96, 
         3322.44, 3520.00, 3729.31, 3951.07, 4186.01]

# Set colors for each frequency
colors = [[139/255, 0, 0]] * len(freqs_org)
sounds = {				
'A': (0, 100, 0),  # Dark Green+I1:I31
'B': (255, 127, 80), # Coral
'C': (210, 180, 140),   # Light Brown
'Ç': (205, 170, 100), # Light golden brown
'D': (255, 165, 0), # Orange
'E': (0, 255, 255), # Light Blue
'Ə': (230, 230, 250), # Lavender
'F': (139, 0, 139), # Dark Magenta
'G': (255, 215, 0), # Gold
'Ğ':  (184, 134, 11),  # Golden brown
'H': (128, 128, 0), # Olive
'X':  (50, 60, 30),   # Dark brown green
'I': (100, 200, 200), # light sea wave
'İ': (46, 139, 87),  # Sea Wave
'J': (221, 160, 221),  # Plum
'K': (255, 0, 255), # Magenta
'Q': (153, 50, 204),  # Dark blue magenta
'L': (0, 0, 255),   # Blue
'M': (255, 0, 0), # Red
'N': (255, 255, 0), # Yellow
'O': (50, 205, 50), # Lime
'Ö': (50, 70, 0), # Dark lime
'P': (255, 255, 224), # Light Yellow
'R':(255, 250, 205), # Lemon
'S': (255, 182, 193),  # Light Pink
'Ş': (210, 105, 30), # Chocolate
'T': (189, 252, 201),  # Mint
'U': (64, 224, 208), # Turquoise
'Ü': (0, 255, 0), # Green ŋ
'V': (250, 128, 114), # Salmon
'Y': (35, 70, 70),   # Dark green blue
'a': (0, 100, 0),  # Dark Green
'b': (255, 127, 80), # Coral
'c': (210, 180, 140),   # Light Brown
'd': (255, 165, 0), # Orange
'e': (0, 255, 255), # Light Blue
'f': (139, 0, 139), # Dark Magenta
'g': (255, 215, 0), # Gold
'h': (128, 128, 0), # Olive
'i': (46, 139, 87),  # Sea Wave
'j': (250, 128, 114),   # Salmon
'k': (255, 0, 255), # Magenta
'l': (0, 0, 255),   # Blue
'm': (255, 0, 0), # Red
'n': (255, 255, 0), # Yellow
'o': (50, 205, 50), # Lime
'p': (139, 0, 0), # Dark Red
'q': (153, 50, 204),   # Dark blue magenta
'r': (255, 250, 205), # Lemon
's': (255, 182, 193),  # Light Pink
't': (0, 0, 139),  # Dark Blue
'u': (64, 224, 208), # Turquoise
'v': (255, 192, 203), # Pink
'w': (255, 255, 224), # Light Yellow
'x': (50, 60, 30),   # Dark brown green
'y': (35, 70, 70),   # Dark green blue
'z': (165, 42, 42), # Brown
'th': (189, 252, 201),  # Mint
'sh': (210, 105, 30), # Chocolate
'ing': (0, 255, 0), #Green ŋ
'isi': (250, 128, 114), # Salmon
'ʌ': (65, 105, 225),  # Royal Blue
'æ': (230, 230, 250),  # Lavender
 'æ': (230, 230, 250),
'Ə' :(230, 230, 250),
'Ğ':(184, 134, 11),  # Golden brown
'ğ':  (184, 134, 11),  # Golden brown
'ə': (230, 230, 250),
'Ş':(210, 105, 30), # Chocolate
'ş': (210, 105, 30), # Chocolate
    "ʒ":  (250, 128, 114),  # Salmon
    "ʃ": (210, 105, 30),  # Chocolate
    "z": (165, 42, 42),  # Brown
    "θ": (255, 140, 0),  # Dark Orange
   'Ü':(0, 255, 0), # Green ŋ
   'ü': (0, 255, 0), # Green ŋ
'Ö':(50, 70, 0), # Dark lime
'ö': (50, 70, 0), # Dark lime
'Ç': (205, 170, 100), # Light golden brown
'ç': (205, 170, 100) # Light golden brown
    
}

def read_docx(file):
    doc = Document(file)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return '\n'.join(full_text)

def read_pdf(file):
    full_text = []
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            full_text.append(page.extract_text())
    return '\n'.join(full_text)

def split_image_into_chunks(image, chunk_size):
    width, height = image.size
    chunks = []
    for i in range(0, width, chunk_size):
        chunk = image.crop((i, 0, min(i + chunk_size, width), height))
        buf = io.BytesIO()
        chunk.save(buf, format='PNG')
        buf.seek(0)
        chunks.append(base64.b64encode(buf.getvalue()).decode())
    return chunks

def generate_color_palette():
    chars = string.digits + string.ascii_lowercase + string.ascii_uppercase + '!?., '
    palette = {}
    '''
    num_colors = len(chars)
    for i, char in enumerate(chars):
        hue = i**2 / num_colors   
        lightness = 0.3 + (i % 2) * 0.4 
        saturation = 0.8 + (i % 3) * 0.6 
        rgb = colorsys.hls_to_rgb(hue, lightness, saturation)
        rgb = tuple(int(255 * x) for x in rgb)
        palette[char] = rgb
    '''
    palette['A']  = (200,200,200)
    palette['b'] = (165,0,165)
    palette['c'] = (100,200,255)
    
    for s in sounds:
        p=sounds[s]
        palette[s]=p
    
    print('pppp',palette)
    return palette

def char_to_color(char, palette):
    return palette.get(char, (100,100,100)) 

def color_to_char(color, palette):
    for char, col in palette.items():
        if col == color:
            return char
    return '?'

def string_to_color_pattern(input_string, palette, cell_width=200, cell_height=150):
    length = len(input_string)
    width=0
    for t in input_string:
        if t.islower():
            width+=cell_width
        else:
            width+=int(cell_width*1.5)
        
    #width = length * cell_width
    height = cell_height + cell_height // 2  
    image = Image.new("RGB", (width, height), (255, 255, 255))  
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default(size=50)

    color_code = []
    for i, char in enumerate(input_string):
        if char.islower():
            color = char_to_color(char, palette)
            color_code.append(color)
            top_left = (i * cell_width, 0)
            bottom_right = ((i + 1) * cell_width, cell_height)
            draw.rectangle([top_left, bottom_right], fill=color)
            text_width, text_height = 20,20
            text_x = top_left[0] + (cell_width - text_width) / 2
            text_y = cell_height + (cell_height // 2 - text_height) / 2
            font = ImageFont.load_default(size=50)
            draw.text((text_x, text_y), char, fill=(0, 0, 0), font=font, stroke_width=1)
        else:
            color = char_to_color(char, palette)
            color_code.append(color)
            top_left = (i * cell_width, 0)
            bottom_right = ((i + 1) * cell_width*1.5, cell_height)
            draw.rectangle([top_left, bottom_right], fill=color)
            text_width, text_height = 50,30
            text_x = top_left[0] + (cell_width*1.1 - text_width) / 2
            text_y = cell_height + (cell_height // 2 - text_height) / 2 - 20
            font = ImageFont.load_default(size=65)
            draw.text((text_x, text_y), char, fill=(0, 0, 0), font=font, stroke_width=3)
            
    
    return image, color_code

def color_code_to_string(color_code, palette):
    return ''.join(color_to_char(tuple(color), palette) for color in color_code)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_audio():
    global session
    
    if 'file' not in request.files:
        return render_template('index.html', error="No file part")
    file = request.files['file']
    if file.filename == '':
        return render_template('index.html', error="No selected file")
    if file:
        y, sr = librosa.load(file)

        
        #y = y.reshape(-1, 1)

        if y.ndim > 1 and y.shape[1] > 1:
            print("Audio has more than one channel. Using the first channel.")
            y = y[:, 0]  # Select the first channel
    
        if len(y)>Fs*2.0*60:
            y=y[:int(Fs*2.0*60)]
        '''
        D = np.abs(librosa.stft(y))
        D_db = librosa.amplitude_to_db(D, ref=np.max)
        
        num_colors = 256
        colors = [(0, 'black')]
        for i in range(1, num_colors):
            frequency = i / num_colors * (sr / 2)
            hue = frequency / (sr / 2)
            colors.append((i / (num_colors - 1), plt.cm.hsv(hue)[:3]))
        
        cmap = mcolors.LinearSegmentedColormap.from_list("custom_colormap", colors)
        
        fig, ax = plt.subplots(figsize=(10, 4))
        img = librosa.display.specshow(D_db, sr=sr, x_axis='time', y_axis='log', cmap=cmap, ax=ax)
        cbar = fig.colorbar(img, ax=ax, format='%+2.0f dB')
        cbar.set_label('Decibels')
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0)
        buf.seek(0)
        plot_url = base64.b64encode(buf.getvalue()).decode()
        '''

        # Save the uploaded file temporarily
        #temp_filename = 'uploaded_audio.wav' if file.filename.endswith('.wav') else 'uploaded_audio.mp3'
        #file.save(temp_filename)
        
        frequencies,amplitudes= process_audio(y)
        
        # Store frequency data for Dash
        frequency_data = {
            'frequencies': frequencies,
            'amplitudes': amplitudes
        }
        #session['frequency_data'] = frequency_data

        df=pd.DataFrame(frequency_data)
        os.remove('freq.csv')     
        df.to_csv('freq.csv',index=0)
        
        # here plot_url=plot_url
        return render_template('color_representation.html')

@app.route('/text-to-color', methods=['GET', 'POST'])
def text_to_color():
    if request.method == 'POST':
        input_string = ""
        if 'text' in request.form and request.form['text']:
            input_string = request.form['text']
        elif 'file' in request.files and request.files['file'].filename:
            file = request.files['file']
            filename = file.filename.lower()
            if filename.endswith('.txt'):
                input_string = file.read().decode('utf-8')
            elif filename.endswith('.docx'):
                input_string = read_docx(file)
            elif filename.endswith('.pdf'):
                input_string = read_pdf(file)
            else:
                return render_template('text_to_color.html', error="Unsupported file format")
        else:
            return render_template('text_to_color.html', error="No input provided")
        
        palette = generate_color_palette()
        
        image, color_code = string_to_color_pattern(input_string, palette)
        
        image_chunks = split_image_into_chunks(image, chunk_size=200)  

        return render_template('text_to_color_representation.html', image_chunks=image_chunks, color_code=color_code)

    return render_template('text_to_color.html')

@app.route('/color-to-text', methods=['GET', 'POST'])
def color_to_text():
    if request.method == 'POST':
        if 'color_code' in request.form and request.form['color_code']:
            color_code_input = request.form['color_code']
            print('strip',color_code_input.strip())
            color_code = color_code_input.strip().strip('][').split('),')
            cz = []
            for x in color_code:
                z = x.strip().strip('(').strip(')')
                z = z.split(',')
                u,v,w = z
                z = (int(u),int(v),int(w))
                cz.append(tuple(z))
            print(cz)
            print(color_code)
            palette = generate_color_palette()
            original_text = color_code_to_string(cz, palette)
            return render_template('color_to_text.html', original_text=original_text, color_code=color_code_input)
        else:
            return render_template('color_to_text.html', error="No input provided")
    return render_template('color_to_text.html')

colors = plt.cm.Set1(np.linspace(0, 1, len(freqs_org)))  # Choose your preferred colormap

frequency_colors_update = {
    "m_as_in_mat": {"range": (100, 200), "color": (255, 0, 0)},  # Red
    "p_as_in_pat": {"range": (100, 200), "color": (139, 0, 0)},  # Dark Red
    "b_as_in_bat": {"range": (100, 300), "color": (255, 127, 80)},  # Coral
    "d_as_in_dog": {"range": (200, 400), "color": (255, 165, 0)},  # Orange
    "g_as_in_go": {"range": (200, 600), "color": (255, 215, 0)},  # Gold
    "n_as_in_no": {"range": (200, 600), "color": (255, 255, 0)},  # Yellow
    "w_as_in_wet": {"range": (200, 1000), "color": (255, 255, 224)},  # Light Yellow
    "r_as_in_rat": {"range": (200, 1000), "color": (255, 250, 205)},  # Lemon
    "ŋ_as_in_sing": {"range": (200, 1000), "color": (0, 255, 0)},  # Green

    # Mid Frequency Sounds
    "ɑ_as_in_father": {"range": (700, 1100), "color": (0, 100, 0)},  # Dark Green
    "o_as_in_pot": {"range": (300, 1500), "color": (50, 205, 50)},  # Lime
    "h_as_in_hat": {"range": (1000, 2000), "color": (128, 128, 0)},  # Olive
    "ð_as_in_this": {"range": (1000, 3000), "color": (189, 252, 201)},  # Mint
    "e_as_in_bed": {"range": (400, 2000), "color": (0, 255, 255)},  # Light Blue
    "u_as_in_put": {"range": (250, 2000), "color": (64, 224, 208)},  # Turquoise
    "i_as_in_sit": {"range": (250, 3000), "color": (46, 139, 87)},  # Sea Wave
    "a_as_in_cat": {"range": (500, 2500), "color": (135, 206, 235)},  # Sky Blue
    "l_as_in_lamp": {"range": (300, 3000), "color": (0, 0, 255)},  # Blue
    "t_as_in_top": {"range": (300, 3000), "color": (0, 0, 139)},  # Dark Blue
    "ʌ_as_in_cup": {"range": (500, 1500), "color": (65, 105, 225)},  # Royal Blue
    "ə_as_in_sofa": {"range": (500, 1500), "color": (128, 0, 128)},  # Violet
    "j_as_in_jump": {"range": (500, 2000), "color": (221, 160, 221)},  # Plum
    "æ_as_in_cat": {"range": (500, 2500), "color": (230, 230, 250)},  # Lavender

    # High Frequency Sounds
    "k_as_in_kite": {"range": (1500, 4000), "color": (255, 0, 255)},  # Magenta
    "f_as_in_fish": {"range": (1700, 2000), "color": (139, 0, 139)},  # Dark Magenta
    "v_as_in_vet": {"range": (200, 5000), "color": (255, 192, 203)},  # Pink
    "s_as_in_sat": {"range": (2000, 5000), "color": (255, 182, 193)},  # Light Pink
    "ʒ_as_in_measure": {"range": (2000, 5000), "color": (250, 128, 114)},  # Salmon
    "ʃ_as_in_she": {"range": (2000, 8000), "color": (210, 105, 30)},  # Chocolate
    "z_as_in_zoo": {"range": (3000, 7000), "color": (165, 42, 42)},  # Brown
    "θ_as_in_thin": {"range": (6000, 8000), "color": (255, 140, 0)}  # Dark Orange
}


frequency_colors_update = {
    "A0": {"frequency": 27.50, "color": (139, 0, 0), "range": (27.50, 29.14)},
    "A#0/Bb0": {"frequency": 29.14, "color": (255, 69, 0), "range": (29.14, 30.87)},
    "B0": {"frequency": 30.87, "color": (204, 204, 0), "range": (30.87, 32.70)},
    "C1": {"frequency": 32.70, "color": (102, 152, 0), "range": (32.70, 34.65)},
    "C#1/Db1": {"frequency": 34.65, "color": (0, 100, 0), "range": (34.65, 36.71)},
    "D1": {"frequency": 36.71, "color": (0, 50, 69), "range": (36.71, 38.89)},
    "D#1/Eb1": {"frequency": 38.89, "color": (0, 0, 139), "range": (38.89, 41.20)},
    "E1": {"frequency": 41.20, "color": (75, 0, 130), "range": (41.20, 43.65)},
    "F1": {"frequency": 43.65, "color": (112, 0, 171), "range": (43.65, 46.25)},
    "F#1/Gb1": {"frequency": 46.25, "color": (148, 0, 211), "range": (46.25, 49.00)},
    "G1": {"frequency": 49.00, "color": (157, 0, 106), "range": (49.00, 51.91)},
    "G#1/Ab1": {"frequency": 51.91, "color": (165, 0, 0), "range": (51.91, 55.00)},
    "A1": {"frequency": 55.00, "color": (210, 0, 128), "range": (55.00, 58.27)},
    "A#1/Bb1": {"frequency": 58.27, "color": (255, 94, 0), "range": (58.27, 61.74)},
    "B1": {"frequency": 61.74, "color": (221, 221, 0), "range": (61.74, 65.41)},
    "C2": {"frequency": 65.41, "color": (111, 175, 0), "range": (65.41, 69.30)},
    "C#2/Db2": {"frequency": 69.30, "color": (0, 128, 0), "range": (69.30, 73.42)},
    "D2": {"frequency": 73.42, "color": (0, 64, 85), "range": (73.42, 77.78)},
    "D#2/Eb2": {"frequency": 77.78, "color": (0, 0, 170), "range": (77.78, 82.41)},
    "E2": {"frequency": 82.41, "color": (92, 0, 159), "range": (82.41, 87.31)},
    "F2": {"frequency": 87.31, "color": (119, 0, 96), "range": (87.31, 92.50)},
    "F#2/Gb2": {"frequency": 92.50, "color": (159, 0, 226), "range": (92.50, 98.00)},
    "G2": {"frequency": 98.00, "color": (175, 0, 113), "range": (98.00, 103.83)},
    "G#2/Ab2": {"frequency": 103.83, "color": (191, 0, 0), "range": (103.83, 110.00)},
    "A2": {"frequency": 110.00, "color": (223, 59, 128), "range": (110.00, 116.54)},
    "A#2/Bb2": {"frequency": 116.54, "color": (255, 119, 0), "range": (116.54, 123.47)},
    "B2": {"frequency": 123.47, "color": (238, 238, 0), "range": (123.47, 130.81)},
    "C3": {"frequency": 130.81, "color": (119, 159, 0), "range": (130.81, 138.59)},
    "C#3/Db3": {"frequency": 138.59, "color": (0, 160, 0), "range": (138.59, 146.83)},
    "D3": {"frequency": 146.83, "color": (0, 80, 100), "range": (146.83, 155.56)},
    "D#3/Eb3": {"frequency": 155.56, "color": (0, 0, 200), "range": (155.56, 164.81)},
    "E3": {"frequency": 164.81, "color": (109, 0, 188), "range": (164.81, 174.61)},
    "F3": {"frequency": 174.61, "color": (140, 0, 215), "range": (174.61, 185.00)},
    "F#3/Gb3": {"frequency": 185.00, "color": (170, 0, 241), "range": (185.00, 196.00)},
    "G3": {"frequency": 196.00, "color": (194, 0, 121), "range": (196.00, 207.65)},
    "G#3/Ab3": {"frequency": 207.65, "color": (217, 0, 0), "range": (207.65, 220.00)},
    "A3": {"frequency": 220.00, "color": (236, 72, 0), "range": (220.00, 233.08)},
    "A#3/Bb3": {"frequency": 233.08, "color": (255, 144, 0), "range": (233.08, 246.94)},
    "B3": {"frequency": 246.94, "color": (255, 255, 0), "range": (246.94, 261.63)},
    "C4": {"frequency": 261.63, "color": (128, 224, 0), "range": (261.63, 277.18)},
    "C#4/Db4": {"frequency": 277.18, "color": (0, 192, 0), "range": (277.18, 293.66)},
    "D4": {"frequency": 293.66, "color": (0, 96, 115), "range": (293.66, 311.13)},
    "D#4/Eb4": {"frequency": 311.13, "color": (0, 0, 230), "range": (311.13, 329.63)},
    "E4": {"frequency": 329.63, "color": (126, 0, 217), "range": (329.63, 349.23)},
    "F4": {"frequency": 349.23, "color": (159, 26, 236), "range": (349.23, 369.99)},
    "F#4/Gb4": {"frequency": 369.99, "color": (191, 51, 255), "range": (369.99, 392.00)},
    "G4": {"frequency": 392.00, "color": (217, 26, 128), "range": (392.00, 415.30)},
    "G#4/Ab4": {"frequency": 415.30, "color": (243, 0, 0), "range": (415.30, 440.00)},
    "A4": {"frequency": 440.00, "color": (249, 85, 0), "range": (440.00, 466.16)},
    "A#4/Bb4": {"frequency": 466.16, "color": (255, 169, 0), "range": (466.16, 493.88)},
    "B4": {"frequency": 493.88, "color": (255, 255, 51), "range": (493.88, 523.25)},
    "C5": {"frequency": 523.25, "color": (153, 255, 51), "range": (523.25, 554.37)},
    "C#5/Db5": {"frequency": 554.37, "color": (51, 255, 51), "range": (554.37, 587.33)},
    "D5": {"frequency": 587.33, "color": (51, 204, 204), "range": (587.33, 622.25)},
    "D#5/Eb5": {"frequency": 622.25, "color": (51, 51, 255), "range": (622.25, 659.25)},
    "E5": {"frequency": 659.25, "color": (128, 51, 255), "range": (659.25, 698.46)},
    "F5": {"frequency": 698.46, "color": (159, 87, 255), "range": (698.46, 739.99)},
    "F#5/Gb5": {"frequency": 739.99, "color": (190, 123, 255), "range": (739.99, 783.99)},
    "G5": {"frequency": 783.99, "color": (204, 87, 128), "range": (783.99, 830.61)},
    "G#5/Ab5": {"frequency": 830.61, "color": (255, 51, 51), "range": (830.61, 880.00)},
    "A5": {"frequency": 880.00, "color": (255, 128, 102), "range": (880.00, 932.33)},
    "A#5/Bb5": {"frequency": 932.33, "color": (255, 204, 102), "range": (932.33, 987.77)},
    "B5": {"frequency": 987.77, "color": (255, 255, 102), "range": (987.77, 1046.50)},
    "C6": {"frequency": 1046.50, "color": (179, 255, 102), "range": (1046.50, 1108.73)},
    "C#6/Db6": {"frequency": 1108.73, "color": (102, 255, 102), "range": (1108.73, 1174.66)},
    "D6": {"frequency": 1174.66, "color": (102, 204, 204), "range": (1174.66, 1244.51)},
    "D#6/Eb6": {"frequency": 1244.51, "color": (102, 102, 255), "range": (1244.51, 1318.51)},
    "E6": {"frequency": 1318.51, "color": (153, 102, 255), "range": (1318.51, 1396.91)},
    "F6": {"frequency": 1396.91, "color": (177, 128, 255), "range": (1396.91, 1479.98)},
    "F#6/Gb6": {"frequency": 1479.98, "color": (201, 153, 255), "range": (1479.98, 1567.98)},
    "G6": {"frequency": 1567.98, "color": (209, 128, 153), "range": (1567.98, 1661.22)},
    "G#6/Ab6": {"frequency": 1661.22, "color": (255, 102, 102), "range": (1661.22, 1760.00)},
    "A6": {"frequency": 1760.00, "color": (255, 153, 128), "range": (1760.00, 1864.66)},
    "A#6/Bb6": {"frequency": 1864.66, "color": (255, 204, 153), "range": (1864.66, 1975.53)},
    "B6": {"frequency": 1975.53, "color": (255, 255, 153), "range": (1975.53, 2093.00)},
    "C7": {"frequency": 2093.00, "color": (204, 255, 153), "range": (2093.00, 2217.46)},
    "C#7/Db7": {"frequency": 2217.46, "color": (153, 255, 153), "range": (2217.46, 2349.32)},
    "D7": {"frequency": 2349.32, "color": (153, 204, 204), "range": (2349.32, 2489.02)},
    "D#7/Eb7": {"frequency": 2489.02, "color": (153, 153, 255), "range": (2489.02, 2637.02)},
    "E7": {"frequency": 2637.02, "color": (197, 153, 255), "range": (2637.02, 2793.83)},
    "F7": {"frequency": 2793.83, "color": (222, 176, 255), "range": (2793.83, 2959.96)},
    "F#7/Gb7": {"frequency": 2959.96, "color": (246, 198, 255), "range": (2959.96, 3135.96)},
    "G7": {"frequency": 3135.96, "color": (251, 176, 204), "range": (3135.96, 3322.44)},
    "G#7/Ab7": {"frequency": 3322.44, "color": (255, 153, 153), "range": (3322.44, 3520.00)},
    "A7": {"frequency": 3520.00, "color": (255, 194, 176), "range": (3520.00, 3729.31)},
    "A#7/Bb7": {"frequency": 3729.31, "color": (255, 234, 198), "range": (3729.31, 3951.07)},
    "B7": {"frequency": 3951.07, "color": (255, 255, 204), "range": (3951.07, 4186.01)},
    "C8": {"frequency": 4186.01, "color": (144, 238, 144), "range": (4186.01, 4434.92)}
}





@app.route('/record', methods=['GET', 'POST'])
def record():
    if request.method == 'POST':
        if 'file' in request.files:
            # Handle file upload
            audio_file = request.files['file']
            if audio_file.filename.endswith(('.mp3', '.wav')):
                
                # Save the uploaded file temporarily
                temp_filename = 'uploaded_audio.wav' if audio_file.filename.endswith('.wav') else 'uploaded_audio.mp3'
                audio_file.save(temp_filename)

                # Read audio data using soundfile
                audio_data, sample_rate = sf.read(temp_filename)

                #audio_segment.export('uploaded_audio.wav', format='wav')

                #audio_data = np.array(audio_segment.get_array_of_samples())
                audio_data = audio_data.reshape(-1, 1)
                return process_audio(audio_data)
            else:
                return 'Unsupported file format. Please upload MP3 or WAV.', 400
        else:
            # Handle recording
            duration = int(request.form['duration'])
            print("Recording starts...")
            audio_data = sd.rec(int(duration * Fs), samplerate=Fs, channels=1, dtype='float64')
            sd.wait()
            print("Recording completed.")
            return process_audio(audio_data)

    return render_template('frequency_plot.html', spectrum_image=None)

def process_audio(audio_data):
    if audio_data.ndim > 1 and audio_data.shape[1] > 1:
        print("Audio has more than one channel. Using the first channel.")
        audio_data = audio_data[:, 0]  # Select the first channel
        
    L = len(audio_data)
    Y = fft(audio_data.flatten())
    P2 = np.abs(Y / L)
    P1 = P2[:L // 2 + 1]
    P1[1:-1] = 2 * P1[1:-1]
    f = Fs * np.arange((L // 2) + 1) / L   
            
    return f,P1
    #return f'<h2>Frequency Spectrum</h2><img src="data:image/png;base64,{plot_url}" alt="Frequency Spectrum">'

@app.route('/upload', methods=['POST'])
def upload_file():
    return record()  # Delegate to the record function

@dash_app.callback(
    Output('bar-chart', 'figure'),
    [Input('frequency-data', 'data')]
)

@dash_app.callback(
    Output('bar-chart', 'figure'),
    [Input('frequency-data', 'data')]
)
def update_bar_chart(frequency_data):
    if not frequency_data:
        return go.Figure()  # Return empty figure if no data

    freqq=pd.read_csv('freq.csv')
                
    frequency_data=freqq
    frequencies = list(frequency_data['frequencies'])
    amplitudes = list(frequency_data['amplitudes'])
         
    # Convert received data into a DataFrame
    df = pd.DataFrame(frequency_data)

    frequencies = list(df['frequencies'])
    amplitudes = list(df['amplitudes'])

    fig = go.Figure(data=[
        go.Bar(
            x=frequencies,
            y=amplitudes,
            marker_color='rgba(0, 100, 200, 0.6)' 
        )
    ])

    box_traces = []
    for note in frequency_colors_update:
        lower_bound, upper_bound = frequency_colors_update[note]["range"]
        freq_data = df[(df['Frequency'] > lower_bound) & (df['Frequency'] < upper_bound)]

        if not freq_data.empty:
            box_traces.append(go.Box(
                y=freq_data['Amplitude'],  
                name=note,
                marker_color=f'rgba({",".join(map(str, frequency_colors_update[note]["color"]))}, 0.6)'
            ))

    fig.add_traces(box_traces)

    fig.update_layout(
        title='Frequency vs Amplitude',
        xaxis_title='Frequency',
        yaxis_title='Amplitude'
    )

    return fig


# Layout for Dash app
df = px.data.gapminder()
fig = px.bar(df[df["year"] == 2007], x="continent", y="pop", title="Population by Continent")
freqq=pd.read_csv('freq.csv')
                
frequency_data=freqq
frequencies = list(frequency_data['frequencies'])
amplitudes = list(frequency_data['amplitudes'])
# Convert received data into a DataFrame
df = pd.DataFrame(frequency_data)

frequency_data['notes']=['aaa']*len(frequency_data)
colors=[]
for note in frequency_colors_update:
        lower_bound, upper_bound = frequency_colors_update[note]["range"]
        freq_data = frequency_data[(frequency_data['frequencies'] > lower_bound) & (frequency_data['frequencies'] < upper_bound)]
        frequency_data.loc[freq_data.index.tolist(),'notes']=note
        colors.append(f'rgba({",".join(map(str, frequency_colors_update[note]["color"]))}, 0.6)')




frequency_data=frequency_data[frequency_data['notes']!='aaa']

frequency_data2=frequency_data.groupby('notes').sum()
frequency_data2=frequency_data2.reset_index()
frequency_data2=frequency_data2.sample(len(frequency_data2))
idx=frequency_data2.index.tolist()
colors=[colors[i] for i in idx]
print(frequency_data.head())

fig2 = px.bar(frequency_data2, x="notes", y="amplitudes", title="Amplitude vs Frequency")
fig2.update_traces(marker_color=colors)

dash_app.layout = html.Div([  
    dcc.Graph(id='bar-chart',figure=fig2)
    #dcc.Store(id='frequency-data', data={}),  # To store frequency data
    #dcc.Graph(id='bar-chart',figure=update_bar_chart(None)),
    #html.Div(id='graph-container', style={'display': 'none'})  # Hidden div for handling updates
])

# Callback to load frequency data from session when a request is made
@dash_app.callback(
    Output('frequency-data', 'data'),
    [Input('bar-chart', 'id')]  # Dummy input to trigger callback
)
def load_frequency_data(_):
    frequency_data = session.get('frequency_data', {})
    return frequency_data  # Return the data to the Store

# Config
UPLOAD_FOLDER = 'static/uploads'
OUTPUT_FOLDER = 'static/output'
ALLOWED_EXTENSIONS = {'wav', 'mp3', 'ogg', 'flac'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/process_gif', methods=['GET', 'POST'])
def process_gif():
    gif_filename = None

    if request.method == 'POST':
        if 'audio' not in request.files:
            return 'No file part'

        file = request.files['audio']
        if file.filename == '':
            return 'No selected file'

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            gif_filename = os.path.splitext(filename)[0] + '.gif'
            gif_filename = 'music.png'
            gif_path = os.path.join(app.config['OUTPUT_FOLDER'], gif_filename)
            print('here',gif_path)

            # Process uploaded audio and generate GIF
            process_audio_to_gif(filepath, gif_path)
   
    return render_template('index.html', gif_file=gif_filename)


@app.route('/static/output/<filename>')
def serve_gif(filename):
    return send_from_directory(app.config['OUTPUT_FOLDER'], filename)
    
@app.route('/download/<filename>')
def download_gif(filename):
    return send_from_directory(app.config['OUTPUT_FOLDER'], filename, as_attachment=True)


def hue_to_note_name(hue):
    index = int((hue % 360) / 30)
    return note_names[index]

def brightness_to_octave(brightness):
    return int(3 + brightness * 3)

freq_symbols={
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
    "B3": {"frequency": 246.94, "color": [250, 250, 0], "range": [246.94, 261.63], "symbol": "♩"},

    "C4": {"frequency": 261.63, "color": [128, 224, 0], "range": [261.63, 277.18], "symbol": "♩"},
    "C#4/Db4": {"frequency": 277.18, "color": [0, 192, 0], "range": [277.18, 293.66], "symbol": "♯"},
    "D4": {"frequency": 293.66, "color": [0, 96, 115], "range": [293.66, 311.13], "symbol": "♩"},
    "D#4/Eb4": {"frequency": 311.13, "color": [0, 0, 230], "range": [311.13, 329.63], "symbol": "♯"},
    "D#4": {"frequency": 311.13, "color": [0, 0, 230], "range": [311.13, 329.63], "symbol": "♯"},
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
    "D#5/Eb5": {"frequency": 622.25, "color": [51, 51, 255], "range": [622.25, 659.26], "symbol": "♭"},
    "E5": {"frequency": 659.26, "color": [128, 51, 255], "range": [659.26, 698.46], "symbol": "𝅘𝅥𝅮"},
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
    "A7": {"frequency": 3520.00, "color": [255, 194, 176], "range": [3520.00, 3729.32], "symbol": "𝅗𝅥"},
    "A#7/Bb7": {"frequency": 3729.32, "color": [255, 234, 198], "range": [3729.32, 3951.07], "symbol": "♯"},
   "B7": {"frequency": 3951.07, "color": [255, 255, 204], "range": [3951.07, 4186.01], "symbol": "𝅘𝅥"},
    
        "C8": {"frequency": 4186.01, "color": [144, 238, 144], "range": [4186.01, 4434.92], "symbol": "♩"},
   
}

def get_quickly_frequency_by_color(r, g, b):
    target = [r, g, b]
    for note, props in freq_symbols.items():
        if props["color"] == target:
            return props["frequency"]
    return None  # or raise an error / return a default

def color_to_frequency(r, g, b):
    h, s, v = rgb_to_hsv(r / 255, g / 255, b / 255)
    hue_deg = h * 360
    note_name = hue_to_note_name(hue_deg)
    octave = brightness_to_octave(v)
    midi_note = 12 + octave * 12 + NOTE_TO_SEMITONE[note_name]
    return 440 * 2 ** ((midi_note - 69) / 12)

def get_frequency_from_color(r, g, b, threshold=10000):  # very high
    closest_freq = None
    closest_dist = float('inf')
    for info in freq_symbols.values():
        rgb = info.get("color")
        if tuple(rgb)==(r,g,b):
            closest_freq = info["frequency"]
            return closest_freq
        
        if rgb:
            dist = color_distance((r, g, b), tuple(rgb))
            if dist < closest_dist:
                closest_dist = dist
                closest_freq = info["frequency"]
    return closest_freq

def generate_tone(frequencies, brush, duration=DURATION_PER_STEP):
    # Validate brush type first
    valid_brushes = {"spray", "star", "cross", "square", "triangle", "sawtooth", "round", "line"}
    if brush.lower() not in valid_brushes:
        raise ValueError(f"Invalid brush type: {brush}. Valid options are {valid_brushes}")

    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    
    if frequencies==0:
        return np.zeros_like(t)

    # Parameter validation
    if not isinstance(frequencies, (list, np.ndarray)) or len(frequencies) == 0:
        return np.zeros_like(t)
    # The second 'if not frequencies:' is redundant if the first one checks len(frequencies) == 0
    # but keeping it for now if there's a subtle difference intended (e.g., empty list vs. None)
    if not frequencies:
        return np.zeros_like(t)
    
    
    
    frequencies = np.clip(frequencies, 20, 20000)  # Audible range
    
    # Phase-based waveform generation (anti-aliased)
    # Assuming frequencies is a list/array of frequencies for multiple tones.
    # If it's a single frequency, frequencies.mean() will work.
    # If it's multiple frequencies for a single tone, you might need to adjust this.
    # For now, assuming `frequencies` is a list of individual frequencies to process in the loop.
    # The `phase` calculation here seems to be for a single mean frequency, which might not be
    # what's intended if `freq` in the loop is meant to be the specific frequency for that iteration.
    # Let's adjust `phase` calculation to be inside the loop or based on `freq` if needed.
    # For now, I'll keep it outside, assuming it's a base phase.
    # If `frequencies` is a list of single frequencies to be processed one by one,
    # `phase` should likely be calculated per `freq` inside the loop.
    # For this fix, I'll assume `phase` is a general time-based array.
    
    # Re-evaluating phase: if `freq` is used inside the loop, `phase` should be `2 * np.pi * freq * t`
    # Let's move this inside the loop for clarity and correctness based on `freq`.
    
    waveform = np.zeros_like(t)

    for freq in frequencies:
        # Calculate phase for the current frequency within the loop
        phase = 2 * np.pi * freq * t

        if brush.lower() == "spray":
            # FM synthesis with harmonic ratio modulation
            mod_ratio = 1.7 + 0.3 * np.sin(2 * np.pi * 0.2 * t)
            carrier = np.sin(phase + 3 * np.sin(mod_ratio * phase))
            tone = carrier * (0.6 + 0.4 * np.sin(2 * np.pi * 5 * t))
            
            # Add filtered noise layer
            noise = 0.15 * np.random.normal(0, 1, len(t))
            # Ensure SAMPLE_RATE is defined and accessible for signal.butter
            noise = signal.lfilter(*signal.butter(4, 1000/(SAMPLE_RATE/2)), noise)
            tone = tone * (0.7 + 0.3 * np.sin(2 * np.pi * 3 * t)) + noise
            # The commented out lines below were part of the original snippet,
            # but were not indented properly and are likely alternative implementations.
            # # Smooth frequency + amplitude modulation
            # mod_freq = freq + 40 * np.sin(2 * np.pi * 6 * t)
            # amp_mod = 0.8 + 0.2 * np.sin(2 * np.pi * 3 * t)
            # tone = np.sin(2 * np.pi * mod_freq * t) * amp_mod

        elif brush.lower() == "star":
            # Additive synthesis with harmonic series
            harmonics = [
                (1, 0.6),    # Fundamental
                (2, 0.4),    # Octave
                (3, 0.3),    # Perfect fifth
                (5, 0.2)     # Major third
            ]
            tone = sum(np.sin(h * phase) * amp for h, amp in harmonics)
            
            # Gentle detuning
            detune = 1 + 0.001 * np.sin(2 * np.pi * 0.1 * t)
            tone = tone * detune

            # # Musical interval: root + octave + major third (harmonic stack)
            # # tone = (
            # #     0.5 * np.sin(2 * np.pi * freq * t) +
            # #    0.3 * np.sin(2 * np.pi * freq * 2 * t) +
            # #   0.2 * np.sin(2 * np.pi * freq * 2.5 * t)  # Major third above octave
            # # )

        elif brush.lower() == "cross":
            # Phase distortion synthesis
            distorted_phase = phase + 0.8 * np.sin(phase)
            tone = np.sin(distorted_phase) * np.sin(2 * distorted_phase)

            # # Chorus-like detuning effect
            # # tone = (
            # #     0.6 * np.sin(2 * np.pi * freq * t) +
            # #     0.4 * np.sin(2 * np.pi * (freq + 6) * t)
            # # )
        elif brush.lower() == "square":
            # Pulse width modulation
            pw = 0.5 + 0.3 * np.sin(2 * np.pi * 0.5 * t)
            tone = signal.square(phase, duty=pw)

            # # Rich odd harmonics for a warm square tone
            # # tone = signal.square(2 * np.pi * freq * t)
            # # tone += 0.3 * np.sin(3 * 2 * np.pi * freq * t)
            # # tone += 0.2 * np.sin(5 * 2 * np.pi * freq * t)

        elif brush.lower() == "triangle":
            # Band-limited triangle with even harmonics
            tone = signal.sawtooth(phase, width=0.5)
            tone -= 0.25 * signal.sawtooth(2 * phase, width=0.5)

            # # Soft odd harmonics — smooth and mellow
            # # tone = signal.sawtooth(2 * np.pi * freq * t, width=0.5)
            # # tone += 0.2 * np.sin(3 * 2 * np.pi * freq * t)

        elif brush.lower() == "sawtooth":
            # Supersaw-style detuned oscillators
            detune = [0.99, 1.0, 1.01]
            # Changed frequencies.mean() to freq to use the current loop frequency
            tone = sum(0.4 * np.sin(2 * np.pi * d * freq * t) for d in detune)
            
            # # Full harmonic spectrum, shaped by envelope
            # # tone = signal.sawtooth(2 * np.pi * freq * t)

        else:  # Default "round" - sine wave
            # Subtle vibrato and harmonics
            vibrato = 0.1 * np.sin(2 * np.pi * 6 * t)  # Reduced from 0.3
            tone = 0.9 * np.sin(phase + vibrato) + 0.1 * np.sin(3 * phase)  # 90/10 balance
            # # tone = np.sin(2 * np.pi * freq * t)
        
        # Add the generated tone for the current frequency to the overall waveform
        waveform += tone

    # Envelope: soft attack and exponential decay
    envelope = np.ones_like(t)
    attack = int(0.1 * SAMPLE_RATE)
    attack_len = int(0.1 * len(t))  # 10% of duration
    attack_len = max(1, attack_len)
    
    envelope[:attack_len] = np.linspace(0, 1, attack_len)
    envelope[attack_len:] = np.exp(-5 * np.linspace(0, 1, len(t) - attack_len))

    waveform *= envelope

    # Normalize to prevent clipping
    # This normalization should apply to the final `waveform`, not `tone`
    max_val = np.max(np.abs(waveform))
    if max_val > 0:
        waveform /= max_val

    return waveform

def color_distance(c1, c2):
    return sum((a - b) ** 2 for a, b in zip(c1, c2)) ** 0.5

@app.route('/drawing2audio')
def drawing2audio():
    return render_template('drawing_to_note.html')

@app.route('/submit', methods=['POST'])
def submit():
    data = request.json
    if 'image' not in data:
        return jsonify({"error": "No image provided"}), 400

    brush = data.get('brush', 'unknown')
    image_data = data['image'].split(',')[1]
    img = Image.open(BytesIO(base64.b64decode(image_data))).convert('RGBA')
    width, height = img.size
    pixels = img.load()

    print(f"Received image size: {width}x{height}")

    timeline = {}  # x coordinate -> list of frequencies
    colors_found = set()

    for x in range(width):
        freqs = []
        for y in range(height):
            r, g, b, a = pixels[x, y]
            
            
            
            if not(r ==0 and g==0 and b==0):
                if r==g and g==b:
                    continue
                freq=get_quickly_frequency_by_color(int(r),int(g),int(b))
                
                if a > 200:  # ignore transparent pixels
                    freq = get_frequency_from_color(r, g, b)
                    if freq:
                        freqs.append(freq)
                        colors_found.add((r, g, b))
           
        if freqs:
            timeline[x] = list(np.unique(freqs))
            print(x,timeline[x])
            
        elif len(list(timeline))>0:
            timeline[x] = 0
            print(x,timeline[x])
    
    stop=1
    for x in range(width):
        if x in timeline:
            if not (timeline[x] == 0):
                stop=x
    
    for r in range(stop,width):
        del timeline[r]
    
    print(timeline)
    print(f"Colors detected (approx): {colors_found}")
    if not timeline:
        return jsonify({"error": "No valid colors detected"}), 400

    # Generate audio: sum tones for each vertical slice, then concatenate horizontally
    #audio_segments = [generate_tone(timeline[x],brush) for x in sorted(timeline.keys())]
    #audio = np.concatenate(audio_segments)
    #audio_int16 = np.int16(audio * 32767)

    audio_segments = []
    for x in sorted(timeline.keys()):
    
        segment = generate_tone(timeline[x],brush)
        #segment = segment / np.max(np.abs(segment))  # Normalize per slice
        audio_segments.append(segment)
    
    audio = np.concatenate(audio_segments)
    audio = audio / np.max(np.abs(audio))  # Final normalization
    audio_int16 = np.int16(audio * 32767)


    filename = f"sound_{int(time.time() * 1000)}.wav"
    filepath = os.path.join(OUTPUT_DIR, filename)
    write_wav(filepath, SAMPLE_RATE, audio_int16)

    return jsonify({"url": f"/static/audio/{filename}"})

@app.route('/static/audio/<path:filename>')
def serve_audio(filename):
    return send_from_directory(OUTPUT_DIR, filename)

if __name__ == '__main__':
     app.run(debug=True,host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))


