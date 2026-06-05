"""NeuroCap – GRU_ATT_DANN (GRU 2 couches + Attention Bahdanau) sur datasets augmentés (A, B, C, D, FULL) + LOSO"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import torch.nn as nn
from DL_utils import N_CLASSES, CNNPreEncoder, BahdanauAttention
from DANN_utils import DomainClassifier, dann_main


class GRU_Att_DANN(nn.Module):
    """
    GRU 2 couches + Attention Bahdanau + DANN.
    CNNPreEncoder → GRU(2L) → Attention (feat_dim=64) → label_head + domain_head.
    """
    def __init__(self, n_classes=N_CLASSES):
        super().__init__()
        self.pre_encoder = CNNPreEncoder(out_features=64)
        self.rnn = nn.GRU(64, 64, num_layers=2, batch_first=True, dropout=0.3)
        self.attention = BahdanauAttention(64)
        self.label_head = nn.Sequential(
            nn.Linear(64, 32), nn.ReLU(), nn.Dropout(0.5), nn.Linear(32, n_classes),
        )
        self.domain_head = DomainClassifier(64)

    def forward(self, x, lambda_grl=1.0):
        out, _ = self.rnn(self.pre_encoder(x))
        feat, _ = self.attention(out)
        return self.label_head(feat), self.domain_head(feat, lambda_grl)


if __name__ == '__main__':
    dann_main("GRU_Att_DANN", GRU_Att_DANN)
