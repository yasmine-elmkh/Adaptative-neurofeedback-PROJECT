"""NeuroCap – CNN2D sur spectrogrammes EEG (A, B, C, D, FULL) + LOSO"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent)) 

from pathlib import Path;

import torch, torch.nn as nn
from DL_utils import N_CLASSES, EPOCH_SAMPLES, dl_main

def signal_to_spectrogram(x, n_fft=128, hop_length=32, window=None):
    if window is None:
        window = torch.hann_window(n_fft, device=x.device)
    x_sq = x.squeeze(1)
    stft = torch.stft(x_sq, n_fft=n_fft, hop_length=hop_length, window=window, return_complex=True)
    return torch.abs(stft).unsqueeze(1)

class CNN2D(nn.Module):
    def __init__(self, n_classes=N_CLASSES):
        super().__init__()
        self.conv1 = nn.Sequential(nn.Conv2d(1, 32, 3, padding=1), nn.BatchNorm2d(32), nn.ReLU(), nn.MaxPool2d(2), nn.Dropout2d(0.25))
        self.conv2 = nn.Sequential(nn.Conv2d(32, 64, 3, padding=1), nn.BatchNorm2d(64), nn.ReLU(), nn.MaxPool2d(2), nn.Dropout2d(0.25))
        self.conv3 = nn.Sequential(nn.Conv2d(64, 128, 3, padding=1), nn.BatchNorm2d(128), nn.ReLU(), nn.AdaptiveAvgPool2d((4, 4)))
        self.fc = nn.Sequential(nn.Flatten(), nn.Linear(128*4*4, 256), nn.BatchNorm1d(256), nn.ReLU(), nn.Dropout(0.5), nn.Linear(256, n_classes))
    def forward(self, x):
        x = signal_to_spectrogram(x)
        return self.fc(self.conv3(self.conv2(self.conv1(x))))

if __name__ == '__main__':
    dl_main("CNN2D", CNN2D)