"""
NeuroCap – Rapport d'analyse : Approches Baseline (ML classique)
Génère : reports/Tests/rapports/RAPPORT_BASELINE.txt
"""

import json
import os
from pathlib import Path
from datetime import datetime

# ─── Chemins ────────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
BL_JSON      = PROJECT_ROOT / 'reports' / 'Tests' / 'baselines'      / 'results.json'
CMP_JSON     = PROJECT_ROOT / 'reports' / 'Tests' / 'comparison_dann' / 'summary.json'
OUT_DIR      = PROJECT_ROOT / 'reports' / 'Tests' / 'rapports'
OUT_FILE     = OUT_DIR / 'RAPPORT_BASELINE.txt'

OUT_DIR.mkdir(parents=True, exist_ok=True)


# ─── Chargement des données ─────────────────────────────────────────────────
def load_data():
    bl  = json.loads(BL_JSON.read_text(encoding='utf-8'))  if BL_JSON.exists()  else {}
    cmp = json.loads(CMP_JSON.read_text(encoding='utf-8')) if CMP_JSON.exists() else {}
    return bl, cmp


def write_rapport(bl: dict, cmp: dict) -> str:
    lines = []
    W = 78

    def h1(t): lines.append('=' * W); lines.append(t.center(W)); lines.append('=' * W)
    def h2(t): lines.append(''); lines.append(t); lines.append('─' * W)
    def p(*args): lines.append(' '.join(str(a) for a in args))
    def nl(): lines.append('')

    # ── En-tête ─────────────────────────────────────────────────────────────
    h1("NEUROCAP – RAPPORT D'ANALYSE : APPROCHES BASELINE (ML CLASSIQUE)")
    p(f"Date de génération : {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    p(f"Source de données  : {BL_JSON.relative_to(PROJECT_ROOT)}")
    p(f"Méthode d'éval.    : Holdout (test set fixe, sujets disjoint du train)")

    # ── Contexte du projet ──────────────────────────────────────────────────
    h2("1. CONTEXTE ET OBJECTIF")
    p("""Le projet NeuroCap vise à classifier en temps réel deux états cognitifs distincts
à partir de signaux EEG bruts :
  • Concentration  (label 0)  →  casque OpenBCI (domaine 0)
  • Stress         (label 1)  →  casque EMOTIV  (domaine 1)

Les approches ML classiques (Baseline) constituent la première ligne de comparaison.
Elles opèrent sur un vecteur de 80 features ingéniérées (FeatEng-80f) extraites des
signaux bruts (bande de puissance, cohérence inter-canaux, asymétrie frontale, etc.)
et sont évaluées sur un ensemble holdout de 299 exemples issus de 7 sujets jamais
vus à l'entraînement.
""")

    # ── Résultats ───────────────────────────────────────────────────────────
    h2("2. RÉSULTATS COMPARATIFS – MODÈLES BASELINE")
    if bl:
        results = sorted(bl.get('all_results', []),
                         key=lambda r: r['f1_macro'], reverse=True)
        header = f"{'Rang':<5} {'Modèle':<30} {'F1-Macro':>9} {'AUC':>9} {'Accuracy':>9} " \
                 f"{'Recall':>8} {'Specif.':>8} {'Incert.%':>9}"
        p(header)
        p('─' * W)
        for i, r in enumerate(results, 1):
            flag = ' ← MEILLEUR' if i == 1 else ''
            p(f"{i:<5} {r['model_feat']:<30} {r['f1_macro']:>9.4f} {r['auc']:>9.4f} "
              f"{r['accuracy']:>9.4f} {r['recall']:>8.4f} {r['specificity']:>8.4f} "
              f"{r['pct_uncertain']:>8.2f}%{flag}")

    nl()
    # ── Analyse modèle par modèle ────────────────────────────────────────────
    h2("3. ANALYSE DÉTAILLÉE PAR MODÈLE")
    p("""
┌─ LightGBM-FeatEng-80f  [RECOMMANDÉ] ──────────────────────────────────────┐
│  F1-Macro = 0.9630  |  AUC = 0.9941  |  Accuracy = 96.7%                  │
│  Recall = 0.9646    |  Spécificité = 0.9703  |  Incertitude = 1.67%        │
│                                                                             │
│  Points forts :                                                             │
│  • Meilleur F1-macro et accuracy parmi les 4 baselines                     │
│  • AUC = 0.9941 : capacité discriminante quasi-parfaite                    │
│  • Taux d'incertitude le plus bas (1.67%)  →  peu de cas ambigus           │
│  • Gradient boosting par feuilles (leaf-wise) : moins de variance que XGB  │
│  • Robuste aux features redondantes dans FeatEng-80f                       │
│  Limitation :                                                               │
│  • Inference time 2.9s (feature extraction comprise, non le modèle seul)   │
│  • Nécessite un pipeline de feature engineering pré-calibré                │
└─────────────────────────────────────────────────────────────────────────────┘

┌─ XGBoost-FeatEng-80f ──────────────────────────────────────────────────────┐
│  F1-Macro = 0.9558  |  AUC = 0.9963  |  Accuracy = 95.99%                 │
│  Precision = 0.9844 (la plus haute!)  |  Recall = 0.9545                   │
│                                                                             │
│  Points forts :                                                             │
│  • AUC légèrement supérieur à LightGBM (0.9963 vs 0.9941)                  │
│  • Precision la plus élevée → très peu de faux positifs stress             │
│  • Excellent choix si on veut minimiser les fausses alarmes stress          │
│  Limitation :                                                               │
│  • F1-Macro inférieur de 0.72pp par rapport à LightGBM                     │
│  • Recall légèrement plus faible (0.9545 vs 0.9646)                        │
└─────────────────────────────────────────────────────────────────────────────┘

┌─ Random Forest-FeatEng-80f ────────────────────────────────────────────────┐
│  F1-Macro = 0.9455  |  AUC = 0.9970  |  Accuracy = 94.98%                 │
│  Recall = 0.9293    |  Incertitude = 8.03%  (la plus haute!)               │
│                                                                             │
│  • AUC très élevé (0.9970) mais F1 plus faible → seuil de décision         │
│    sous-optimal, beaucoup de cas "incertains" (8.03%)                      │
│  • Moins adapté pour le déploiement temps réel (incertitude élevée)        │
└─────────────────────────────────────────────────────────────────────────────┘

┌─ SVM-FeatEng-80f ──────────────────────────────────────────────────────────┐
│  F1-Macro = 0.9334  |  AUC = 0.9830  |  Accuracy = 93.98%                 │
│  Incertitude = 1.67%  |  Temps inference = 0.044s (le plus rapide!)        │
│                                                                             │
│  • Inference la plus rapide de tous les baselines (~44ms)                  │
│  • Mais F1 et AUC inférieurs aux autres → acceptable en contrainte IoT     │
│    seulement si la vitesse est critique et la précision secondaire          │
└─────────────────────────────────────────────────────────────────────────────┘
""")

    # ── Discussion critique ──────────────────────────────────────────────────
    h2("4. DISCUSSION : LIMITES DES APPROCHES BASELINE")
    p("""Les approches ML classiques présentent plusieurs limites structurelles par rapport
aux approches deep learning pour ce problème :

  a) DÉPENDANCE À L'INGÉNIERIE DE FEATURES :
     Les 80 features (FeatEng-80f) nécessitent un calcul explicite (FFT, cohérence,
     Hjorth parameters, etc.). Tout changement de matériel (fréquence d'échantillonnage,
     nombre de canaux) invalide le pipeline de features. Les DL apprennent directement
     depuis le signal brut.

  b) GÉNÉRALISATION INTER-SUJETS LIMITÉE :
     En holdout, LightGBM atteint 96.7%, mais en LOSO (leave-one-subject-out), les
     DL atteignent 99.77% (CNN2D). La différence s'élargit sur des nouveaux sujets.

  c) ABSENCE D'ADAPTATION EN LIGNE :
     Impossible de fine-tuner un LightGBM sur quelques exemples d'un nouveau sujet.
     Les DL permettent une adaptation rapide (fine-tuning head-only en <5 secondes
     sur 109 échantillons).

  d) TRAITEMENT TEMPOREL :
     Les features agrègent la dimension temporelle (fenêtre de 4s → 1 vecteur).
     Un CNN2D traite le signal comme une image temps-fréquence et préserve la
     structure temporelle fine, ce qui est crucial pour les transitoires EEG.
""")

    # ── Comparaison globale ─────────────────────────────────────────────────
    if cmp:
        h2("5. POSITIONNEMENT DANS LA COMPARAISON GLOBALE")
        bp = cmp.get('best_per_category', {})
        bl_info = bp.get('Baseline ML', {})
        dl_info = bp.get('Deep Learning', {})
        dann_info = bp.get('DANN', {})
        ft_info  = bp.get('Fine-tuning', {})
        p(f"{'Catégorie':<20} {'Meilleur modèle':<35} {'F1-Macro':>9} {'Score':>8}")
        p('─' * W)
        for cat, info in [('Baseline ML', bl_info), ('Deep Learning', dl_info),
                          ('DANN', dann_info), ('Fine-tuning', ft_info)]:
            if info:
                flag = ' ←' if cat == 'Baseline ML' else ''
                p(f"{cat:<20} {info.get('model','N/A'):<35} "
                  f"{info.get('f1_macro',0):>9.4f} {info.get('score',0):>8.4f}{flag}")
        nl()
        gap = dl_info.get('f1_macro', 0) - bl_info.get('f1_macro', 0) if dl_info and bl_info else 0
        p(f"  → Écart Baseline vs Deep Learning : +{gap:.4f} F1-macro en faveur du DL")
        p(f"  → Les approches DL/DANN/FT surpassent toutes les baselines ML classiques.")

    # ── Recommandation ───────────────────────────────────────────────────────
    h2("6. RECOMMANDATION ARGUMENTÉE")
    p("""
VERDICT :  LightGBM-FeatEng-80f  est le MEILLEUR MODÈLE BASELINE.
══════════════════════════════════════════════════════════════════

Arguments :
  ✓  F1-Macro = 0.9630  (le plus élevé parmi les 4 baselines)
  ✓  AUC = 0.9941       (capacité de ranking quasi-parfaite)
  ✓  Taux d'incertitude le plus bas (1.67%)
  ✓  Recall et Spécificité équilibrés → adapté à la détection stress+concentration
  ✓  Entraînable rapidement, interprétable (feature importance), déployable sur CPU

Quand utiliser LightGBM (contexte BCI embarqué/offline) :
  • Contraintes matérielles fortes (pas de GPU, mémoire RAM limitée)
  • Besoin de haute interprétabilité (feature importance visible)
  • Pipeline offline (batch processing, pas de streaming temps réel)
  • Prototypage rapide avant investissement dans l'infrastructure DL

Quand NE PAS utiliser LightGBM (recommander CNN2D à la place) :
  • Nouveaux sujets non vus → le modèle DL généralise mieux (+3.47pp F1)
  • Nouveaux casques EEG → features invalides, DL adaptable via fine-tuning
  • Application temps réel → pas de recompute de features, inférence DL en <1ms/batch
  • Besoin d'adaptation continue → fine-tuning DL possible, pas GBDT

CONCLUSION : LightGBM est une solide baseline mais reste en retrait de 3.47pp F1-Macro
par rapport au CNN2D (DL). Pour un déploiement production NeuroCap, CNN2D est recommandé.
LightGBM reste pertinent comme référence comparative et pour des contextes embarqués très
contraints où le DL n'est pas envisageable.
""")

    h2("7. FICHIERS GÉNÉRÉS")
    p(f"  • {OUT_FILE.relative_to(PROJECT_ROOT)}")
    p(f"  • Source : {BL_JSON.relative_to(PROJECT_ROOT)}")
    p(f"  Rapport généré le {datetime.now().strftime('%Y-%m-%d à %H:%M:%S')}")
    lines.append('=' * W)

    return '\n'.join(lines)


def main():
    print("NeuroCap – Génération du rapport BASELINE...")
    bl, cmp = load_data()
    if not bl:
        print(f"[ERREUR] Fichier non trouvé : {BL_JSON}")
        print("  → Lancez d'abord : python Tests/test_baselines.py")
        return
    rapport = write_rapport(bl, cmp)
    OUT_FILE.write_text(rapport, encoding='utf-8')
    print(rapport)
    print(f"\n✓ Rapport sauvegardé : {OUT_FILE}")


if __name__ == '__main__':
    main()
