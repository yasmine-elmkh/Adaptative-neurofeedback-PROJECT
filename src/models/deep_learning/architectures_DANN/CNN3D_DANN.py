"""NeuroCap – CNN3D_DANN (multi-scale STFT) sur datasets augmentés (A, B, C, D, FULL) + LOSO"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import torch, torch.nn as nn
from DL_utils import N_CLASSES
from DANN_utils import DomainClassifier, dann_main


class MultiScaleSTFT(nn.Module):
    """Crée un volume 3D : (batch, 1, n_scales, freq, time)."""
    def __init__(self, n_ffts=(64, 128, 256), hop=32):
        super().__init__()
        self.n_ffts = n_ffts
        self.hop = hop

    def forward(self, x):
        x_1d = x.squeeze(1)
        spectros = []
        for nfft in self.n_ffts:
            win = torch.hann_window(nfft, device=x.device)
            s = torch.stft(x_1d, n_fft=nfft, hop_length=self.hop,
                           window=win, return_complex=True)
            spectros.append(torch.abs(s))
        max_f = max(s.shape[1] for s in spectros)
        max_t = max(s.shape[2] for s in spectros)
        padded = [
            nn.functional.pad(s, (0, max_t - s.shape[2], 0, max_f - s.shape[1]))
            for s in spectros
        ]
        return torch.stack(padded, dim=1).unsqueeze(1)  # (B, 1, 3, F, T)


class CNN3D_DANN(nn.Module):
    """
    CNN3D + DANN.
    Volume STFT multi-échelle → Conv3D × 3 (feat_dim=256) → label_head + domain_head.
    """
    def __init__(self, n_classes=N_CLASSES):
        super().__init__()
        self.stft = MultiScaleSTFT()
        self.conv = nn.Sequential(
            nn.Conv3d(1, 16, 3, padding=1), nn.BatchNorm3d(16), nn.ReLU(),
            nn.MaxPool3d((1, 2, 2)),
            nn.Conv3d(16, 32, 3, padding=1), nn.BatchNorm3d(32), nn.ReLU(),
            nn.MaxPool3d((1, 2, 2)),
            nn.Conv3d(32, 64, 3, padding=1), nn.BatchNorm3d(64), nn.ReLU(),
            nn.AdaptiveAvgPool3d((1, 2, 2)),
        )
        self.flatten = nn.Flatten()
        feat_dim = 64 * 1 * 2 * 2  # 256
        self.label_head = nn.Sequential(
            nn.Linear(feat_dim, 128), nn.ReLU(),
            nn.Dropout(0.5), nn.Linear(128, n_classes),
        )
        self.domain_head = DomainClassifier(feat_dim)

    def forward(self, x, lambda_grl=1.0):
        feat = self.flatten(self.conv(self.stft(x)))
        return self.label_head(feat), self.domain_head(feat, lambda_grl)


if __name__ == '__main__':
    dann_main("CNN3D_DANN", CNN3D_DANN)
