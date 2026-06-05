"""NeuroCap – CNN1D_DANN sur datasets augmentés (A, B, C, D, FULL) + LOSO"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import torch.nn as nn
from DL_utils import N_CLASSES
from DANN_utils import GradientReversalLayer, DomainClassifier, dann_main


class CNN1D_DANN(nn.Module):
    """
    CNN1D + DANN.
    Feature extraction identique à CNN1D (feat_dim=1024),
    suivi d'un label_head et d'un domain_head avec GRL.
    """
    def __init__(self, n_classes=N_CLASSES):
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv1d(1, 32, 25, padding=12), nn.BatchNorm1d(32), nn.ReLU(),
            nn.MaxPool1d(4), nn.Dropout(0.25),
            nn.Conv1d(32, 64, 15, padding=7), nn.BatchNorm1d(64), nn.ReLU(),
            nn.MaxPool1d(4), nn.Dropout(0.25),
            nn.Conv1d(64, 128, 5, padding=2), nn.BatchNorm1d(128), nn.ReLU(),
            nn.AdaptiveAvgPool1d(8),
        )
        self.flatten = nn.Flatten()
        self.label_head = nn.Sequential(
            nn.Linear(1024, 128), nn.BatchNorm1d(128), nn.ReLU(),
            nn.Dropout(0.5), nn.Linear(128, n_classes),
        )
        self.domain_head = DomainClassifier(1024)

    def forward(self, x, lambda_grl=1.0):
        feat = self.flatten(self.features(x))
        return self.label_head(feat), self.domain_head(feat, lambda_grl)


if __name__ == '__main__':
    dann_main("CNN1D_DANN", CNN1D_DANN)
