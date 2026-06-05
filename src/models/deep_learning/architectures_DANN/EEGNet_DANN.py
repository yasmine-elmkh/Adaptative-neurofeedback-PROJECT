"""NeuroCap – EEGNet_DANN sur datasets augmentés (A, B, C, D, FULL) + LOSO"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import torch, torch.nn as nn
from DL_utils import N_CLASSES, EPOCH_SAMPLES
from DANN_utils import DomainClassifier, dann_main


class EEGNet_DANN(nn.Module):
    """
    EEGNet + DANN.
    Convolutions dépthwise séparables (feat_dim dynamique) → label_head + domain_head.
    """
    def __init__(self, n_classes=N_CLASSES, F1=8, D=2, F2=16, dropout=0.5):
        super().__init__()
        self.conv1   = nn.Conv2d(1, F1, (1, 64), padding=(0, 32), bias=False)
        self.bn1     = nn.BatchNorm2d(F1)
        self.dw      = nn.Conv2d(F1, F1 * D, (1, 1), groups=F1, bias=False)
        self.bn2     = nn.BatchNorm2d(F1 * D)
        self.elu     = nn.ELU()
        self.pool1   = nn.AvgPool2d((1, 4))
        self.drop1   = nn.Dropout(dropout)
        self.sep_dw  = nn.Conv2d(F1 * D, F1 * D, (1, 16), padding=(0, 8),
                                 groups=F1 * D, bias=False)
        self.sep_pw  = nn.Conv2d(F1 * D, F2, (1, 1), bias=False)
        self.bn3     = nn.BatchNorm2d(F2)
        self.pool2   = nn.AvgPool2d((1, 8))
        self.drop2   = nn.Dropout(dropout)
        feat_dim = self._compute_feat_dim()
        self.label_head  = nn.Linear(feat_dim, n_classes)
        self.domain_head = DomainClassifier(feat_dim)

    def _compute_feat_dim(self):
        with torch.no_grad():
            return self._forward_features(
                torch.zeros(1, 1, 1, EPOCH_SAMPLES)).shape[1]

    def _forward_features(self, x):
        x = self.bn1(self.conv1(x))
        x = self.elu(self.bn2(self.dw(x)))
        x = self.drop1(self.pool1(x))
        x = self.sep_pw(self.sep_dw(x))
        x = self.elu(self.bn3(x))
        return self.drop2(self.pool2(x)).flatten(1)

    def forward(self, x, lambda_grl=1.0):
        if x.dim() == 3:
            x = x.unsqueeze(1)
        feat = self._forward_features(x)
        return self.label_head(feat), self.domain_head(feat, lambda_grl)


if __name__ == '__main__':
    dann_main("EEGNet_DANN", EEGNet_DANN)
