# visualize_scoring.py — Documentation Détaillée

## Vue d'ensemble

`visualize_scoring.py` génère 7 figures de visualisation à partir des CSVs de scores produits par `concentration_scoring.py` et `stress_scoring.py`. Il fournit un tableau de bord visuel complet pour valider la qualité et la distribution des scores.

**Fichier :** `src/data/scoring/visualize_scoring.py`  
**Lignes :** ~445  
**Rôle :** Visualisation des scores — 7 figures PNG dans `reports/scoring/merge/`

---

## Fonctions utilitaires

### `save(fig, name)`
Sauvegarde une figure matplotlib dans `reports/scoring/merge/` avec un préfixe numéroté.

**Paramètres :**
- `fig` — Figure matplotlib
- `name` — Nom de fichier (ex: `'01_score_distributions'`)

**Résolution :** 150 DPI, format PNG.

---

### `load_csvs()`
Charge les deux CSVs de scores.

**Retourne :** `(df_c, df_s)` — DataFrames concentration et stress

---

## 7 Figures générées

### Figure 1 — `fig_score_distributions(df_c, df_s)`

**Fichier :** `01_score_distributions.png`

**Description :** Histogrammes comparatifs des distributions de scores concentration vs stress.

**Layout :** 2 subplots côte à côte
- Gauche : distribution scores concentration (bleu)
- Droite : distribution scores stress (rouge)

**Informations affichées :**
- Histogramme des scores
- Courbe de densité KDE
- Ligne verticale à 5.0 (seuil Low/High)
- Statistiques : N, mean, std, % high

---

### Figure 2 — `fig_conc_by_level(df_c)`

**Fichier :** `02_conc_by_level.png`

**Description :** Boxplots des scores de concentration par niveau cognitif.

**Layout :** 1 subplot
- Axe X : niveaux (natural, lowlevel, midlevel, highlevel)
- Axe Y : score concentration [0-10]
- Couleurs par niveau

**Vérification attendue :** Les boîtes doivent se superposer partiellement mais montrer une progression claire : natural < lowlevel < midlevel < highlevel.

---

### Figure 3 — `fig_stress_by_task(df_s)`

**Fichier :** `03_stress_by_task.png`

**Description :** Boxplots des scores de stress par type de tâche.

**Layout :** 1 subplot
- Axe X : tâches (relax, maths, sym, stroop)
- Axe Y : score stress [0-10]

**Vérification attendue :** relax ≈ 0.5-1.5, tâches stressantes ≈ 5-9.

---

### Figure 4 — `fig_conc_by_subject(df_c)`

**Fichier :** `04_conc_by_subject.png`

**Description :** Score moyen de concentration par sujet (barres avec intervalles de confiance).

**Layout :** 1 subplot
- Axe X : sujets (1-15)
- Axe Y : score moyen ± std
- Coloré par score moyen (gradient bleu)

**Utilité :** Identifier les sujets avec des profils EEG atypiques (score très faible ou très élevé quelle que soit la tâche).

---

### Figure 5 — `fig_stress_by_subject(df_s)`

**Fichier :** `05_stress_by_subject.png`

**Description :** Score moyen de stress par sujet (sujets 1-40).

**Layout :** Identique à Figure 4 mais pour le stress.

---

### Figure 6 — `fig_epochs_count(df_c, df_s)`

**Fichier :** `06_epochs_count.png`

**Description :** Nombre d'époques par sujet pour les deux datasets.

**Layout :** 2 subplots
- Gauche : époques par sujet concentration
- Droite : époques par sujet stress

**Utilité :** Détecter les déséquilibres de données entre sujets (certains sujets peuvent avoir moins d'époques après rejet d'artefacts).

---

### Figure 7 — `fig_dataset_overview(df_c, df_s)`

**Fichier :** `07_dataset_overview.png`

**Description :** Vue d'ensemble comparant les deux datasets sur les métriques clés.

**Layout :** Grille 2×3
- (1,1) : Scatter score_conc vs score_stress (pour sujets communs si applicable)
- (1,2) : Distribution classe Low/High pour concentration
- (1,3) : Distribution classe Low/High pour stress
- (2,1) : Timeline des scores par sujet (heatmap)
- (2,2) : Corrélation features-scores (correlation matrix)
- (2,3) : Tableau récapitulatif (N époquess, N sujets, % high)

---

### `main()`

```python
df_c, df_s = load_csvs()

fig1 = fig_score_distributions(df_c, df_s)    → save(fig1, '01_score_distributions')
fig2 = fig_conc_by_level(df_c)                → save(fig2, '02_conc_by_level')
fig3 = fig_stress_by_task(df_s)               → save(fig3, '03_stress_by_task')
fig4 = fig_conc_by_subject(df_c)              → save(fig4, '04_conc_by_subject')
fig5 = fig_stress_by_subject(df_s)            → save(fig5, '05_stress_by_subject')
fig6 = fig_epochs_count(df_c, df_s)           → save(fig6, '06_epochs_count')
fig7 = fig_dataset_overview(df_c, df_s)       → save(fig7, '07_dataset_overview')
```

**Sortie :** `reports/scoring/merge/01_*.png` à `07_*.png`
