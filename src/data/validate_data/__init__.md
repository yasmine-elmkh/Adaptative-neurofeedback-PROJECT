# __init__.py (validate_data) — Documentation

## Vue d'ensemble

Fichier d'initialisation du package Python `src/data/validate_data/`. Permet l'importation du package depuis d'autres modules.

**Fichier :** `src/data/validate_data/__init__.py`  
**Contenu :** Vide ou imports de facilité  

## Package validate_data

Ce package contient les scripts de validation Phase 1 des datasets EEG :

| Module | Description |
|--------|-------------|
| `validate_stress.py` | Validation dataset SAM40 Stress (EMOTIV, .mat, 128 Hz) |
| `validate_concentration.py` | Validation dataset Cognitive Load (OpenBCI, .txt, 200 Hz) |

## Usage

```python
# Import direct des fonctions
from src.data.validate_data.validate_stress import main as validate_stress
from src.data.validate_data.validate_concentration import main as validate_concentration

# Ou exécution standalone
# python src/data/validate_data/validate_stress.py
# python src/data/validate_data/validate_concentration.py
```
