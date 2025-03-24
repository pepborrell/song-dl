import io
from pathlib import Path

import librosa
import librosa.display
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image


def generate_spectrogram(audio_path: Path) -> Image.Image:
    """Example usage:
    img = generate_spectrogram("your_audio_file.wav")
    img.show()  # To display
    img.save("spectrogram.png")  # To save
    """
    if not audio_path.exists():
        raise FileNotFoundError(f"File not found: {audio_path}")
    # Load the audio file
    y, sr = librosa.load(audio_path, sr=None)

    # Compute spectrogram
    D = librosa.amplitude_to_db(np.abs(librosa.stft(y)), ref=np.max, top_db=100)

    # Create a figure without displaying it
    fig, ax = plt.subplots(figsize=(10, 10), dpi=500)
    # Display spectrogram and store the result
    img = librosa.display.specshow(D, sr=sr, x_axis="time", y_axis="hz", ax=ax)

    # Make axis go up to 24kHz. this is the default for spek.
    ax.set_ylim(0, 24000)

    # Create a colorbar with a reference to the mappable object
    cbar = plt.colorbar(img, ax=ax, format="%+2.0f dB")
    cbar.set_label("dB")

    # Save to a BytesIO buffer
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", pad_inches=0)
    plt.close(fig)

    # Convert buffer to PIL image
    buf.seek(0)
    img = Image.open(buf)
    return img
