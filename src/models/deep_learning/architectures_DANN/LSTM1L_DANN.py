"""NeuroCap – LSTM1L_DANN sur datasets augmentés (A, B, C, D, FULL) + LOSO"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import torch.nn as nn
from DL_utils import N_CLASSES, CNNPreEncoder
from DANN_utils import DomainClassifier, dann_main


class LSTM_1L_DANN(nn.Module):
    """
    LSTM unidirectionnel 1 couche + DANN.
    CNNPreEncoder → LSTM(1L) → dernier pas (feat_dim=64) → label_head + domain_head.
    """
    def __init__(self, n_classes=N_CLASSES):
        super().__init__()
        self.pre_encoder = CNNPreEncoder(out_features=64)
        self.rnn = nn.LSTM(64, 64, num_layers=1, batch_first=True)
        self.label_head = nn.Sequential(
            nn.Linear(64, 32), nn.ReLU(), nn.Dropout(0.5), nn.Linear(32, n_classes),
        )
        self.domain_head = DomainClassifier(64)

    def forward(self, x, lambda_grl=1.0):
        out, _ = self.rnn(self.pre_encoder(x))
        feat = out[:, -1, :]
        return self.label_head(feat), self.domain_head(feat, lambda_grl)


if __name__ == '__main__':
    dann_main("LSTM_1L_DANN", LSTM_1L_DANN)
