# NeuroCap — Data Validation (`src/data/validate_data/`)

Holdout validation scripts that verify signal quality and class balance on the held-out test sets before training.

---

## Scripts

| Script | Description |
|---|---|
| `validate_concentration.py` | Quality checks on the concentration holdout set |
| `validate_stress.py` | Quality checks on the stress holdout set |

---

## Checks performed

- **Signal quality** — SNR, peak-to-peak amplitude, flat-line detection
- **Class balance** — epoch count per class, imbalance ratio
- **Feature distributions** — sanity check that key spectral features (alpha/beta/theta power) fall within expected ranges

---

## Usage

```bash
python src/data/validate_data/validate_concentration.py \
    --data data/Dataset/Cognitive_Load_Assessment_Concentration/ \
    --output reports/EDA/Validation/

python src/data/validate_data/validate_stress.py \
    --data data/Dataset/Stress_dataset/ \
    --output reports/EDA/Validation/
```

Results are saved to `reports/EDA/Validation/` as JSON reports and distribution plots.
