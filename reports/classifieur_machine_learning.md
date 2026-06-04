# Chapitre : Classifieur Machine Learning

## 1. Préparation des données et extraction des caractéristiques

Le pipeline d’apprentissage a été alimenté par les traitements de la section `src/data/` :

- `pipeline_fp2.py` réalise le filtrage, la correction de baseline, la segmentation en epochs et le rejet d’artefacts.
- `features_extraction.py` extrait les caractéristiques spectrales, temporelles et wavelet à partir des epochs fusionnées.
- `feature_eng.py` construit le jeu enrichi de 63 variables en utilisant la sélection de features, la normalisation et la réduction de dimension.

Ce pipeline permet d’obtenir un jeu de données exploitable pour la classification binaire `concentration` vs `stress`, avec une validation par leave-one-subject-out (LOSO) et une analyse par expériences `A`, `B`, `C`, `D`, `FULL`.

Les données sont ensuite remises aux modèles classiques de `src/models/baselines/` : SVM, Random Forest, XGBoost et LightGBM.

---

## 2. Modèles de classification testés

Les scripts de baselines sont regroupés dans `src/models/baselines/` :

- `baseline_ML.py` : entraînement et évaluation des modèles sur les caractéristiques brutes.
- `baseline_ML_feature_eng.py` : entraînement sur les caractéristiques ingénierées (63 features).
- `compare_baselines_features.py` : comparaison brute vs caractéristiques enrichies.

Les modèles implémentés sont :

- SVM (RBF)
- Random Forest
- XGBoost
- LightGBM

Les résultats de comparaison montrent que les features ingénierées améliorent significativement les performances de tous les classifieurs, ce qui justifie leur utilisation dans le chapitre de classification.

---

## 3. Résultats expérimentaux

Les sorties de synthèse sont stockées dans `reports/baseline_FeatEng/outputs_baseline/` avec le fichier `report_all.txt` qui centralise les métriques par expérience.

### Résumé des performances (features ingénierées)

| Expérience | SVM | Random Forest | XGBoost | LightGBM |
|---|---:|---:|---:|---:|
| A | Acc 0.8930 / F1-macro 0.8899 / AUC 0.9636 | Acc 0.8694 / F1-macro 0.8661 / AUC 0.9488 | Acc 0.9061 / F1-macro 0.9042 / AUC 0.9679 | Acc 0.9001 / F1-macro 0.8982 / AUC 0.9667 |
| B | Acc 0.8974 / F1-macro 0.8947 / AUC 0.9666 | Acc 0.8768 / F1-macro 0.8736 / AUC 0.9503 | Acc 0.8996 / F1-macro 0.8972 / AUC 0.9681 | Acc 0.9004 / F1-macro 0.8982 / AUC 0.9673 |
| C | Acc 0.9054 / F1-macro 0.9030 / AUC 0.9697 | Acc 0.8776 / F1-macro 0.8746 / AUC 0.9516 | Acc 0.8985 / F1-macro 0.8961 / AUC 0.9688 | Acc 0.8996 / F1-macro 0.8974 / AUC 0.9680 |
| D | Acc 0.9012 / F1-macro 0.8987 / AUC 0.9692 | Acc 0.8735 / F1-macro 0.8705 / AUC 0.9485 | Acc 0.8968 / F1-macro 0.8946 / AUC 0.9654 | Acc 0.9018 / F1-macro 0.8997 / AUC 0.9647 |
| FULL | Acc 0.9053 / F1-macro 0.9029 / AUC 0.9714 | Acc 0.8768 / F1-macro 0.8737 / AUC 0.9510 | Acc 0.9015 / F1-macro 0.8993 / AUC 0.9694 | Acc 0.8965 / F1-macro 0.8944 / AUC 0.9682 |

Le meilleur score global de la synthèse est obtenu par XGBoost sur l’expérience A avec un F1-macro de `0.9042`.

---

## 4. Pourquoi retenir LightGBM comme classifieur principal

Malgré le fait que XGBoost soit légèrement meilleur sur certaines expériences, LightGBM constitue le meilleur compromis pour ce projet pour plusieurs raisons techniques et opérationnelles :

1. **Performance stable et très compétitive** : les scores de LightGBM restent très proches des meilleurs modèles sur l’ensemble des expériences, avec un F1-macro autour de `0.898–0.900` et une AUC proche de `0.965–0.968`.
2. **Efficacité computationnelle** : LightGBM est optimisé pour les jeux de données tabulaires structurés grâce à son apprentissage histogramme et à la croissance par feuilles, ce qui réduit le temps d’entraînement et la mémoire consommée.
3. **Adapté au temps réel** : le backend de l’application utilise directement un classifieur LightGBM sur les 63 features enrichies (`app/Backend/app/services/eeg/dsp/ml_classifier.py`), ce qui confirme sa sélection pour l’inférence opérationnelle.
4. **Déploiement natif et cohérent avec le pipeline** : les modèles LightGBM sont sauvegardés dans `models/baseline_FeatEng/baseline_models/` et intégrés au service de classification en temps réel, ce qui simplifie la chaîne de déploiement.
5. **Robustesse pour la classification EEG** : LightGBM gère bien les relations non linéaires entre caractéristiques EEG, tout en restant rapide et stable sur des features normalisées et sélectionnées.

En résumé, LightGBM n’est pas toujours le meilleur en précision brute absolue, mais il est le **meilleur modèle d’implémentation** : performant, rapide, léger, et directement exploitable dans l’application finale.

---

## 5. Figures à insérer dans le rapport

Les images suivantes peuvent être insérées dans la section de classification pour illustrer les résultats de LightGBM et la comparaison globale :

- `Figure 1 — Matrice de confusion LightGBM (FULL)`  
  `![Matrice de confusion LightGBM](reports/baseline_FeatEng/outputs_baseline/FULL/LightGBM/confusion_matrix_norm.png)`

- `Figure 2 — Courbe ROC LightGBM (FULL)`  
  `![Courbe ROC LightGBM](reports/baseline_FeatEng/outputs_baseline/FULL/LightGBM/roc_curve.png)`

- `Figure 3 — Distribution des probabilités LightGBM (FULL)`  
  `![Distribution des probabilités LightGBM](reports/baseline_FeatEng/outputs_baseline/FULL/LightGBM/probability_distribution.png)`

- `Figure 4 — Comparaison globale des classifieurs`  
  `![Comparaison globale](reports/baseline_FeatEng/outputs_baseline/comparison_all.png)`

- `Figure 5 — Synthèse textuelle des résultats`  
  *(source de synthèse : `reports/baseline_FeatEng/outputs_baseline/report_all.txt`)*

---

## 6. Références internes du projet

- `src/data/README.md` : description du pipeline de prétraitement et d’extraction des features.
- `src/models/baselines/README.md` : scripts et résultats des baselines classiques.
- `reports/README.md` : structure des sorties et résultats globaux.
- `reports/baseline_FeatEng/outputs_baseline/report_all.txt` : synthèse quantitative des performances.
- `models/baseline_FeatEng/baseline_models/` : modèles sauvegardés pour l’inférence.
- `app/Backend/app/services/eeg/dsp/ml_classifier.py` : classifieur LightGBM déployé en temps réel.
