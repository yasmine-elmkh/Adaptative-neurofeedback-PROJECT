"""NeuroCap – CNN1D sur datasets augmentés (A, B, C, D, FULL) + LOSO"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pathlib import Path; 
import torch.nn as nn
from DL_utils import N_CLASSES, dl_main

class CNN1D(nn.Module):
    def __init__(self, n_classes=N_CLASSES):
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv1d(1, 32, 25, padding=12), nn.BatchNorm1d(32), nn.ReLU(), nn.MaxPool1d(4), nn.Dropout(0.25),
            nn.Conv1d(32, 64, 15, padding=7), nn.BatchNorm1d(64), nn.ReLU(), nn.MaxPool1d(4), nn.Dropout(0.25),
            nn.Conv1d(64, 128, 5, padding=2), nn.BatchNorm1d(128), nn.ReLU(), nn.AdaptiveAvgPool1d(8),
        )
        self.fc = nn.Sequential(nn.Flatten(), nn.Linear(1024, 128), nn.BatchNorm1d(128), nn.ReLU(), nn.Dropout(0.5), nn.Linear(128, n_classes))
    def forward(self, x):
        return self.fc(self.features(x))

if __name__ == '__main__':
    dl_main("CNN1D", CNN1D)