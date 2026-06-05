"""NeuroCap – BIGRU_ATT_DANN (BiGRU 2 couches + Attention Bahdanau) sur datasets augmentés (A, B, C, D, FULL) + LOSO"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import torch.nn as nn
from DL_utils import N_CLASSES, CNNPreEncoder, BahdanauAttention
from DANN_utils import DomainClassifier, dann_main


class BiGRU_Att_DANN(nn.Module):
    """
    BiGRU 2 couches + Attention Bahdanau + DANN.
    CNNPreEncoder → BiGRU(2L) → Attention (feat_dim=128) → label_head + domain_head.
    """
    def __init__(self, n_classes=N_CLASSES):
        super().__init__()
        self.pre_encoder = CNNPreEncoder(out_features=64)
        self.rnn = nn.GRU(64, 64, num_layers=2, batch_first=True,
                          bidirectional=True, dropout=0.3)
        self.attention = BahdanauAttention(128)
        self.label_head = nn.Sequential(
            nn.Linear(128, 32), nn.ReLU(), nn.Dropout(0.5), nn.Linear(32, n_classes),
        )
        self.domain_head = DomainClassifier(128)

    def forward(self, x, lambda_grl=1.0):
        out, _ = self.rnn(self.pre_encoder(x))
        feat, _ = self.attention(out)
        return self.label_head(feat), self.domain_head(feat, lambda_grl)


if __name__ == '__main__':
    dann_main("BiGRU_Att_DANN", BiGRU_Att_DANN)
