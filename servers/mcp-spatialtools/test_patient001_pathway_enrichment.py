#!/usr/bin/env python3
"""Test pathway enrichment with Patient-001 differential expression results.

This script:
1. Reads Patient-001 spatial data
2. Identifies differentially expressed genes (tumor vs stroma)
3. Performs pathway enrichment on the DEGs
"""

import sys
from pathlib import Path
import pandas as pd
from scipy.stats import mannwhitneyu

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Import pathway enrichment test function
from test_pathway_enrichment_simple import perform_enrichment_test


def main():
    """Test pathway enrichment with Patient-001 data."""

    print("=" * 80)
    print("PATIENT-001 PATHWAY ENRICHMENT TEST")
    print("=" * 80)
    print()

    # Load Patient-001 spatial data
    data_dir = Path("/Users/lynnlangit/Documents/GitHub/spatial-mcp/data/patient-data/PAT001-OVC-2025/spatial")
    expression_file = data_dir / "visium_gene_expression.csv"
    annotations_file = data_dir / "visium_region_annotations.csv"

    print(f"Loading data from: {data_dir}")
    print()

    # Read files
    expression = pd.read_csv(expression_file, index_col=0)  # First column is barcode
    annotations = pd.read_csv(annotations_file)

    print(f"✅ Expression data: {expression.shape[0]} spots × {expression.shape[1]} genes")
    print(f"✅ Annotations: {annotations.shape[0]} spots")
    print()

    # Add barcode column to expression
    expression['barcode'] = expression.index

    # Merge expression with annotations
    data = expression.merge(annotations, on='barcode')

    # Get region counts
    region_counts = data['region'].value_counts()
    print("Region distribution:")
    for region, count in region_counts.items():
        print(f"  {region}: {count} spots")
    print()

    # Identify DEGs: tumor_core vs stroma
    print("Performing differential expression: tumor_core vs stroma")
    print("-" * 80)

    tumor_spots = data[data['region'] == 'tumor_core']
    stroma_spots = data[data['region'] == 'stroma']

    print(f"Tumor core: {len(tumor_spots)} spots")
    print(f"Stroma: {len(stroma_spots)} spots")
    print()

    # Get gene columns (exclude metadata)
    gene_cols = [col for col in expression.columns if col not in ['barcode', 'region']]

    # Perform Mann-Whitney U test for each gene
    degs = []
    for gene in gene_cols:
        tumor_expr = tumor_spots[gene].values
        stroma_expr = stroma_spots[gene].values

        # Skip if all zeros
        if tumor_expr.sum() == 0 and stroma_expr.sum() == 0:
            continue

        # Mann-Whitney U test
        try:
            stat, p_value = mannwhitneyu(tumor_expr, stroma_expr, alternative='two-sided')

            # Calculate fold change
            tumor_mean = tumor_expr.mean()
            stroma_mean = stroma_expr.mean()

            if stroma_mean > 0:
                fold_change = tumor_mean / stroma_mean
            else:
                fold_change = tumor_mean if tumor_mean > 0 else 1.0

            # Log2 fold change
            import math
            log2_fc = math.log2(fold_change) if fold_change > 0 else 0

            degs.append({
                'gene': gene,
                'tumor_mean': tumor_mean,
                'stroma_mean': stroma_mean,
                'fold_change': fold_change,
                'log2_fc': log2_fc,
                'p_value': p_value
            })
        except Exception as e:
            continue

    # Convert to DataFrame
    degs_df = pd.DataFrame(degs)

    # Apply FDR correction (Benjamini-Hochberg)
    degs_df = degs_df.sort_values('p_value')
    num_tests = len(degs_df)
    degs_df['rank'] = range(1, num_tests + 1)
    degs_df['p_adj'] = degs_df.apply(lambda row: min(1.0, row['p_value'] * num_tests / row['rank']), axis=1)

    # Filter significant DEGs (FDR < 0.05)
    sig_degs = degs_df[degs_df['p_adj'] < 0.05].copy()

    print(f"✅ Tested {len(degs_df)} genes")
    print(f"✅ Significant DEGs (FDR < 0.05): {len(sig_degs)}")
    print()

    # Separate upregulated and downregulated
    up_degs = sig_degs[sig_degs['log2_fc'] > 0].sort_values('p_adj')
    down_degs = sig_degs[sig_degs['log2_fc'] < 0].sort_values('p_adj')

    print(f"Upregulated in tumor (vs stroma): {len(up_degs)}")
    print(f"Downregulated in tumor (vs stroma): {len(down_degs)}")
    print()

    # Show top DEGs
    print("Top 10 upregulated genes in tumor_core:")
    for i, row in up_degs.head(10).iterrows():
        print(f"  {row['gene']}: log2FC={row['log2_fc']:.2f}, p_adj={row['p_adj']:.4f}")
    print()

    print("Top 10 downregulated genes in tumor_core:")
    for i, row in down_degs.head(10).iterrows():
        print(f"  {row['gene']}: log2FC={row['log2_fc']:.2f}, p_adj={row['p_adj']:.4f}")
    print()

    print("=" * 80)
    print()

    # Pathway enrichment on upregulated genes
    if len(up_degs) >= 3:
        print("PATHWAY ENRICHMENT: Upregulated Genes in Tumor Core")
        print("=" * 80)
        up_gene_list = up_degs['gene'].tolist()
        print(f"Analyzing {len(up_gene_list)} upregulated genes")
        print()

        # Test multiple databases
        for database in ["GO_BP", "Hallmark", "KEGG", "Drug_Resistance"]:
            print(f"\nDatabase: {database}")
            print("-" * 80)

            result = perform_enrichment_test(up_gene_list, database=database, p_value_cutoff=0.1)

            if result['pathways_enriched'] > 0:
                print(f"✅ Enriched pathways: {result['pathways_enriched']}")
                print(f"🎯 Top pathway: {result['pathways'][0]['pathway_name']}")
                print()

                for i, pathway in enumerate(result['pathways'][:3], 1):
                    print(f"{i}. {pathway['pathway_name']}")
                    print(f"   Overlap: {pathway['genes_overlapping']}/{pathway['genes_in_pathway']} genes")
                    print(f"   P-adj: {pathway['p_adj']:.6f}")
                    print(f"   Fold enrichment: {pathway['fold_enrichment']}x")
                    print(f"   Genes: {', '.join(pathway['overlapping_genes'][:10])}")
                    if len(pathway['overlapping_genes']) > 10:
                        print(f"          ... +{len(pathway['overlapping_genes']) - 10} more")
                    print()
            else:
                print("⚠️  No significant pathways found")

    print()
    print("=" * 80)
    print()

    # Pathway enrichment on downregulated genes
    if len(down_degs) >= 3:
        print("PATHWAY ENRICHMENT: Downregulated Genes in Tumor Core")
        print("=" * 80)
        down_gene_list = down_degs['gene'].tolist()
        print(f"Analyzing {len(down_gene_list)} downregulated genes")
        print()

        # Test GO_BP and Hallmark
        for database in ["GO_BP", "Hallmark"]:
            print(f"\nDatabase: {database}")
            print("-" * 80)

            result = perform_enrichment_test(down_gene_list, database=database, p_value_cutoff=0.1)

            if result['pathways_enriched'] > 0:
                print(f"✅ Enriched pathways: {result['pathways_enriched']}")
                print(f"🎯 Top pathway: {result['pathways'][0]['pathway_name']}")
                print()

                for i, pathway in enumerate(result['pathways'][:3], 1):
                    print(f"{i}. {pathway['pathway_name']}")
                    print(f"   Overlap: {pathway['genes_overlapping']}/{pathway['genes_in_pathway']} genes")
                    print(f"   P-adj: {pathway['p_adj']:.6f}")
                    print(f"   Genes: {', '.join(pathway['overlapping_genes'])}")
                    print()
            else:
                print("⚠️  No significant pathways found")

    print()
    print("=" * 80)
    print("✅ Patient-001 pathway enrichment test completed!")
    print("=" * 80)
    print()


if __name__ == "__main__":
    main()
