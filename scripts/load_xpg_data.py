import pandas as pd
from xpg_app.models import Gene

# ⬅️ Use your NEW annotated TSV
FILE_PATH = "/Users/Muthu/Downloads/Gene_Annotation/XPGs_with_disease_annotations.tsv"

# Load TSV
df = pd.read_csv(FILE_PATH, sep="\t")

# 🔥 Normalize column names (strip whitespace, remove BOM)
df.columns = df.columns.str.strip()
df.columns = df.columns.str.replace('\ufeff', '', regex=True)

# 🔍 Show available columns for debugging
print("COLUMNS:", df.columns)

# Fix gene description column name if needed
if "Gene description" in df.columns:
    df.rename(columns={"Gene description": "gene_description"}, inplace=True)

if "gene description" in df.columns:
    df.rename(columns={"gene description": "gene_description"}, inplace=True)

print("Final columns:", df.columns)

# 🚨 Wipe old gene table (optional but recommended if schema changed)
# from xpg_app.models import Gene
Gene.objects.all().delete()

# Insert into DB
for _, row in df.iterrows():
    Gene.objects.create(
        gene=row.get("gene", ""),
        log2FC=row.get("log2FC", None),
        adjP=row.get("adjP", None),
        ENSEMBL=row.get("ENSEMBL", ""),
        gene_description=row.get("gene_description", ""),
        ENTREZID=row.get("ENTREZID", ""),
        Human_ENSEMBL=row.get("Human_ENSEMBL", ""),
        Mouse_GO_ID=row.get("Mouse_GO_ID", ""),
        pathways=row.get("pathways", ""),
        tract_SM=row.get("tract_SM", ""),
        tract_AB=row.get("tract_AB", ""),
        tract_PR=row.get("tract_PR", ""),
        tract_OC=row.get("tract_OC", ""),
        Drugs_SM=row.get("Drugs_SM", ""),
        Drugs_AB=row.get("Drugs_AB", ""),
        Drugs_PR=row.get("Drugs_PR", ""),
        Drugs_OC=row.get("Drugs_OC", ""),
        Drugs_Enzyme=row.get("Drugs_Enzyme", ""),
        Drugs_Unknown=row.get("Drugs_Unknown", ""),
        Drugs_Antibody_drug_conjugate=row.get("Drugs_Antibody drug conjugate", ""),
        pv_mean=row.get("pv_mean", None),
        nonpv_mean=row.get("nonpv_mean", None),
        pv_enrichment=row.get("pv_enrichment", None),

        # ⭐ NEW disease-significance fields:
        SFARI_significant=row.get("SFARI_significant", False),
        SCHEMA_significant=row.get("SCHEMA_significant", False),
        BipEx_significant=row.get("BipEx_significant", False),
        Epi25_significant=row.get("Epi25_significant", False),
        Disease_hit_count=row.get("Disease_hit_count", 0),
    )

print("🔥 Loaded annotated XPG data with disease significance!")
