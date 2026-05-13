"""
NeuroCap – GRU_2L sur datasets augmentés (A, B, C, D, FULL) + LOSO
GRU unidirectionnel 2 couches 64 unités + pré-encodeur CNN (1000 → ~63 pas).
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import torch.nn as nn
from DL_utils import N_CLASSES, CNNPreEncoder, dl_main

class GRU_2L(nn.Module):
    """GRU unidirectionnel 2 couches 64 unités avec CNNPreEncoder."""
    def __init__(self, n_classes=N_CLASSES):
        super().__init__()
        self.pre_encoder = CNNPreEncoder(out_features=64)
        self.rnn = nn.GRU(64, 64, num_layers=2, batch_first=True, dropout=0.3)
        self.fc = nn.Sequential(nn.Linear(64, 32), nn.ReLU(), nn.Dropout(0.5), nn.Linear(32, n_classes))
    def forward(self, x):
        x = self.pre_encoder(x)          # (B, 1, 1000) → (B, ~63, 64)
        out, _ = self.rnn(x)             # (B, ~63, hidden)
        return self.fc(out[:, -1, :])     # Dernier pas de temps

if __name__ == "__main__":
    dl_main("GRU_2L", GRU_2L)