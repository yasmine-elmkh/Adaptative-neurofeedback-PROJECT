"""NeuroCap – CNN_LSTM sur datasets augmentés (A, B, C, D, FULL) + LOSO"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import torch, torch.nn as nn
from DL_utils import N_CLASSES, dl_main

class CNN_LSTM(nn.Module):
    """CNN encoder → BiLSTM + Attention. Le CNN réduit la séquence AVANT le LSTM."""
    def __init__(self, n_classes=N_CLASSES, hidden_size=64):
        super().__init__()
        self.enc = nn.Sequential(
            nn.Conv1d(1, 32, 15, padding=7), nn.BatchNorm1d(32), nn.ReLU(), nn.MaxPool1d(4),
            nn.Conv1d(32, 64, 11, padding=5), nn.BatchNorm1d(64), nn.ReLU(), nn.MaxPool1d(4),
            nn.Conv1d(64, 128, 5, padding=2), nn.BatchNorm1d(128), nn.ReLU(), nn.MaxPool1d(4),
        )
        self.lstm = nn.LSTM(128, hidden_size, 2, batch_first=True, bidirectional=True, dropout=0.3)
        self.att = nn.Sequential(nn.Linear(hidden_size*2, 64), nn.Tanh(), nn.Linear(64, 1))
        self.fc = nn.Sequential(nn.Linear(hidden_size*2, 64), nn.ReLU(), nn.Dropout(0.5), nn.Linear(64, n_classes))
    def forward(self, x):
        x = self.enc(x).permute(0, 2, 1)  # (B, ~15, 128) au lieu de (B, 1000, 1)
        out, _ = self.lstm(x)
        att_w = torch.softmax(self.att(out), dim=1)
        context = (att_w * out).sum(dim=1)
        return self.fc(context)

if __name__ == '__main__':
    dl_main("CNN_LSTM", CNN_LSTM)