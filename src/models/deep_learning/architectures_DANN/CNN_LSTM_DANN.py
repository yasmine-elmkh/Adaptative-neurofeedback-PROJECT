"""NeuroCap – CNN_LSTM_DANN (CNN encoder → BiLSTM + Attention) sur datasets augmentés (A, B, C, D, FULL) + LOSO"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import torch, torch.nn as nn
from DL_utils import N_CLASSES
from DANN_utils import DomainClassifier, dann_main


class CNN_LSTM_Att_DANN(nn.Module):
    """
    CNN encoder → BiLSTM + Attention + DANN.
    CNN réduit la séquence, BiLSTM(2L) traite,
    Attention produit le contexte (feat_dim=128) → label_head + domain_head.
    """
    def __init__(self, n_classes=N_CLASSES, hidden_size=64):
        super().__init__()
        self.enc = nn.Sequential(
            nn.Conv1d(1, 32, 15, padding=7), nn.BatchNorm1d(32), nn.ReLU(), nn.MaxPool1d(4),
            nn.Conv1d(32, 64, 11, padding=5), nn.BatchNorm1d(64), nn.ReLU(), nn.MaxPool1d(4),
            nn.Conv1d(64, 128, 5, padding=2), nn.BatchNorm1d(128), nn.ReLU(), nn.MaxPool1d(4),
        )
        self.lstm = nn.LSTM(128, hidden_size, 2, batch_first=True,
                            bidirectional=True, dropout=0.3)
        self.att = nn.Sequential(
            nn.Linear(hidden_size * 2, 64), nn.Tanh(), nn.Linear(64, 1),
        )
        feat_dim = hidden_size * 2  # 128
        self.label_head = nn.Sequential(
            nn.Linear(feat_dim, 64), nn.ReLU(), nn.Dropout(0.5), nn.Linear(64, n_classes),
        )
        self.domain_head = DomainClassifier(feat_dim)

    def forward(self, x, lambda_grl=1.0):
        x = self.enc(x).permute(0, 2, 1)
        out, _ = self.lstm(x)
        att_w = torch.softmax(self.att(out), dim=1)
        feat = (att_w * out).sum(dim=1)
        return self.label_head(feat), self.domain_head(feat, lambda_grl)


if __name__ == '__main__':
    dann_main("CNN_LSTM_Att_DANN", CNN_LSTM_Att_DANN)
