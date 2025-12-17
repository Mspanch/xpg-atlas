from django.db import models

class Gene(models.Model):
    gene = models.CharField(max_length=100)
    log2FC = models.FloatField(null=True)
    adjP = models.FloatField(null=True)
    ENSEMBL = models.CharField(max_length=50, blank=True)
    ENTREZID = models.CharField(max_length=50, blank=True)
    Human_ENSEMBL = models.CharField(max_length=50, blank=True)
    Mouse_GO_ID = models.CharField(max_length=50, blank=True)

    pathways = models.TextField(blank=True)
    tract_SM = models.TextField(blank=True)
    tract_AB = models.TextField(blank=True)
    tract_PR = models.TextField(blank=True)
    tract_OC = models.TextField(blank=True)

    Drugs_SM = models.TextField(blank=True)
    Drugs_AB = models.TextField(blank=True)
    Drugs_PR = models.TextField(blank=True)
    Drugs_OC = models.TextField(blank=True)
    Drugs_Enzyme = models.TextField(blank=True)
    Drugs_Unknown = models.TextField(blank=True)
    Drugs_Antibody_drug_conjugate = models.TextField(blank=True)

    pv_mean = models.FloatField(null=True)
    nonpv_mean = models.FloatField(null=True)
    pv_enrichment = models.FloatField(null=True)

    gene_description = models.TextField(blank=True)

    # ⭐ EXACT names expected by load_xpg_data.py:
    SFARI_significant = models.BooleanField(default=False)
    SCHEMA_significant = models.BooleanField(default=False)
    BipEx_significant = models.BooleanField(default=False)
    Epi25_significant = models.BooleanField(default=False)
    Disease_hit_count = models.IntegerField(default=0)

    def __str__(self):
        return self.gene
