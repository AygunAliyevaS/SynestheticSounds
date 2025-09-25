import librosa
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import random
import matplotlib.pyplot as plt
import imageio
#import imageio.v2 as iio
import os

import numpy as np
import librosa

def get_note_durations(notes, sr, hop_length, beats_per_measure=4, measure_duration=2.0):
    seconds_per_beat = measure_duration / beats_per_measure
    frame_duration = hop_length / sr

    # Group repeated notes
    grouped = []
    current_note = notes[0]
    count = 1
    for n in notes[1:]:
        if n == current_note:
            count += 1
        else:
            grouped.append((current_note, count))
            current_note = n
            count = 1
    grouped.append((current_note, count))

    durations_in_beats = [frames * frame_duration / seconds_per_beat for _, frames in grouped]

    def map_duration(beat):
        if beat >= 4:
            return "whole"
        elif beat >= 2:
            return "half"
        elif beat >= 1:
            return "quarter"
        elif beat >= 0.5:
            return "eighth"
        elif beat>=0.25:
            return "sixteenth"
        elif beat>0.125:
            return "thirty-second"
        else:
            return "sixty-forth"
    return [(note, map_duration(beat)) for (note, _), beat in zip(grouped, durations_in_beats)]

duration_symbol={'whole':1,'half':2,'quarter':3,'eighth':4,'sixteenth':5,'thirty-second':6,'sixty-forth':7}
'''
duration_symbol = {
    'whole': '𝅝',
    'half': '𝅗𝅥',
    'quarter': '♩',
    'eighth': '♪',
    'sixteenth': '𝅘𝅥𝅮',
    'thirty-second':'𝅘𝅥𝅯',
    'sixty-forth':'𝅘𝅥𝅰'
}
'''
note_durations_values = {
    "whole": 4,
    "half": 2,
    "quarter": 1,
    "eighth": 0.5,
    "sixteenth": 0.25,
    "thirty-second": 0.125,
    'sixty-forth':0.0625
}

def get_notes_from_audio(y, sr):
    # Step 1: Get pitch and magnitude from piptrack
    pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
    
    selected_pitches = []
    selected_magnitudes = []

    # Step 2: Collect dominant pitch and magnitude per frame
    for t in range(pitches.shape[1]):
        mag = magnitudes[:, t]
        pitch = pitches[:, t]

        index = mag.argmax()
        freq = pitch[index]
        strength = mag[index]

        if freq > 0 and strength > 0:
            selected_pitches.append(freq)
            selected_magnitudes.append(strength)

    if not selected_magnitudes:
        return []  # handle silent input

    # Step 3: Compute average magnitude
    avg_mag = np.mean(selected_magnitudes)

    # Step 4: Filter pitches with magnitude above average
    filtered_notes = []
    for freq, mag in zip(selected_pitches, selected_magnitudes):
        if mag >= avg_mag:
            note = librosa.hz_to_note(freq)
            filtered_notes.append(note)

    return filtered_notes


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
    "E7": {"frequency": 2637.02, "color": (197, 153, 255), "range": (2637.02, 2793.83)},   "F7": {"frequency": 2793.83, "color": (222, 176, 255), "range": (2793.83, 2959.96)},
    "F#7/Gb7": {"frequency": 2959.96, "color": (246, 198, 255), "range": (2959.96, 3135.96)},
    "G7": {"frequency": 3135.96, "color": (251, 176, 204), "range": (3135.96, 3322.44)},
    "G#7/Ab7": {"frequency": 3322.44, "color": (255, 153, 153), "range": (3322.44, 3520.00)},
    "A7": {"frequency": 3520.00, "color": (255, 194, 176), "range": (3520.00, 3729.31)},
    "A#7/Bb7": {"frequency": 3729.31, "color": (255, 234, 198), "range": (3729.31, 3951.07)},
    "B7": {"frequency": 3951.07, "color": (255, 255, 204), "range": (3951.07, 4186.01)},
    "C8": {"frequency": 4186.01, "color": (144, 238, 144), "range": (4186.01, 4434.92)}
}


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
    
        "C3": {"frequency": 130.81, "color": [120, 190, 0], "range": [130.81, 138.59], "symbol": "♩"},
    "C#3/Db3": {"frequency": 138.59, "color": [0, 155, 0], "range": [138.59, 146.83], "symbol": "♯"},
    "D3": {"frequency": 146.83, "color": [0, 80, 100], "range": [146.83, 155.56], "symbol": "♩"},
    "D#3/Eb3": {"frequency": 155.56, "color": [0, 0, 200], "range": [155.56, 164.81], "symbol": "♯"},
    "E3": {"frequency": 164.81, "color": [110, 0, 180], "range": [164.81, 174.61], "symbol": "♩"},
    "F3": {"frequency": 174.61, "color": [140, 0, 110], "range": [174.61, 185.00], "symbol": "♩"},
    "F#3/Gb3": {"frequency": 185.00, "color": [170, 0, 240], "range": [185.00, 196.00], "symbol": "♯"},
    "G3": {"frequency": 196.00, "color": [190, 0, 130], "range": [196.00, 207.65], "symbol": "♩"},
    "G#3/Ab3": {"frequency": 207.65, "color": [210, 0, 0], "range": [207.65, 220.00], "symbol": "♯"},
     "G#3": {"frequency": 207.65, "color": [210, 0, 0], "range": [207.65, 220.00], "symbol": "♯"},
    "A3": {"frequency": 220.00, "color": [240, 85, 145], "range": [220.00, 233.08], "symbol": "♩"},
    "A#3/Bb3": {"frequency": 233.08, "color": [255, 145, 0], "range": [233.08, 246.94], "symbol": "♯"},
     "A#3": {"frequency": 233.08, "color": [255, 145, 0], "range": [233.08, 246.94], "symbol": "♯"},
    "B3": {"frequency": 246.94, "color": [250, 250, 0], "range": [246.94, 261.63], "symbol": "♩"},

    "C4": {"frequency": 261.63, "color": [130, 205, 0], "range": [261.63, 277.18], "symbol": "♩"},
    "C#4/Db4": {"frequency": 277.18, "color": [0, 180, 0], "range": [277.18, 293.66], "symbol": "♯"},
    "C#4": {"frequency": 277.18, "color": [0, 180, 0], "range": [277.18, 293.66], "symbol": "♯"},
    "D4": {"frequency": 293.66, "color": [0, 100, 120], "range": [293.66, 311.13], "symbol": "♩"},
    "D#4/Eb4": {"frequency": 311.13, "color": [0, 0, 230], "range": [311.13, 329.63], "symbol": "♯"},
    "D#4": {"frequency": 311.13, "color": [0, 0, 230], "range": [311.13, 329.63], "symbol": "♯"},
    "E4": {"frequency": 329.63, "color": [120, 0, 200], "range": [329.63, 349.23], "symbol": "♩"},
    "F4": {"frequency": 349.23, "color": [160, 0, 120], "range": [349.23, 369.99], "symbol": "♩"},
    "F#4/Gb4": {"frequency": 369.99, "color": [180, 0, 255], "range": [369.99, 392.00], "symbol": "♯"},
    "F#4": {"frequency": 369.99, "color": [180, 0, 255], "range": [369.99, 392.00], "symbol": "♯"},
    "G4": {"frequency": 392.00, "color": [200, 0, 140], "range": [392.00, 415.30], "symbol": "♩"},
    "G#4/Ab4": {"frequency": 415.30, "color": [230, 0, 0], "range": [415.30, 440.00], "symbol": "♯"},
    "A4": {"frequency": 440.00, "color": [255, 102, 160], "range": [440.00, 466.16], "symbol": "♩"},
    "A#4/Bb4": {"frequency": 466.16, "color": [255, 170, 0], "range": [466.16, 493.88], "symbol": "♯"},
    "A#4": {"frequency": 466.16, "color": [255, 170, 0], "range": [466.16, 493.88], "symbol": "♯"},
    "B4": {"frequency": 493.88, "color": [255, 255, 0], "range": [493.88, 523.25], "symbol": "♩"},
    
        "C3": {"frequency": 130.81, "color": [124, 189, 0], "range": [130.81, 138.59], "symbol": "𝅘𝅥"},
    "C#3/Db3": {"frequency": 138.59, "color": [0, 140, 0], "range": [138.59, 146.83], "symbol": "♯"},
    "D3": {"frequency": 146.83, "color": [0, 70, 92], "range": [146.83, 155.56], "symbol": "♪"},
    "D#3/Eb3": {"frequency": 155.56, "color": [0, 0, 187], "range": [155.56, 164.81], "symbol": "♭"},
     "D#3": {"frequency": 155.56, "color": [0, 0, 187], "range": [155.56, 164.81], "symbol": "♭"},
    "E3": {"frequency": 164.81, "color": [109, 0, 177], "range": [164.81, 174.61], "symbol": "𝅘𝅥𝅮"},
    "F3": {"frequency": 174.61, "color": [125, 0, 108], "range": [174.61, 185.00], "symbol": "♩"},
    "F#3/Gb3": {"frequency": 185.00, "color": [167, 0, 237], "range": [185.00, 196.00], "symbol": "♯"},
    "F#3": {"frequency": 185.00, "color": [167, 0, 237], "range": [185.00, 196.00], "symbol": "♯"},
    "G3": {"frequency": 196.00, "color": [182, 0, 122], "range": [196.00, 207.65], "symbol": "♫"},
    "G#3/Ab3": {"frequency": 207.65, "color": [200, 0, 0], "range": [207.65, 220.00], "symbol": "♭"},
    "A3": {"frequency": 220.00, "color": [235, 76, 132], "range": [220.00, 233.08], "symbol": "𝅗𝅥"},
    "A#3/Bb3": {"frequency": 233.08, "color": [255, 140, 0], "range": [233.08, 246.94], "symbol": "♯"},
    "B3": {"frequency": 246.94, "color": [255, 255, 0], "range": [246.94, 261.63], "symbol": "𝅘𝅥"},
    "C4": {"frequency": 261.63, "color": [130, 200, 0], "range": [261.63, 277.18], "symbol": "♩"},  # Middle C
    "C#4/Db4": {"frequency": 277.18, "color": [0, 160, 0], "range": [277.18, 293.66], "symbol": "♯"},
    "D4": {"frequency": 293.66, "color": [0, 80, 104], "range": [293.66, 311.13], "symbol": "♪"},
    "D#4/Eb4": {"frequency": 311.13, "color": [0, 0, 204], "range": [311.13, 329.63], "symbol": "♭"},
    "E4": {"frequency": 329.63, "color": [122, 0, 195], "range": [329.63, 349.23], "symbol": "𝅘𝅥𝅮"},
    "F4": {"frequency": 349.23, "color": [135, 0, 119], "range": [349.23, 369.99], "symbol": "♩"},
    "F#4/Gb4": {"frequency": 369.99, "color": [175, 0, 245], "range": [369.99, 392.00], "symbol": "♯"},
    "G4": {"frequency": 392.00, "color": [189, 0, 132], "range": [392.00, 415.30], "symbol": "♫"},
    "G#4/Ab4": {"frequency": 415.30, "color": [210, 0, 0], "range": [415.30, 440.00], "symbol": "♭"},
    "G#4": {"frequency": 415.30, "color": [210, 0, 0], "range": [415.30, 440.00], "symbol": "♭"},
    "A4": {"frequency": 440.00, "color": [248, 94, 139], "range": [440.00, 466.16], "symbol": "𝅗𝅥"},
    "A#4/Bb4": {"frequency": 466.16, "color": [255, 160, 0], "range": [466.16, 493.88], "symbol": "♯"},
     "A#4": {"frequency": 466.16, "color": [255, 160, 0], "range": [466.16, 493.88], "symbol": "♯"},
    "B4": {"frequency": 493.88, "color": [255, 255, 51], "range": [493.88, 523.25], "symbol": "𝅘𝅥"},
    
        "C5": {"frequency": 523.25, "color": [140, 210, 0], "range": [523.25, 554.37], "symbol": "♩"},
    "C#5/Db5": {"frequency": 554.37, "color": [0, 170, 0], "range": [554.37, 587.33], "symbol": "♯"},
    "C#5": {"frequency": 554.37, "color": [0, 170, 0], "range": [554.37, 587.33], "symbol": "♯"},
    "D5": {"frequency": 587.33, "color": [0, 90, 115], "range": [587.33, 622.25], "symbol": "♪"},
    "D#5/Eb5": {"frequency": 622.25, "color": [0, 0, 221], "range": [622.25, 659.26], "symbol": "♭"},
    "D#5": {"frequency": 622.25, "color": [0, 0, 221], "range": [622.25, 659.26], "symbol": "♭"},
    
    "E5": {"frequency": 659.26, "color": [135, 0, 213], "range": [659.26, 698.46], "symbol": "𝅘𝅥𝅮"},
    "F5": {"frequency": 698.46, "color": [148, 0, 132], "range": [698.46, 739.99], "symbol": "♩"},
    "F#5/Gb5": {"frequency": 739.99, "color": [183, 0, 255], "range": [739.99, 783.99], "symbol": "♯"},
    "F#5": {"frequency": 739.99, "color": [183, 0, 255], "range": [739.99, 783.99], "symbol": "♯"},
    "G5": {"frequency": 783.99, "color": [196, 0, 141], "range": [783.99, 830.61], "symbol": "♫"},
    "G#5/Ab5": {"frequency": 830.61, "color": [220, 0, 0], "range": [830.61, 880.00], "symbol": "♭"},
    "G#5": {"frequency": 830.61, "color": [220, 0, 0], "range": [830.61, 880.00], "symbol": "♭"},
    "A5": {"frequency": 880.00, "color": [255, 110, 145], "range": [880.00, 932.33], "symbol": "𝅗𝅥"},
    "A#5/Bb5": {"frequency": 932.33, "color": [255, 180, 0], "range": [932.33, 987.77], "symbol": "♯"},
    "A#5": {"frequency": 932.33, "color": [255, 180, 0], "range": [932.33, 987.77], "symbol": "♯"},
    "B5": {"frequency": 987.77, "color": [255, 255, 102], "range": [987.77, 1046.50], "symbol": "𝅘𝅥"},
    
        "C6": {"frequency": 1046.50, "color": [160, 240, 0], "range": [1046.50, 1108.73], "symbol": "♩"},
    "C#6/Db6": {"frequency": 1108.73, "color": [0, 190, 0], "range": [1108.73, 1174.66], "symbol": "♯"},
    "C#6": {"frequency": 1108.73, "color": [0, 190, 0], "range": [1108.73, 1174.66], "symbol": "♯"},
    "D6": {"frequency": 1174.66, "color": [0, 105, 130], "range": [1174.66, 1244.51], "symbol": "♪"},
    "D#6/Eb6": {"frequency": 1244.51, "color": [0, 0, 238], "range": [1244.51, 1318.51], "symbol": "♭"},
     "D#6": {"frequency": 1244.51, "color": [0, 0, 238], "range": [1244.51, 1318.51], "symbol": "♭"},
    "E6": {"frequency": 1318.51, "color": [158, 0, 240], "range": [1318.51, 1396.91], "symbol": "𝅘𝅥𝅮"},
    "F6": {"frequency": 1396.91, "color": [171, 0, 149], "range": [1396.91, 1479.98], "symbol": "♩"},
    "F#6/Gb6": {"frequency": 1479.98, "color": [200, 0, 255], "range": [1479.98, 1567.98], "symbol": "♯"},
    "F#6": {"frequency": 1479.98, "color": [200, 0, 255], "range": [1479.98, 1567.98], "symbol": "♯"},
    "G6": {"frequency": 1567.98, "color": [210, 0, 153], "range": [1567.98, 1661.22], "symbol": "♫"},
    "G#6/Ab6": {"frequency": 1661.22, "color": [235, 0, 0], "range": [1661.22, 1760.00], "symbol": "♭"},
    "G#6": {"frequency": 1661.22, "color": [235, 0, 0], "range": [1661.22, 1760.00], "symbol": "♭"},
    "A6": {"frequency": 1760.00, "color": [255, 140, 170], "range": [1760.00, 1864.66], "symbol": "𝅗𝅥"},
    "A#6/Bb6": {"frequency": 1864.66, "color": [255, 200, 0], "range": [1864.66, 1975.53], "symbol": "♯"},
    "A#6": {"frequency": 1864.66, "color": [255, 200, 0], "range": [1864.66, 1975.53], "symbol": "♯"},
    "B6": {"frequency": 1975.53, "color": [255, 255, 153], "range": [1975.53, 2093.00], "symbol": "𝅘𝅥"},

    "C7": {"frequency": 2093.00, "color": [195, 255, 0], "range": [2093.00, 2217.46], "symbol": "♩"},
    "C#7/Db7": {"frequency": 2217.46, "color": [0, 210, 0], "range": [2217.46, 2349.32], "symbol": "♯"},
    "C#7": {"frequency": 2217.46, "color": [0, 210, 0], "range": [2217.46, 2349.32], "symbol": "♯"},
    "D7": {"frequency": 2349.32, "color": [0, 120, 140], "range": [2349.32, 2489.02], "symbol": "♪"},
    "D#7/Eb7": {"frequency": 2489.02, "color": [0, 0, 255], "range": [2489.02, 2637.02], "symbol": "♭"},
    "D#7": {"frequency": 2489.02, "color": [0, 0, 255], "range": [2489.02, 2637.02], "symbol": "♭"},
    "E7": {"frequency": 2637.02, "color": [170, 0, 255], "range": [2637.02, 2793.83], "symbol": "𝅘𝅥𝅮"},
    "F7": {"frequency": 2793.83, "color": [180, 0, 159], "range": [2793.83, 2959.96], "symbol": "♩"},
    "F#7/Gb7": {"frequency": 2959.96, "color": [210, 0, 255], "range": [2959.96, 3135.96], "symbol": "♯"},
    "F#7": {"frequency": 2959.96, "color": [210, 0, 255], "range": [2959.96, 3135.96], "symbol": "♯"},
    "G7": {"frequency": 3135.96, "color": [220, 0, 170], "range": [3135.96, 3322.44], "symbol": "♫"},
    "G#7/Ab7": {"frequency": 3322.44, "color": [245, 0, 0], "range": [3322.44, 3520.00], "symbol": "♭"},
    "G#7": {"frequency": 3322.44, "color": [245, 0, 0], "range": [3322.44, 3520.00], "symbol": "♭"},
    "A7": {"frequency": 3520.00, "color": [255, 160, 180], "range": [3520.00, 3729.32], "symbol": "𝅗𝅥"},
    "A#7/Bb7": {"frequency": 3729.32, "color": [255, 225, 0], "range": [3729.32, 3951.07], "symbol": "♯"},
    "A#7": {"frequency": 3729.32, "color": [255, 225, 0], "range": [3729.32, 3951.07], "symbol": "♯"},
    "B7": {"frequency": 3951.07, "color": [255, 255, 178], "range": [3951.07, 4186.01], "symbol": "𝅘𝅥"},
    
        "C8": {"frequency": 4186.01, "color": [200, 255, 0], "range": [4186.01, 4434.92], "symbol": "♩"},
    "C#8/Db8": {"frequency": 4434.92, "color": [0, 255, 0], "range": [4434.92, 4698.64], "symbol": "♯"},
    "C#8": {"frequency": 4434.92, "color": [0, 255, 0], "range": [4434.92, 4698.64], "symbol": "♯"},
    "D8": {"frequency": 4698.64, "color": [0, 160, 180], "range": [4698.64, 4978.03], "symbol": "♪"},
    "D#8/Eb8": {"frequency": 4978.03, "color": [0, 0, 255], "range": [4978.03, 5274.04], "symbol": "♭"},
    "D#8": {"frequency": 4978.03, "color": [0, 0, 255], "range": [4978.03, 5274.04], "symbol": "♭"},
    "E8": {"frequency": 5274.04, "color": [160, 0, 255], "range": [5274.04, 5587.66], "symbol": "𝅘𝅥𝅮"},
    "F8": {"frequency": 5587.66, "color": [180, 0, 159], "range": [5587.66, 5919.91], "symbol": "♩"},
    "F#8/Gb8": {"frequency": 5919.91, "color": [210, 0, 255], "range": [5919.91, 6271.93], "symbol": "♯"},
    "G8": {"frequency": 6271.93, "color": [220, 0, 170], "range": [6271.93, 6644.88], "symbol": "♫"},
    "G#8/Ab8": {"frequency": 6644.88, "color": [245, 0, 0], "range": [6644.88, 7040.00], "symbol": "♭"},
    "G#8": {"frequency": 6644.88, "color": [245, 0, 0], "range": [6644.88, 7040.00], "symbol": "♭"},
    "A8": {"frequency": 7040.00, "color": [255, 160, 180], "range": [7040.00, 7458.64], "symbol": "𝅗𝅥"},
    "A#8/Bb8": {"frequency": 7458.64, "color": [255, 225, 0], "range": [7458.64, 7902.13], "symbol": "♯"},
    "A#8": {"frequency": 7458.64, "color": [255, 225, 0], "range": [7458.64, 7902.13], "symbol": "♯"},
    "B8": {"frequency": 7902.13, "color": [255, 255, 178], "range": [7902.13, 8372.02], "symbol": "𝅘𝅥"},


}

note_number_dict = {
    "C": 0,
    "C#": 1, "Db": 1,
    "D": 2,
    "D#": 3, "Eb": 3,
    "E": 4,
    "F": 5,
    "F#": 6, "Gb": 6,
    "G": 7,
    "G#": 8, "Ab": 8,
    "A": 9,
    "A#": 10, "Bb": 10,
    "B": 11
}


# Function to combine images into a GIF
def create_gif(image_folder, output_filename, duration):
    # Get list of all image files in the specified folder
    images = []
    for filename in sorted(os.listdir(image_folder)):
        if filename.endswith(('.png', '.jpg', '.jpeg')):
            images.append(imageio.imread(os.path.join(image_folder, filename)))

    # Create the GIF and save it to the specified output file
    iio.mimsave(output_filename, images, duration=duration,loop=0)
    print(f"GIF saved as {output_filename}")



from concurrent.futures import ThreadPoolExecutor

def create_gif(image_folder, output_filename, duration=1.0):
    """
    Create a GIF from images in the specified folder.
    
    Args:
        image_folder (str): Path to the folder containing images.
        output_filename (str): Path to save the output GIF.
        duration (float): Duration per frame in seconds.
    """
    # Collect image file paths
    filenames = sorted([
        os.path.join(image_folder, fname)
        for fname in os.listdir(image_folder)
        if fname.lower().endswith(('.png', '.jpg', '.jpeg'))
    ])

    # Read images in parallel
    with ThreadPoolExecutor() as executor:
        images = list(executor.map(imageio.imread, filenames))

    # Save images as GIF
    imageio.mimsave(output_filename, images, duration=duration, loop=0)
    print(f"GIF saved as {output_filename}")

import re

# Map note names to semitone offsets
NOTE_OFFSETS = {
    'C': 0, 'C#': 1, 'Db': 1,
    'D': 2, 'D#': 3, 'Eb': 3,
    'E': 4,
    'F': 5, 'F#': 6, 'Gb': 6,
    'G': 7, 'G#': 8, 'Ab': 8,
    'A': 9, 'A#': 10, 'Bb': 10,
    'B': 11
}

def note_to_midi(note: str) -> int:
    """Convert a note like 'A4' or 'C#5' to a MIDI note number."""
    match = re.match(r'^([A-Ga-g]{1}[#b]?)(-?\d+)$', note)
    if not match:
        raise ValueError(f"Invalid note format: {note}")
    name = match.group(1).capitalize()
    octave = int(match.group(2))
    if name not in NOTE_OFFSETS:
        raise ValueError(f"Invalid note name: {name}")
    return 12 * (octave + 1) + NOTE_OFFSETS[name]

def get_string_number_mod12(note: str, reference_note: str = 'A4', reference_string: int = 0) -> int:
    """Map a note to a 12-string system (returns 0-11)."""
    midi_note = note_to_midi(note)
    ref_midi = note_to_midi(reference_note)
    diff = midi_note - ref_midi
    return (reference_string + diff) % 12


def process_audio_to_gif(audio_path,gif_path):
    audio_data_org, sr = librosa.load(audio_path)    

    
    print('sr',sr)    
    counter=0

    # Canvas setup
    width=1000
    height=220
        
    t=len(audio_data_org)//sr
    
    files = os.listdir('music')
    
    
    for f in files:
        os.remove('music/'+f)
    
    ttt=6
    nn=int(sr*ttt);

    
    d=len(list(range(0,sr*t-nn,nn)))
    canvas_size = (width, height*d)
    artwork = Image.new("RGB", canvas_size, "white")
    draw = ImageDraw.Draw(artwork)
    
    tempo, beat_frames = librosa.beat.beat_track(y=audio_data_org[:sr*10], sr=sr)
    beat_times = librosa.frames_to_time(beat_frames)

    # Estimate average interval between beats
    intervals = [t2 - t1 for t1, t2 in zip(beat_times[:-1], beat_times[1:])]
    avg_interval = sum(intervals) / len(intervals)

    # Assume measure duration ~ 2 seconds and calculate beats per measure
    estimated_beats_per_measure = round(2 / avg_interval)
            
    all_info=[]
    
    for tt in range(0,sr*t-nn,nn):  
        audio_data=audio_data_org[tt:tt+nn]
        notes=get_notes_from_audio(audio_data,sr)

        note_durations = get_note_durations(notes, sr=sr, hop_length=512,beats_per_measure=estimated_beats_per_measure)
        
        for i,note in enumerate(note_durations):
                 
            n=note[0].replace("♯","#")
            
            if n not in freq_symbols:
                continue
            string_number = get_string_number_mod12(n[:3])
            
                
            symbol=freq_symbols[n]["symbol"]
            symbol=symbol.replace("#","♯")
            color=tuple(freq_symbols[n]["color"])
            
            ds=duration_symbol[note[1]]          
            ds2=note_durations_values[note[1]]
            all_info.append((symbol, ds,ds2,string_number,color))

    
    counter=0     
    x_position=45    
    font3 = ImageFont.truetype("static/DejaVuSans.ttf", size=18)
    time=0
    
    wd=500
    for t in range(len(all_info)):  
    
        lower_freq_lines = [120, 130, 140, 150, 160,170]  
        lower_freq_lines = [counter*height+ii for ii in lower_freq_lines]   
        higher_freq_lines = [30, 40, 50, 60, 70,80]  
        higher_freq_lines = [counter*height+ii for ii in higher_freq_lines]   
        
        
        Num_lines=6
        for i in range(Num_lines):           
            y=lower_freq_lines[i]
            draw.line([0, y, width, y], fill="black", width=2)
            
        for i in range(Num_lines):           
            y=higher_freq_lines[i]
            draw.line([0, y,width, y], fill="black", width=2)
        
        #draw.line([width/3, lower_freq_lines[0],width/3, lower_freq_lines[-1]], fill="black", width=2)        
        #draw.line([width/3, higher_freq_lines[0],width/3, higher_freq_lines[-1]], fill="black", width=2)
        
        #draw.line([2*width/3, lower_freq_lines[0],2*width/3, lower_freq_lines[-1]], fill="black", width=2)        
        #draw.line([2*width/3, higher_freq_lines[0],2*width/3, higher_freq_lines[-1]], fill="black", width=2)
     
        C=(np.random.randint(255),np.random.randint(255),np.random.randint(255))

        font2 = ImageFont.truetype("static/DejaVuSans.ttf", size=30)
        y_position=lower_freq_lines[0]-80
        
        
        draw.text((35,y_position-13),"2", fill=(0,0,0), font=font2)
        draw.text((35,y_position+10),str(estimated_beats_per_measure), fill=(0,0,0), font=font2)        
        
        font = ImageFont.truetype("static/Bravura.otf", size=50)
        draw.text((1,y_position),"𝄢", fill=C, font=font)  
        
        y_position=higher_freq_lines[0]-60
        draw.text((1,y_position),"𝄞", fill=C, font=font)
        draw.text((35,y_position-75),"2", fill=(0,0,0), font=font2)
        draw.text((35,y_position-50),str(estimated_beats_per_measure), fill=(0,0,0), font=font2)


        
        symbol = all_info[t][0]
        note_duration_symbol = all_info[t][1]
        note_duration = all_info[t][2]
        string_number=all_info[t][3]
        color=all_info[t][4]
        spacing=0.05
        time+=spacing
        
        x_position = x_position + wd*spacing
            
        if string_number<6:
            y_position = lower_freq_lines[0]-60-2*string_number
            draw.text((x_position,y_position),symbol, fill=color, font=font)                      
            draw.text((x_position,lower_freq_lines[0]+50),str(note_duration_symbol), fill=(0,0,0), font=font3)
        else:
            y_position = higher_freq_lines[0]-60-(2*(string_number-6))
            draw.text((x_position,y_position),symbol, fill=color, font=font)             
            draw.text((x_position,higher_freq_lines[0]+50),str(note_duration_symbol), fill=(0,0,0), font=font3)
        
        
        x_position+=int(note_duration*wd)
        time+=note_duration
        
        #print(symbol,x_position,note_duration)
        
        time_range=[round(iii,2) for iii in np.arange(time-spacing-note_duration,time,0.005)]
        
        #print(time_range)
        for k in range(len(time_range)):
            
            if round(time_range[k],2)%2==0 and time_range[k]!=0:
                
                r=(time_range[k]-min(time_range))/(max(time_range)-min(time_range))
                
                print(r,r*width)
                
                draw.line([r*width, lower_freq_lines[0],r*width, lower_freq_lines[-1]], fill="black", width=2)
                draw.line([r*width, higher_freq_lines[0],r*width, higher_freq_lines[-1]], fill="black", width=2)
                    
        if x_position>width:
        
            x_position=45
            counter+=1
            draw.line([width-5, higher_freq_lines[0],width-5, higher_freq_lines[-1]], fill="black", width=2)
            draw.line([width-10, higher_freq_lines[0],width-10, higher_freq_lines[-1]], fill="black", width=2)
            
            draw.line([width-5, lower_freq_lines[0],width-5, lower_freq_lines[-1]], fill="black", width=2)
            draw.line([width-10, lower_freq_lines[0],width-10, lower_freq_lines[-1]], fill="black", width=2)
            
                
    # Step 4: Save the artwork
    artwork.save('static/output/music.png', "PNG")

    # Example usage
    image_folder = 'music'  # Replace with your folder path
    output_filename = gif_path       # Desired output file name
 
