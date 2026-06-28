"""
BM25 léger — recherche lexicale par mots-clés sans index inversé.
Basé sur : Karpukhin et al., 2020 (cité dans Ng et al., NEJM AI 2025, ref 42).

Formule :
    score(q, d) = Σ_w  IDF(w) × TF(w,d) × (k1+1)
                        ─────────────────────────────
                        TF(w,d) + k1×(1 - b + b×|d|/avgdl)

Simplification : IDF=1.0 (corpus trop petit pour l'estimer).
"""


def bm25_score(query: str, text: str) -> float:
    """
    Score BM25 normalisé [0, 1] entre une requête et un texte.

    Paramètres :
        k1    = 1.5  (saturation fréquence)
        b     = 0.75 (normalisation longueur document)
        avgdl = 150  (longueur moyenne estimée des docs KB)
    """
    words   = query.lower().split()
    text_lc = text.lower()
    k1, b   = 1.5, 0.75
    avgdl   = 150.0
    dl      = len(text_lc.split())
    score   = 0.0

    for w in words:
        tf    = text_lc.count(w)
        idf   = 1.0
        score += idf * (tf * (k1 + 1)) / (tf + k1 * (1 - b + b * dl / avgdl))

    return min(score / max(len(words), 1), 1.0)
