import librosa 
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import io


file = 'audio.mp3'
y, sr = librosa.load(file) # loading the audio file

D = np.abs(librosa.stft(y)) 
# Here we are computing the STFT of the audio signal. 
# The result is a complex-valued matrix D, where each element represents the 
# magnitude and phase of a particular frequency at a particular time. 
# Using the np.abs function, we can extract the magnitude of the STFT and will discard any phase information.

D_db = librosa.amplitude_to_db(D, ref=np.max)

# Here we are converting the magnitude of the STFT to decibels.
# The ref parameter specifies the reference power to use when computing the decibels. 
# The reference value is set to the maximum value of the D matrix.

num_colors = 256
colors = [(0, 'black')]
for i in range(1, num_colors):
    frequency = i / num_colors * (sr / 2)  # Normalize frequency to the Nyquist frequency
    hue = frequency / (sr / 2)  # Map frequency to hue
    colors.append((i / (num_colors - 1), plt.cm.hsv(hue)[:3]))  # Add color tuple

# In the above few lines of code we have defined the color map and the colors that will be used in the plot.
# We are using the HSV color space to map the frequency of the audio signal to a color.
# Lower frequencies are mapped to the start of hsv

cmap = mcolors.LinearSegmentedColormap.from_list("custom_colormap", colors)

# Here we are creating a color map using the LinearSegmentedColormap class from matplotlib.colors.
# The from_list method takes in the name of the colormap and the colors that will be used in the plot,
# and returns a LinearSegmentedColormap object.

fig, ax = plt.subplots(figsize=(10, 4))
img = librosa.display.specshow(D_db, sr=sr, x_axis='time', y_axis='log', cmap=cmap, ax=ax)

# Here we are displaying the spectrogram with a custom colormap.
# The cmap parameter specifies the color map to use.

cbar = fig.colorbar(img, ax=ax, format='%+2.0f dB')
cbar.set_label('Decibels')
# Add color bar

plt.show()
# Show the plot