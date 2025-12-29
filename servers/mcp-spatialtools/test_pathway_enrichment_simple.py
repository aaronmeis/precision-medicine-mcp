#!/usr/bin/env python3
"""Simple test for pathway enrichment Fisher's exact test logic.

Tests the enrichment calculation directly without FastMCP.
"""

import sys
from pathlib import Path
from scipy.stats import fisher_exact

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Import pathway database
from mcp_spatialtools.server import OVARIAN_CANCER_PATHWAYS


def perform_enrichment_test(gene_list, database="GO_BP", p_value_cutoff=0.05):
    """Test pathway enrichment calculation."""

    # Normalize gene lists (case-insensitive)
    gene_list_upper = [gene.upper() for gene in gene_list]

    # Default background: all genes in the pathway database
    all_pathway_genes = set()
    if database in OVARIAN_CANCER_PATHWAYS:
        for pathway_info in OVARIAN_CANCER_PATHWAYS[database].values():
            all_pathway_genes.update([g.upper() for g in pathway_info["genes"]])
    background_genes_upper = list(all_pathway_genes)

    # Get pathways for selected database
    if database not in OVARIAN_CANCER_PATHWAYS:
        print(f"❌ Unknown database: {database}")
        return

    pathways_db = OVARIAN_CANCER_PATHWAYS[database]

    # Perform enrichment for each pathway
    enrichment_results = []

    for pathway_id, pathway_info in pathways_db.items():
        pathway_genes_upper = [g.upper() for g in pathway_info["genes"]]

        # 2x2 contingency table for Fisher's exact test
        genes_in_list_and_pathway = set(gene_list_upper) & set(pathway_genes_upper)
        genes_in_list_not_pathway = set(gene_list_upper) - set(pathway_genes_upper)
        genes_in_pathway_not_list = set(pathway_genes_upper) - set(gene_list_upper)
        genes_not_in_either = set(background_genes_upper) - set(gene_list_upper) - set(pathway_genes_upper)

        a = len(genes_in_list_and_pathway)
        b = len(genes_in_pathway_not_list)
        c = len(genes_in_list_not_pathway)
        d = len(genes_not_in_either)

        # Skip if no overlap
        if a == 0:
            continue

        # Fisher's exact test (one-sided for enrichment)
        contingency_table = [[a, b], [c, d]]
        try:
            _, p_value = fisher_exact(contingency_table, alternative='greater')
        except Exception as e:
            print(f"⚠️  Fisher's exact test failed for {pathway_id}: {e}")
            continue

        # Calculate fold enrichment
        if a + c > 0 and b + d > 0:
            fold_enrichment = (a / (a + c)) / ((a + b) / (a + b + c + d))
        else:
            fold_enrichment = 0.0

        # Store result
        enrichment_results.append({
            "pathway_id": pathway_id,
            "pathway_name": pathway_info["name"],
            "genes_in_pathway": len(pathway_genes_upper),
            "genes_overlapping": a,
            "overlapping_genes": sorted(list(genes_in_list_and_pathway)),
            "p_value": float(p_value),
            "fold_enrichment": round(float(fold_enrichment), 2)
        })

    # Sort by p-value
    enrichment_results.sort(key=lambda x: x["p_value"])

    # Apply Benjamini-Hochberg FDR correction
    num_tests = len(enrichment_results)
    for i, result in enumerate(enrichment_results):
        rank = i + 1
        # BH correction: p_adj = p_value * num_tests / rank
        p_adj = min(1.0, result["p_value"] * num_tests / rank)
        result["p_adj"] = round(float(p_adj), 6)

    # Filter by significance
    significant_pathways = [p for p in enrichment_results if p["p_adj"] < p_value_cutoff]

    # Return results
    return {
        "database": database,
        "genes_analyzed": len(gene_list_upper),
        "background_size": len(background_genes_upper),
        "pathways_tested": len(pathways_db),
        "pathways_enriched": len(significant_pathways),
        "p_value_cutoff": p_value_cutoff,
        "pathways": significant_pathways[:20],
        "mode": "test"
    }


def main():
    """Run enrichment tests."""

    print("=" * 80)
    print("PATHWAY ENRICHMENT TEST - Direct Fisher's Exact Test")
    print("=" * 80)
    print()

    # Test 1: DNA repair genes
    print("Test 1: DNA Repair Genes")
    print("-" * 80)
    dna_repair_genes = [
        "BRCA1", "BRCA2", "TP53", "ATM", "ATR", "RAD51", "XRCC1", "ERCC1", "MSH2", "MLH1"
    ]
    print(f"Genes: {', '.join(dna_repair_genes)}")
    print()

    result1 = perform_enrichment_test(dna_repair_genes, database="GO_BP", p_value_cutoff=0.05)

    print(f"✅ Database: {result1['database']}")
    print(f"✅ Genes analyzed: {result1['genes_analyzed']}")
    print(f"✅ Background size: {result1['background_size']}")
    print(f"✅ Pathways tested: {result1['pathways_tested']}")
    print(f"✅ Pathways enriched: {result1['pathways_enriched']}")
    print()

    if result1['pathways_enriched'] > 0:
        print(f"🎯 Top pathway: {result1['pathways'][0]['pathway_name']}")
        print()
        print("Top 5 enriched pathways:")
        for i, pathway in enumerate(result1['pathways'][:5], 1):
            print(f"\n{i}. {pathway['pathway_name']} ({pathway['pathway_id']})")
            print(f"   Overlap: {pathway['genes_overlapping']}/{pathway['genes_in_pathway']} genes")
            print(f"   P-value: {pathway['p_value']:.2e}")
            print(f"   P-adj (FDR): {pathway['p_adj']:.6f}")
            print(f"   Fold enrichment: {pathway['fold_enrichment']}x")
            print(f"   Genes: {', '.join(pathway['overlapping_genes'][:8])}")
            if len(pathway['overlapping_genes']) > 8:
                print(f"          ... +{len(pathway['overlapping_genes']) - 8} more")
    else:
        print("⚠️  No significant pathways found")

    print()
    print("=" * 80)
    print()

    # Test 2: Cell cycle genes with Hallmark database
    print("Test 2: Cell Cycle Genes (Hallmark Database)")
    print("-" * 80)
    cell_cycle_genes = [
        "CCND1", "CCNE1", "CDK4", "CDK6", "MYC", "E2F1", "PCNA", "MKI67", "TOP2A", "AURKA"
    ]
    print(f"Genes: {', '.join(cell_cycle_genes)}")
    print()

    result2 = perform_enrichment_test(cell_cycle_genes, database="Hallmark", p_value_cutoff=0.05)

    print(f"✅ Pathways enriched: {result2['pathways_enriched']}")
    print()

    if result2['pathways_enriched'] > 0:
        print(f"🎯 Top pathway: {result2['pathways'][0]['pathway_name']}")
        print()
        for i, pathway in enumerate(result2['pathways'][:3], 1):
            print(f"{i}. {pathway['pathway_name']}")
            print(f"   P-adj: {pathway['p_adj']:.6f}, Enrichment: {pathway['fold_enrichment']}x")
            print(f"   Genes: {', '.join(pathway['overlapping_genes'])}")
            print()
    else:
        print("⚠️  No significant pathways found")

    print("=" * 80)
    print()

    # Test 3: Platinum resistance (Patient-001 relevant)
    print("Test 3: Platinum Resistance Genes (Drug_Resistance Database)")
    print("-" * 80)
    resistance_genes = [
        "PIK3CA", "AKT1", "PTEN", "ABCB1", "BCL2L1", "ERCC1", "GSTP1", "BRCA1"
    ]
    print(f"Genes: {', '.join(resistance_genes)}")
    print()

    result3 = perform_enrichment_test(resistance_genes, database="Drug_Resistance", p_value_cutoff=0.1)

    print(f"✅ Pathways enriched: {result3['pathways_enriched']}")
    print()

    if result3['pathways_enriched'] > 0:
        print(f"🎯 Top pathway: {result3['pathways'][0]['pathway_name']}")
        print()
        for i, pathway in enumerate(result3['pathways'], 1):
            print(f"{i}. {pathway['pathway_name']}")
            print(f"   Overlap: {pathway['genes_overlapping']}/{pathway['genes_in_pathway']} genes")
            print(f"   P-adj: {pathway['p_adj']:.6f}")
            print(f"   Fold enrichment: {pathway['fold_enrichment']}x")
            print(f"   Genes: {', '.join(pathway['overlapping_genes'])}")
            print()
    else:
        print("⚠️  No significant pathways found")

    print("=" * 80)
    print()

    # Test 4: KEGG PI3K/AKT pathway
    print("Test 4: PI3K/AKT Pathway Genes (KEGG Database)")
    print("-" * 80)
    pi3k_genes = ["PIK3CA", "AKT1", "AKT2", "MTOR", "PTEN", "RPS6KB1", "TSC1", "TSC2", "FOXO3"]
    print(f"Genes: {', '.join(pi3k_genes)}")
    print()

    result4 = perform_enrichment_test(pi3k_genes, database="KEGG", p_value_cutoff=0.05)

    print(f"✅ Pathways enriched: {result4['pathways_enriched']}")
    print()

    if result4['pathways_enriched'] > 0:
        print(f"🎯 Top pathway: {result4['pathways'][0]['pathway_name']}")
        print()
        for i, pathway in enumerate(result4['pathways'][:3], 1):
            print(f"{i}. {pathway['pathway_name']} ({pathway['pathway_id']})")
            print(f"   P-adj: {pathway['p_adj']:.6f}")
            print(f"   Genes: {', '.join(pathway['overlapping_genes'])}")
            print()
    else:
        print("⚠️  No significant pathways found")

    print("=" * 80)
    print()
    print("✅ All pathway enrichment tests completed successfully!")
    print()


if __name__ == "__main__":
    main()
