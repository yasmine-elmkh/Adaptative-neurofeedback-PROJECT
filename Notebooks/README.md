# NeuroCap — Notebooks

Jupyter notebooks used for exploratory data analysis (EDA) and prototyping during the NeuroCap ML pipeline development.

---

## Contents

| Notebook | Description |
|---|---|
| `EDA.ipynb` | Full exploratory data analysis: signal visualisation, class distribution, PSD plots, epoch statistics, feature correlation heatmap |

---

## Running notebooks

```bash
# Activate the ML environment and launch Jupyter
pip install jupyter
jupyter notebook Notebooks/EDA.ipynb
```

---

## EDA notebook — sections

1. **Dataset loading** — Load raw CSVs (concentration + stress), inspect shape and sampling rate
2. **Signal visualisation** — Plot raw EEG time series, identify artefacts visually
3. **Class distribution** — Bar charts and pie charts of label counts before/after augmentation
4. **Power Spectral Density** — Welch PSD per class, per frequency band (delta/theta/alpha/beta/gamma)
5. **Epoch statistics** — Mean, std, peak-to-peak per class; artefact rejection threshold analysis
6. **Feature correlation** — Heatmap of pairwise feature correlations; identify redundant features
7. **TBR & EI analysis** — Theta/Beta ratio and Engagement Index distributions per class
8. **IAPF detection** — Individual Alpha Peak Frequency estimation across subjects
9. **Augmentation effect** — Class balance before vs. after augmentation; signal quality check

---

## Dependencies

```bash
pip install jupyter numpy scipy pandas matplotlib seaborn mne pywavelets scikit-learn
```

---

## Output figures

Figures generated in the notebook are saved to `reports/EDA/` for reproducibility and documentation.
