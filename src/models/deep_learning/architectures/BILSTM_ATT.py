"""
NeuroCap – BiLSTM_Att sur datasets augmentés (A, B, C, D, FULL) + LOSO
BiLSTM 2 couches + Attention Bahdanau + pré-encodeur CNN.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import torch.nn as nn
from DL_utils import N_CLASSES, CNNPreEncoder, BahdanauAttention, dl_main

class BiLSTM_Att(nn.Module):
    """BiLSTM 2 couches + Attention Bahdanau avec CNNPreEncoder."""
    def __init__(self, n_classes=N_CLASSES):
        super().__init__()
        self.pre_encoder = CNNPreEncoder(out_features=64)
        self.rnn = nn.LSTM(64, 64, num_layers=2, batch_first=True, bidirectional=True, dropout=0.3)
        self.attention = BahdanauAttention(128)
        self.fc = nn.Sequential(nn.Linear(128, 32), nn.ReLU(), nn.Dropout(0.5), nn.Linear(32, n_classes))
    def forward(self, x):
        x = self.pre_encoder(x)          # (B, 1, 1000) → (B, ~63, 64)
        out, _ = self.rnn(x)             # (B, ~63, hidden)
        context, _ = self.attention(out)  # (B, hidden) — weighted sum
        return self.fc(context)

if __name__ == "__main__":
    dl_main("BiLSTM_Att", BiLSTM_Att)