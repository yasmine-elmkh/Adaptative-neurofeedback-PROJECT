"""
=============================================================================
NeuroCap – Baseline ML (SVM + RF + XGBoost + LightGBM)
baseline_ML.py
=============================================================================
Sortie : [P(Concentration)%, P(Stress)%] — CdC Section 2.5.1
Métriques : Accuracy, F1-binary, F1-MACRO, AUC, Precision, Recall, Spécificité
Validation : LOSO + Val/Test

=== AJOUTS PAR RAPPORT À LA VERSION PRÉCÉDENTE ===
  1. LightGBM ajouté (Phase 2 du CdC)
  2. F1-MACRO ajouté comme métrique principale
  3. Distribution des probabilités (nouvelle figure)
  4. % d'époques incertaines (CdC : max(P) < 0.60)
  5. Sélection du meilleur modèle par F1-MACRO (pas F1-binary)
=============================================================================
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
import lightgbm as lgb
from sklearn.metrics import (accuracy_score, precision_score, recall_score, f1_score,
                             confusion_matrix, roc_curve, auc, classification_report,
                             roc_auc_score)
from sklearn.preprocessing import StandardScaler
import os, warnings, joblib, json, time
from pathlib import Path

warnings.filterwarnings('ignore')
plt.style.use('seaborn-v0_8-whitegrid')

COLORS = {'SVM':'#E74C3C','Random Forest':'#2980B9','XGBoost':'#27AE60','LightGBM':'#F39C12'}

script_dir = Path(__file__).resolve().parent.parent.parent.parent

FEATURES_DIR = script_dir / 'features' /'features_extraction'
EXPERIMENTS = ['A', 'B', 'C', 'D', 'FULL']
OUTPUT_DIR = script_dir / 'reports' / 'Baseline' / 'baselines_outputs'
MODEL_SAVE_ROOT = script_dir / 'models' / 'Baseline' / 'baseline_models'

MODELS = {
    'SVM': SVC(kernel='rbf', C=1.0, gamma='scale', probability=True, random_state=42),
    'Random Forest': RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42),
    'XGBoost': XGBClassifier(n_estimators=100, max_depth=6, learning_rate=0.1,
                              use_label_encoder=False, eval_metric='logloss',
                              random_state=42, verbosity=0),
    'LightGBM': lgb.LGBMClassifier(n_estimators=100, max_depth=8, learning_rate=0.1,
                                     num_leaves=31, random_state=42, verbose=-1,
                                     force_col_wise=True),
}

# ============================================================================
def compute_metrics(y_true, y_pred, y_proba=None):
    cm = confusion_matrix(y_true, y_pred)
    if cm.size == 1:
        val = cm[0,0]; unique = np.unique(y_true)[0]
        if unique == 1: tp,tn,fp,fn = val,0,0,0
        else: tn,tp,fp,fn = val,0,0,0
    else:
        tn,fp,fn,tp = cm.ravel()

    m = {
        'accuracy':    accuracy_score(y_true, y_pred),
        'precision':   precision_score(y_true, y_pred, zero_division=0),
        'recall':      recall_score(y_true, y_pred, zero_division=0),
        'f1':          f1_score(y_true, y_pred, zero_division=0),
        'f1_macro':    f1_score(y_true, y_pred, average='macro', zero_division=0),
        'specificity': tn/(tn+fp) if (tn+fp)>0 else 0.0,
    }
    if y_proba is not None:
        try: m['auc'] = roc_auc_score(y_true, y_proba)
        except: m['auc'] = 0.5
    else: m['auc'] = 0.5
    return m


import numpy as np
from pathlib import Path

FEATURES_DIR = script_dir / 'features' /  'baseline' /'datasets_features_extraction'
exp = 'A'

# Chargement des features, labels et subject_ids
X = np.load(FEATURES_DIR / f'features_{exp}.npy')
y = np.load(FEATURES_DIR / f'labels_{exp}.npy')
sids = np.load(FEATURES_DIR / f'subject_ids_{exp}.npy')

print("=== INSPECTION DES DONNÉES ===")
print(f"Nombre d'époques : {len(X)}")
print(f"Nombre de sujets uniques : {len(np.unique(sids))}")
print(f"IDs des sujets : {np.unique(sids)}")
print("\nDistribution des labels par sujet :")
for sid in np.unique(sids):
    mask = sids == sid
    n_conc = np.sum(y[mask] == 0)
    n_stress = np.sum(y[mask] == 1)
    print(f"  Sujet {sid}: {np.sum(mask)} époques, {n_conc} conc, {n_stress} stress")
    if n_conc > 0 and n_stress > 0:
        print(f"    ⚠️ SUJET MIXTE (les deux labels) -> fuite certaine !")

# Test simple sans classifieur : calculer la distance entre les centres des deux classes
class0 = X[y==0]
class1 = X[y==1]
print(f"\nSéparabilité : distance euclidienne entre les centroïdes = {np.linalg.norm(class0.mean(0) - class1.mean(0)):.2f}")


def loso_cv(X, y, sids, model):
    unique_s = np.unique(sids)
    if len(unique_s) < 2:
        return [],[],[],[],{'accuracy':0,'f1':0,'f1_macro':0,'auc':0,
                            'precision':0,'recall':0,'specificity':0}
    yt_all, yp_all, yprob_all = [],[],[]
    fold_metrics = []
    n_uncertain = 0

    for ts in unique_s:
        tr_mask = sids != ts; te_mask = sids == ts
        Xtr,ytr = X[tr_mask],y[tr_mask]; Xte,yte = X[te_mask],y[te_mask]
        if len(np.unique(ytr)) < 2:
            fold_metrics.append({'accuracy':0,'f1':0,'f1_macro':0,'auc':0.5,
                                  'precision':0,'recall':0,'specificity':0,
                                  'n_samples':len(yte),'valid':False,'subject':int(ts)})
            continue
        sc = StandardScaler(); Xtr_s = sc.fit_transform(Xtr); Xte_s = sc.transform(Xte)
        mc = model.__class__(**model.get_params()); mc.fit(Xtr_s, ytr)
        yp = mc.predict(Xte_s)
        yprob = mc.predict_proba(Xte_s)[:,1] if hasattr(mc,'predict_proba') else None
        if yprob is not None:
            max_p = np.max(mc.predict_proba(Xte_s), axis=1)
            n_uncertain += int(np.sum(max_p < 0.60))
        yt_all.extend(yte); yp_all.extend(yp)
        if yprob is not None: yprob_all.extend(yprob)
        fm = compute_metrics(yte, yp, yprob)
        fm['n_samples']=len(yte); fm['valid']=True; fm['subject']=int(ts)
        fold_metrics.append(fm)

    if yt_all:
        gm = compute_metrics(yt_all, yp_all, yprob_all if yprob_all else None)
    else:
        gm = {'accuracy':0,'f1':0,'f1_macro':0,'auc':0,'precision':0,'recall':0,'specificity':0}
    gm['n_folds_total']=len(unique_s)
    gm['n_folds_valid']=sum(1 for f in fold_metrics if f.get('valid'))
    gm['n_uncertain']=n_uncertain
    gm['pct_uncertain']=(n_uncertain/len(yt_all)*100) if yt_all else 0
    return yt_all, yp_all, yprob_all, fold_metrics, gm


def eval_split(model, scaler, split, fdir):
    fp = fdir/f'features_{split}.npy'; lp = fdir/f'labels_{split}.npy'
    if not fp.exists() or not lp.exists(): return None
    X=np.load(fp); y=np.load(lp)
    if len(X)==0: return None
    Xs=scaler.transform(X); yp=model.predict(Xs)
    yprob=model.predict_proba(Xs)[:,1] if hasattr(model,'predict_proba') else None
    m=compute_metrics(y,yp,yprob); m['n_samples']=len(y)
    if yprob is not None:
        mx=np.max(model.predict_proba(Xs),axis=1)
        m['n_uncertain']=int(np.sum(mx<0.60)); m['pct_uncertain']=m['n_uncertain']/len(y)*100
    return m


# ============================================================================
# VISUALISATIONS
# ============================================================================
def plot_cm(yt,yp,mn,exp,sd):
    cm=confusion_matrix(yt,yp)
    if cm.shape==(1,1): cm=np.array([[cm[0,0],0],[0,0]])
    cmn=cm.astype(float)/(cm.sum(axis=1,keepdims=True)+1e-12)
    plt.figure(figsize=(6,5))
    sns.heatmap(cmn,annot=True,fmt='.2%',cmap='Blues',
                xticklabels=['Concentration','Stress'],yticklabels=['Concentration','Stress'])
    plt.title(f'Matrice confusion — {mn} (Exp.{exp})'); plt.ylabel('Vérité'); plt.xlabel('Prédiction')
    plt.tight_layout(); plt.savefig(os.path.join(sd,'confusion_matrix_norm.png'),dpi=150); plt.close()

def plot_roc(yt,yp,mn,exp,sd):
    if yp is None or len(yp)==0 or len(np.unique(yt))<2: return
    fpr,tpr,_=roc_curve(yt,yp); ra=auc(fpr,tpr)
    plt.figure(figsize=(6,5))
    plt.plot(fpr,tpr,lw=2,label=f'AUC={ra:.3f}',color=COLORS.get(mn,'#27AE60'))
    plt.plot([0,1],[0,1],'k--',lw=1)
    plt.xlabel('FPR'); plt.ylabel('TPR'); plt.title(f'ROC — {mn} (Exp.{exp})')
    plt.legend(); plt.grid(alpha=0.3); plt.tight_layout()
    plt.savefig(os.path.join(sd,'roc_curve.png'),dpi=150); plt.close()

def plot_proba_dist(yt,yprob,mn,exp,sd):
    """Distribution des P(Stress) — montre la séparation des classes."""
    if yprob is None or len(yprob)==0: return
    plt.figure(figsize=(8,5))
    ya,pa = np.array(yt), np.array(yprob)
    if np.sum(ya==0)>0:
        plt.hist(pa[ya==0],bins=25,alpha=0.6,color='#2980B9',label='Concentration (0)',density=True)
    if np.sum(ya==1)>0:
        plt.hist(pa[ya==1],bins=25,alpha=0.6,color='#E74C3C',label='Stress (1)',density=True)
    plt.axvspan(0.40,0.60,alpha=0.12,color='gray',label='Zone incertaine CdC')
    plt.axvline(0.60,color='red',ls=':',lw=1.5,label='Seuil CdC 0.60')
    plt.xlabel('P(Stress)'); plt.ylabel('Densité')
    plt.title(f'Distribution probabilités — {mn} (Exp.{exp})\nsi max(P)<0.60 → feedback suspendu')
    plt.legend(fontsize=8); plt.grid(alpha=0.3); plt.tight_layout()
    plt.savefig(os.path.join(sd,'probability_distribution.png'),dpi=150); plt.close()

def plot_folds(fms,mn,exp,sd):
    if not fms: return
    folds=np.arange(1,len(fms)+1)
    plt.figure(figsize=(12,5))
    plt.plot(folds,[m['accuracy'] for m in fms],'o-',label='Accuracy',color='#3498DB',lw=2)
    plt.plot(folds,[m['f1'] for m in fms],'^-',label='F1-binary',color='#E74C3C',lw=2)
    plt.plot(folds,[m.get('f1_macro',0) for m in fms],'s-',label='F1-MACRO',color='#27AE60',lw=2)
    plt.xlabel('Sujet test (fold)'); plt.ylabel('Score')
    plt.title(f'Métriques par sujet — {mn} (Exp.{exp})')
    plt.legend(); plt.grid(alpha=0.3); plt.ylim([-0.05,1.05]); plt.tight_layout()
    plt.savefig(os.path.join(sd,'fold_metrics.png'),dpi=150); plt.close()

def plot_comparison(results, exps, mnames, outdir):
    exps_ok = [e for e in exps if e in results]
    if not exps_ok: return
    fig,axes=plt.subplots(1,3,figsize=(20,6))
    x=np.arange(len(exps_ok)); w=0.18
    for idx,(metric,title) in enumerate([('acc','Accuracy'),('f1_macro','F1-MACRO'),('auc','AUC')]):
        for i,mn in enumerate(mnames):
            vals=[results[e].get(mn,{}).get(metric,0) for e in exps_ok]
            axes[idx].bar(x+i*w,vals,w,label=mn,color=COLORS.get(mn,'#7F8C8D'),alpha=0.85)
        axes[idx].set_xticks(x+w*1.5); axes[idx].set_xticklabels(exps_ok)
        axes[idx].set_ylabel(title); axes[idx].set_title(title)
        axes[idx].legend(fontsize=7); axes[idx].grid(alpha=0.3); axes[idx].set_ylim([0,1.05])
    plt.suptitle('Comparaison des 4 classifieurs (LOSO)',fontsize=14)
    plt.tight_layout(rect=[0,0,1,0.95])
    plt.savefig(str(outdir/'comparison_all.png'),dpi=150); plt.close()


# ============================================================================
# MAIN
# ============================================================================
def main():
    print("="*70)
    print("NeuroCap — Baseline ML (SVM + RF + XGBoost + LightGBM)")
    print("Sortie : [P(Concentration)%, P(Stress)%]")
    print("Métriques : Accuracy, F1-binary, F1-MACRO, AUC")
    print("="*70)

    if not FEATURES_DIR.exists():
        print(f"\n❌ '{FEATURES_DIR}' introuvable → exécutez extract_features_for_baseline.py")
        return
    OUTPUT_DIR.mkdir(parents=True,exist_ok=True)
    MODEL_SAVE_ROOT.mkdir(parents=True,exist_ok=True)

    all_results = {}
    vt_results = {}

    for exp in EXPERIMENTS:
        ff=FEATURES_DIR/f'features_{exp}.npy'; lf=FEATURES_DIR/f'labels_{exp}.npy'
        sf=FEATURES_DIR/f'subject_ids_{exp}.npy'
        if not all(f.exists() for f in [ff,lf,sf]):
            print(f"\n⚠️ Exp.{exp}: fichiers manquants"); continue
        X=np.load(ff); y=np.load(lf); sids=np.load(sf)
        print(f"\n{'='*55}\nEXP {exp} | {len(X)} epochs | {X.shape[1]} features | "
              f"{np.sum(y==0)} conc. {np.sum(y==1)} stress | {len(np.unique(sids))} sujets\n{'='*55}")
        all_results[exp]={}

        for mn,model in MODELS.items():
            print(f"\n  ▶ {mn}")
            t0=time.time()
            yt,yp,yprob,fms,gm = loso_cv(X,y,sids,model)
            dt=time.time()-t0
            all_results[exp][mn]={
                'acc':gm['accuracy'],'f1':gm['f1'],'f1_macro':gm.get('f1_macro',0),
                'auc':gm.get('auc',0),'precision':gm['precision'],'recall':gm['recall'],
                'specificity':gm['specificity'],'pct_uncertain':gm.get('pct_uncertain',0),
            }
            print(f"    LOSO: Acc={gm['accuracy']:.4f} F1={gm['f1']:.4f} "
                  f"F1m={gm.get('f1_macro',0):.4f} AUC={gm.get('auc',0):.4f} "
                  f"Incert={gm.get('pct_uncertain',0):.1f}% [{dt:.1f}s]")

            od=OUTPUT_DIR/exp/mn.replace(' ','_'); od.mkdir(parents=True,exist_ok=True)
            if yt and len(np.unique(yt))>1:
                plot_cm(yt,yp,mn,exp,str(od))
                if yprob: plot_roc(yt,yprob,mn,exp,str(od)); plot_proba_dist(yt,yprob,mn,exp,str(od))
            plot_folds(fms,mn,exp,str(od))

            sc=StandardScaler(); Xsf=sc.fit_transform(X)
            mf=model.__class__(**model.get_params()); mf.fit(Xsf,y)
            vm=eval_split(mf,sc,'val',FEATURES_DIR); tm=eval_split(mf,sc,'test',FEATURES_DIR)
            vt_results[f"{exp}_{mn}"]={'val':vm,'test':tm}
            if vm: print(f"    VAL : Acc={vm['accuracy']:.4f} F1m={vm.get('f1_macro',0):.4f}")
            if tm: print(f"    TEST: Acc={tm['accuracy']:.4f} F1m={tm.get('f1_macro',0):.4f}")

    # Comparaison
    print(f"\n{'='*80}")
    print(f"{'Exp':>5}|{'Modèle':>15}|{'Acc':>7}|{'F1':>7}|{'F1m':>7}|{'AUC':>7}|{'Prec':>7}|{'Rec':>7}|{'Spéc':>7}|{'Inc%':>6}")
    print("-"*80)
    best_f1m=-1; best_cfg=None
    for exp in EXPERIMENTS:
        if exp not in all_results: continue
        for mn in MODELS:
            if mn not in all_results[exp]: continue
            m=all_results[exp][mn]
            print(f"{exp:>5}|{mn:>15}|{m['acc']:>7.4f}|{m['f1']:>7.4f}|{m['f1_macro']:>7.4f}|"
                  f"{m['auc']:>7.4f}|{m['precision']:>7.4f}|{m['recall']:>7.4f}|"
                  f"{m['specificity']:>7.4f}|{m.get('pct_uncertain',0):>5.1f}%")
            if m['f1_macro']>best_f1m: best_f1m=m['f1_macro']; best_cfg=(exp,mn)
    if best_cfg:
        print(f"\n★ Meilleur (F1-MACRO): {best_cfg[1]} sur Exp.{best_cfg[0]} (F1m={best_f1m:.4f})")

    plot_comparison(all_results, EXPERIMENTS, list(MODELS.keys()), OUTPUT_DIR)

    # Sauvegarde modèles
    if best_cfg:
        be=best_cfg[0]
        Xb=np.load(FEATURES_DIR/f'features_{be}.npy'); yb=np.load(FEATURES_DIR/f'labels_{be}.npy')
        print(f"\n{'='*55}\nSAUVEGARDE MODÈLES (Exp.{be})\n{'='*55}")
        for mn,model in MODELS.items():
            sc=StandardScaler(); Xs=sc.fit_transform(Xb)
            fm=model.__class__(**model.get_params()); fm.fit(Xs,yb)
            sn=mn.replace(' ','_')
            if mn in ['SVM','Random Forest','LightGBM']:
                mp=MODEL_SAVE_ROOT/f"{sn}_concentration_vs_stress.joblib"
                sp=MODEL_SAVE_ROOT/f"{sn}_scaler.joblib"
                joblib.dump(fm,mp); joblib.dump(sc,sp)
            elif mn=='XGBoost':
                mp=MODEL_SAVE_ROOT/f"{sn}_concentration_vs_stress.json"
                sp=MODEL_SAVE_ROOT/f"{sn}_scaler.joblib"
                fm.save_model(str(mp)); joblib.dump(sc,sp)
            print(f"  ✅ {mp.name} + {sp.name}")
            # Démo sortie probabiliste
            p=fm.predict_proba(Xs[:3])
            for i,pp in enumerate(p):
                st="Concentration" if pp[0]>=0.60 else ("Stress" if pp[1]>=0.60 else "INCERTAIN")
                print(f"     Ex{i}: P(C)={pp[0]:.1%} P(S)={pp[1]:.1%} → {st}")

    # Rapport
    with open(str(OUTPUT_DIR/'report_all.txt'),'w',encoding='utf-8') as f:
        f.write("="*70+"\nNeuroCap — Baseline ML — Rapport\n")
        f.write("Sortie: [P(Concentration)%, P(Stress)%]\n")
        f.write("Classifieurs: SVM, RF, XGBoost, LightGBM\n"+"="*70+"\n\n")
        for exp in EXPERIMENTS:
            if exp not in all_results: continue
            f.write(f"Exp {exp}:\n")
            for mn in MODELS:
                if mn not in all_results[exp]: continue
                m=all_results[exp][mn]
                f.write(f"  {mn:15s}: Acc={m['acc']:.4f} F1={m['f1']:.4f} "
                        f"F1m={m['f1_macro']:.4f} AUC={m['auc']:.4f}\n")
            f.write("\n")
        if best_cfg:
            f.write(f"\n★ Meilleur: {best_cfg[1]} Exp.{best_cfg[0]} (F1m={best_f1m:.4f})\n")

    jr={'loso':{},'best':None}
    for e in all_results:
        jr['loso'][e]={}
        for mn in all_results[e]: jr['loso'][e][mn]=all_results[e][mn]
    if best_cfg: jr['best']={'exp':best_cfg[0],'model':best_cfg[1],'f1_macro':best_f1m}
    with open(str(OUTPUT_DIR/'results.json'),'w') as f: json.dump(jr,f,indent=2,default=str)

    print(f"\n✅ Terminé | {OUTPUT_DIR}/ | {MODEL_SAVE_ROOT}/")

if __name__=="__main__": main()