#!/usr/bin/env python3

"""
Annotate XPG TSV with disease significance calls (SFARI, SCHEMA, BipEx, Epi25).
Writes a new TSV: XPGs_with_disease_annotations.tsv
"""

import os
import django
import pandas as pd
import math

# ----------------------------------------------------------
# 1. Setup Django so we can import your disease_utils
# ----------------------------------------------------------
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xpg_portal.settings")
django.setup()

from xpg_app.utils.disease_utils import (
    get_sfari_info,
    get_schema_info,
    get_bipex_info,
    get_epi25_info,
)


# ----------------------------------------------------------
# 2. INPUT / OUTPUT FILE PATHS
# ----------------------------------------------------------
INPUT_TSV = "/Users/Muthu/Downloads/Gene_Annotation/XPGs_with_PV_enrichment.tsv"
OUTPUT_TSV = "/Users/Muthu/Downloads/Gene_Annotation/XPGs_with_disease_annotations.tsv"

print("📂 Loading XPG table...")
df = pd.read_csv(INPUT_TSV, sep="\t")

# ----------------------------------------------------------
# 2B. REMOVE DUPLICATES BEFORE PROCESSING
# ----------------------------------------------------------
print("🧹 Removing duplicate genes...")

# Sort so highest pv_enrichment is kept (safest biologically)
if "pv_enrichment" in df.columns:
    df = df.sort_values("pv_enrichment", ascending=False)

# Drop duplicates based on the *gene* symbol
df = df.drop_duplicates(subset=["gene"], keep="first")

print(f"➡️ After deduplication: {len(df)} rows remain")


# ----------------------------------------------------------
# 3. Helper functions
# ----------------------------------------------------------
def clean_id(value):
    """Convert NaN/None to '', otherwise return uppercase string."""
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return ""
    return str(value).strip()


def is_sig(val):
    """Return True if numeric value < 0.05."""
    return isinstance(val, (float, int)) and val < 0.05


# ----------------------------------------------------------
# 4. Annotate each gene with disease significance
# ----------------------------------------------------------
sfari_sig_list = []
schema_sig_list = []
bipex_sig_list = []
epi25_sig_list = []

print("🔍 Running disease annotation for each gene...")

for idx, row in df.iterrows():
    gene = clean_id(row.get("gene"))
    human_ens = clean_id(row.get("Human_ENSEMBL"))

    # ⭐ SFARI
    sf = get_sfari_info(gene)
    sfari_sig = False
    if sf:
        score = sf.get("score", None)
        sfari_sig = (score == 1)
    sfari_sig_list.append(sfari_sig)

    # ⭐ SCHEMA
    sc = get_schema_info(human_ens)
    schema_sig = False
    if sc and sc.get("q_meta") not in [None, "NA"]:
        try:
            schema_sig = is_sig(float(sc["q_meta"]))
        except:
            schema_sig = False
    schema_sig_list.append(schema_sig)

    # ⭐ BipEx
    bx = get_bipex_info(human_ens)
    bipex_sig = False
    if bx:
        mis_sig = is_sig(bx.get("mis_pval"))
        ptv_sig = is_sig(bx.get("ptv_pval"))
        bipex_sig = (mis_sig or ptv_sig)
    bipex_sig_list.append(bipex_sig)

    # ⭐ Epi25
    ep = get_epi25_info(human_ens)
    epi25_sig = False
    if ep and "group_stats" in ep:
        for g in ep["group_stats"]:
            if is_sig(g.get("pval")):
                epi25_sig = True
                break
    epi25_sig_list.append(epi25_sig)


# ----------------------------------------------------------
# 5. Add columns
# ----------------------------------------------------------
df["SFARI_significant"] = sfari_sig_list
df["SCHEMA_significant"] = schema_sig_list
df["BipEx_significant"] = bipex_sig_list
df["Epi25_significant"] = epi25_sig_list

df["Disease_hit_count"] = (
    df["SFARI_significant"].astype(int)
    + df["SCHEMA_significant"].astype(int)
    + df["BipEx_significant"].astype(int)
    + df["Epi25_significant"].astype(int)
)

print("💾 Saving annotated TSV...")
df.to_csv(OUTPUT_TSV, sep="\t", index=False)

print(f"✅ DONE! Annotated TSV saved to:\n{OUTPUT_TSV}")
