"""
NeuroCap – CNN3D sur représentations temps-fréquence EEG
Transforme le signal en multi-bandes spectrogrammes empilés (δ, θ, α, β, γ)
puis applique des convolutions 3D (bande × fréquence × temps).
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pathlib import Path;
import torch, torch.nn as nn
from DL_utils_regression import N_CLASSES, dl_main_regression

class MultiScaleSTFT(nn.Module):
    """Crée un 'volume' 3D : (batch, 1, n_scales, freq, time)."""
    def __init__(self, n_ffts=[64, 128, 256], hop=32):
        super().__init__()
        self.n_ffts = n_ffts
        self.hop = hop
    
    def forward(self, x):
        # x: (B, 1, 1000)
        x_1d = x.squeeze(1)  # (B, 1000)
        spectros = []
        for nfft in self.n_ffts:
            win = torch.hann_window(nfft, device=x.device)
            s = torch.stft(x_1d, n_fft=nfft, hop_length=self.hop, window=win, return_complex=True)
            spectros.append(torch.abs(s))
        # Pad to same freq/time dims and stack
        max_f = max(s.shape[1] for s in spectros)
        max_t = max(s.shape[2] for s in spectros)
        padded = []
        for s in spectros:
            pf = max_f - s.shape[1]
            pt = max_t - s.shape[2]
            padded.append(torch.nn.functional.pad(s, (0, pt, 0, pf)))
        return torch.stack(padded, dim=1).unsqueeze(1)  # (B, 1, n_scales, freq, time)

class CNN3D(nn.Module):
    def __init__(self, n_classes=N_CLASSES):
        super().__init__()
        self.stft = MultiScaleSTFT(n_ffts=[64, 128, 256], hop=32)
        self.conv = nn.Sequential(
            nn.Conv3d(1, 16, kernel_size=3, padding=1), nn.BatchNorm3d(16), nn.ReLU(),
            nn.MaxPool3d((1, 2, 2)),  # Ne pool PAS sur la dimension scales (3)
            nn.Conv3d(16, 32, kernel_size=3, padding=1), nn.BatchNorm3d(32), nn.ReLU(),
            nn.MaxPool3d((1, 2, 2)),
            nn.Conv3d(32, 64, kernel_size=3, padding=1), nn.BatchNorm3d(64), nn.ReLU(),
            nn.AdaptiveAvgPool3d((1, 2, 2)),
        )
        self.fc = nn.Sequential(nn.Flatten(), nn.Linear(64*1*2*2, 128), nn.ReLU(), nn.Dropout(0.5), nn.Linear(128, n_classes))
    
    def forward(self, x):
        vol = self.stft(x)  # (B, 1, 3, F, T)
        return self.fc(self.conv(vol))

if __name__ == '__main__':
    dl_main_regression("CNN3D", CNN3D)