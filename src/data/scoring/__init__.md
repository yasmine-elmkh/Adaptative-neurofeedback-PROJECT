# __init__.py (scoring) — Documentation

## Vue d'ensemble

Fichier d'initialisation du package Python `src/data/scoring/`. Permet l'importation du package.

**Fichier :** `src/data/scoring/__init__.py`  
**Contenu :** Vide ou imports de facilité

## Package scoring

Ce package contient les scripts de scoring EEG du projet NeuroCap :

| Module | Description |
|--------|-------------|
| `concentration_scoring.py` | Score concentration 0-10 (Cognitive Load, 15 sujets) |
| `stress_scoring.py` | Score stress 0-10 (SAM40, 40 sujets, ground truth scales.xls) |
| `merge_scoring.py` | Fusion signaux+scores, rééchantillonnage → 250 Hz |
| `visualize_scoring.py` | 7 figures diagnostiques des distributions de scores |

## Pipeline de scoring

```
validate_concentration.py  ──→  concentration_scoring.py  ──┐
validate_stress.py         ──→  stress_scoring.py           ├──→  merge_scoring.py ──→ X_*.npy
                                                             │
                                                             └──→  visualize_scoring.py
```

## Usage

```python
# Étapes à exécuter dans l'ordre :
# 1. python src/data/validate_data/validate_concentration.py
# 2. python src/data/validate_data/validate_stress.py
# 3. python src/data/scoring/concentration_scoring.py
# 4. python src/data/scoring/stress_scoring.py
# 5. python src/data/scoring/merge_scoring.py
# 6. python src/data/scoring/visualize_scoring.py
```
