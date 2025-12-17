from django.shortcuts import render
from django.db.models import Q
from django.http import HttpResponse, JsonResponse, Http404
import csv

from .models import Gene
from .utils.disease_utils import (
    get_sfari_info, get_schema_info, get_epi25_info, get_bipex_info
)

# ======================
# HOME
# ======================

def home(request):
    return render(request, 'xpg_app/home.html')


# ======================
# GENE DETAIL PAGE
# ======================

def gene_detail(request, gene_name):
    genes = Gene.objects.filter(gene=gene_name)
    if not genes.exists():
        raise Http404("Gene not found")

    gene = genes.first()

    context = {
        "gene": gene,
        "all_genes": genes,
        "count": genes.count(),

        # Live disease info still shown on detail page
        "sfari_info": get_sfari_info(gene_name),
        "schema_info": get_schema_info(gene.Human_ENSEMBL),
        "epi25_info": get_epi25_info(gene.Human_ENSEMBL),
        "bipex_info": get_bipex_info(gene.Human_ENSEMBL),
    }

    return render(request, "xpg_app/gene_detail.html", context)


# ======================
# SEARCH PAGE
# ======================

def search(request):
    query = request.GET.get('q', '')
    results = []

    if query:
        results = (
            Gene.objects.filter(
                Q(gene__icontains=query) |
                Q(ENSEMBL__icontains=query) |
                Q(Human_ENSEMBL__icontains=query)
            ).distinct()
        )

    # CSV export
    if request.GET.get('download') == 'csv' and results:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="xpg_search_{query}.csv"'
        writer = csv.writer(response)
        writer.writerow(['Gene', 'log2FC', 'adjP', 'ENSEMBL', 'Human_ENSEMBL', 'Description'])

        for g in results:
            writer.writerow([
                g.gene, g.log2FC, g.adjP, g.ENSEMBL, g.Human_ENSEMBL, g.gene_description
            ])

        return response

    return render(request, 'xpg_app/search.html', {
        'query': query,
        'results': results
    })


# ======================
# AUTOCOMPLETE
# ======================

def autocomplete(request):
    query = request.GET.get('term', '')
    results = []

    if query:
        genes = Gene.objects.filter(gene__icontains=query).values_list('gene', flat=True)[:10]
        results = list(genes)

    return JsonResponse(results, safe=False)


# ============================================================
# 🚀 DISEASE OVERVIEW (FAST MODE — USES ONLY DATABASE FIELDS)
# ============================================================

def disease_overview(request):
    # Pull all genes with precomputed significance
    genes = Gene.objects.all()

    rows = []
    for g in genes:
        rows.append({
            "gene": g.gene,
            "description": g.gene_description,

            # Already computed in DB:
            "sfari_sig": int(g.SFARI_significant),
            "schema_sig": int(g.SCHEMA_significant),
            "bipex_sig": int(g.BipEx_significant),
            "epi25_sig": int(g.Epi25_significant),

            "multi_sig_count": g.Disease_hit_count,
        })

    # Rank genes by total significance hits
    rows.sort(key=lambda x: x["multi_sig_count"], reverse=True)

    # ===============================
    # ADD SUMMARY COUNTS FOR TEMPLATE
    # ===============================
    sfari_count = Gene.objects.filter(SFARI_significant=True).count()
    schema_count = Gene.objects.filter(SCHEMA_significant=True).count()
    bipex_count = Gene.objects.filter(BipEx_significant=True).count()
    epi25_count = Gene.objects.filter(Epi25_significant=True).count()
    multi_hit_count = Gene.objects.filter(Disease_hit_count__gte=2).count()

    return render(request, "xpg_app/disease_overview.html", {
        "rows": rows,
        "sfari_count": sfari_count,
        "schema_count": schema_count,
        "bipex_count": bipex_count,
        "epi25_count": epi25_count,
        "multi_hit_count": multi_hit_count,
    })
