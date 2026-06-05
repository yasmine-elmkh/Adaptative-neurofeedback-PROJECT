"""NeuroCap – CNN2D_DANN (spectrogramme STFT) sur datasets augmentés (A, B, C, D, FULL) + LOSO"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import torch, torch.nn as nn
from DL_utils import N_CLASSES
from DANN_utils import DomainClassifier, dann_main


def _signal_to_spectrogram(x, n_fft=128, hop_length=32):
    win = torch.hann_window(n_fft, device=x.device)
    stft = torch.stft(x.squeeze(1), n_fft=n_fft, hop_length=hop_length,
                      window=win, return_complex=True)
    return torch.abs(stft).unsqueeze(1)


class CNN2D_DANN(nn.Module):
    """
    CNN2D + DANN.
    Spectrogramme STFT → Conv2D × 3 (feat_dim=2048) → label_head + domain_head.
    """
    def __init__(self, n_classes=N_CLASSES):
        super().__init__()
        self.conv1 = nn.Sequential(
            nn.Conv2d(1, 32, 3, padding=1), nn.BatchNorm2d(32), nn.ReLU(),
            nn.MaxPool2d(2), nn.Dropout2d(0.25),
        )
        self.conv2 = nn.Sequential(
            nn.Conv2d(32, 64, 3, padding=1), nn.BatchNorm2d(64), nn.ReLU(),
            nn.MaxPool2d(2), nn.Dropout2d(0.25),
        )
        self.conv3 = nn.Sequential(
            nn.Conv2d(64, 128, 3, padding=1), nn.BatchNorm2d(128), nn.ReLU(),
            nn.AdaptiveAvgPool2d((4, 4)),
        )
        self.flatten = nn.Flatten()
        feat_dim = 128 * 4 * 4  # 2048
        self.label_head = nn.Sequential(
            nn.Linear(feat_dim, 256), nn.BatchNorm1d(256), nn.ReLU(),
            nn.Dropout(0.5), nn.Linear(256, n_classes),
        )
        self.domain_head = DomainClassifier(feat_dim, hidden_dim=128)

    def forward(self, x, lambda_grl=1.0):
        x = _signal_to_spectrogram(x)
        feat = self.flatten(self.conv3(self.conv2(self.conv1(x))))
        return self.label_head(feat), self.domain_head(feat, lambda_grl)


if __name__ == '__main__':
    dann_main("CNN2D_DANN", CNN2D_DANN)
