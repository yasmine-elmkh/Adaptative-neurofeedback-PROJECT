"""NeuroCap – TCN sur datasets augmentés (A, B, C, D, FULL) + LOSO"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import torch.nn as nn
from DL_utils_regression import N_CLASSES, dl_main_regression

class TCNBlock(nn.Module):
    def __init__(self, in_ch, out_ch, dilation=1, dropout=0.2):
        super().__init__()
        padding = (7 - 1) * dilation // 2
        self.conv1 = nn.Conv1d(in_ch, out_ch, 7, padding=padding, dilation=dilation)
        self.bn1 = nn.BatchNorm1d(out_ch)
        self.conv2 = nn.Conv1d(out_ch, out_ch, 7, padding=padding, dilation=dilation)
        self.bn2 = nn.BatchNorm1d(out_ch)
        self.drop = nn.Dropout(dropout)
        self.relu = nn.ReLU()
        self.res = nn.Conv1d(in_ch, out_ch, 1) if in_ch != out_ch else nn.Identity()
    def forward(self, x):
        residual = self.res(x)
        x = self.relu(self.bn1(self.conv1(x)))
        x = self.drop(x)
        x = self.relu(self.bn2(self.conv2(x)))
        x = self.drop(x)
        return self.relu(x + residual)

class TCN(nn.Module):
    def __init__(self, n_classes=N_CLASSES):
        super().__init__()
        self.net = nn.Sequential(
            TCNBlock(1, 32, dilation=1), TCNBlock(32, 64, dilation=2),
            TCNBlock(64, 64, dilation=4), TCNBlock(64, 128, dilation=8),
        )
        self.fc = nn.Sequential(nn.AdaptiveAvgPool1d(1), nn.Flatten(), nn.Linear(128, n_classes))
    def forward(self, x):
        return self.fc(self.net(x))

if __name__ == '__main__':
    dl_main_regression("TCN", TCN)