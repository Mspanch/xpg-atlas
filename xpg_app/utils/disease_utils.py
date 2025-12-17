import pandas as pd
import os
import numpy as np

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'data')

# --- Load datasets once globally ---
schema_df = pd.read_csv(os.path.join(DATA_DIR, 'SCHEMA_gene_results.tsv'), sep='\t')
epi25_df = pd.read_csv(os.path.join(DATA_DIR, 'Epi25_gene_results.tsv'), sep='\t')
sfari_df = pd.read_csv(os.path.join(DATA_DIR, 'sfari_genes.csv'))
bipex_df = pd.read_csv(os.path.join(DATA_DIR, 'BipEx_gene_results.tsv'), sep='\t')
bipex_df = bipex_df[bipex_df["group"] == "Bipolar Disorder"]  # only main disorder


# ---------------- SFARI ----------------
def get_sfari_info(gene_symbol):
    df = sfari_df[sfari_df['gene-symbol'].str.upper() == gene_symbol.upper()]
    if df.empty:
        return None
    row = df.iloc[0]
    return {
        "score": row.get('gene-score', 'NA'),
        "category": row.get('genetic-category', 'NA'),
        "syndromic": bool(row.get('syndromic', 0))
    }


# ---------------- SCHEMA ----------------
def get_schema_info(identifier):
    df = schema_df[
        (schema_df['gene_id'].astype(str) == identifier) |
        (schema_df['gene_id'].astype(str).str.upper() == identifier.upper())
    ]
    if df.empty:
        return None
    row = df.iloc[0]
    return {
        "or_ptv": row.get('OR (PTV)', 'NA'),
        "p_meta": row.get('P meta', 'NA'),
        "q_meta": row.get('Q meta', 'NA')
    }


# ---------------- Epi25 ----------------
def get_epi25_info(identifier):
    df = epi25_df[
        (epi25_df['gene_id'].astype(str) == identifier) |
        (epi25_df['gene_id'].astype(str).str.upper() == identifier.upper())
    ]
    if df.empty:
        return None

    group_stats = []
    any_sig = False
    for _, r in df.iterrows():
        pval = r.get("ptv_pval", np.nan)
        or_val = r.get("ptv_OR", np.nan)
        if not pd.isna(pval):
            group_stats.append({
                "group": r["group"],
                "pval": float(pval),
                "odds_ratio": float(or_val) if not pd.isna(or_val) else None
            })
            if pval < 0.05:
                any_sig = True
    return {"group_stats": group_stats, "any_significant": any_sig}


# ---------------- BipEx (Bipolar Disorder) ----------------
def get_bipex_info(identifier):
    """Fetchs BipEx bipolar disorder gene stats."""
    df = bipex_df[
        (bipex_df['gene_id'].astype(str) == identifier) |
        (bipex_df['gene_id'].astype(str).str.upper() == identifier.upper())
    ]
    if df.empty:
        return None

    row = df.iloc[0]
    mis_pval = row.get('damaging_missense_fisher_gnom_non_psych_pval', np.nan)
    ptv_pval = row.get('ptv_fisher_gnom_non_psych_pval', np.nan)
    mis_or = row.get('damaging_missense_fisher_gnom_non_psych_OR', np.nan)
    ptv_or = row.get('ptv_fisher_gnom_non_psych_OR', np.nan)


    return {
        "mis_pval": float(mis_pval),
        "mis_odds_ratio": float(mis_or) if not np.isinf(mis_or) else "Infinity",
        "ptv_pval": float(ptv_pval),
        "ptv_odds_ratio": float(ptv_or) if not np.isinf(ptv_or) else "Infinity",
    }
