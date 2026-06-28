"""
NeuroCap – BiLSTM_2L sur datasets augmentés (A, B, C, D, FULL) + LOSO
BiLSTM 2 couches 64 unités (128 sortie bidi) + pré-encodeur CNN (1000 → ~63 pas).
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import torch.nn as nn
from DL_utils_regression import N_CLASSES, CNNPreEncoder, dl_main_regression

class BiLSTM_2L(nn.Module):
    """BiLSTM 2 couches 64 unités (128 sortie bidi) avec CNNPreEncoder."""
    def __init__(self, n_classes=N_CLASSES):
        super().__init__()
        self.pre_encoder = CNNPreEncoder(out_features=64)
        self.rnn = nn.LSTM(64, 64, num_layers=2, batch_first=True, bidirectional=True, dropout=0.3)
        self.fc = nn.Sequential(nn.Linear(128, 32), nn.ReLU(), nn.Dropout(0.5), nn.Linear(32, n_classes))
    def forward(self, x):
        x = self.pre_encoder(x)          # (B, 1, 1000) → (B, ~63, 64)
        out, _ = self.rnn(x)             # (B, ~63, hidden)
        return self.fc(out[:, -1, :])     # Dernier pas de temps

if __name__ == "__main__":
    dl_main_regression("BiLSTM_2L", BiLSTM_2L)