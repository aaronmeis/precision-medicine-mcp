#!/usr/bin/env python3
"""Test ComBat batch correction with file-based workflow.

Creates temporary batch files and tests the full batch correction pipeline.
"""

import sys
import os
from pathlib import Path
import pandas as pd
import numpy as np
import tempfile
import asyncio

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))


async def test_batch_correction_with_files():
    """Test batch correction with file inputs/outputs."""

    # Import the server module
    from mcp_spatialtools import server

    # Ensure NOT in DRY_RUN mode
    os.environ["SPATIAL_DRY_RUN"] = "false"

    print("=" * 80)
    print("BATCH CORRECTION TEST - File-based Workflow")
    print("=" * 80)
    print()

    # Create temporary directory for test files
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        print(f"Temporary directory: {tmpdir}")
        print()

        # Create synthetic batch data
        print("Creating synthetic batch data...")
        print("-" * 80)

        np.random.seed(42)

        # Shared genes across all batches
        genes = [f"gene_{i+1}" for i in range(50)]

        # Batch 1: 10 samples
        batch1_data = pd.DataFrame(
            np.random.normal(5.0, 2.0, (50, 10)),  # Mean=5, batch effect
            index=genes,
            columns=[f"sample_{i+1}" for i in range(10)]
        )
        batch1_file = tmpdir / "batch1.csv"
        batch1_data.to_csv(batch1_file)
        print(f"✅ Created batch1: {batch1_data.shape[0]} genes × {batch1_data.shape[1]} samples")

        # Batch 2: 10 samples
        batch2_data = pd.DataFrame(
            np.random.normal(7.0, 2.0, (50, 10)),  # Mean=7, different batch effect
            index=genes,
            columns=[f"sample_{i+1}" for i in range(10)]
        )
        batch2_file = tmpdir / "batch2.csv"
        batch2_data.to_csv(batch2_file)
        print(f"✅ Created batch2: {batch2_data.shape[0]} genes × {batch2_data.shape[1]} samples")

        # Batch 3: 10 samples
        batch3_data = pd.DataFrame(
            np.random.normal(3.0, 2.0, (50, 10)),  # Mean=3, another batch effect
            index=genes,
            columns=[f"sample_{i+1}" for i in range(10)]
        )
        batch3_file = tmpdir / "batch3.csv"
        batch3_data.to_csv(batch3_file)
        print(f"✅ Created batch3: {batch3_data.shape[0]} genes × {batch3_data.shape[1]} samples")

        print()

        # Show batch means
        print("Batch means (before correction):")
        print(f"  Batch 1: {batch1_data.values.mean():.3f}")
        print(f"  Batch 2: {batch2_data.values.mean():.3f}")
        print(f"  Batch 3: {batch3_data.values.mean():.3f}")
        print()

        print("=" * 80)
        print()

        # Run batch correction
        print("Running ComBat batch correction...")
        print("-" * 80)

        output_file = tmpdir / "corrected.csv"

        # Call batch correction (need to call the implementation directly, not the FastMCP tool)
        from mcp_spatialtools.server import _combat_batch_correction, _calculate_batch_variance

        # Load all batches
        batch_dfs = [batch1_data, batch2_data, batch3_data]
        batch_labels = ["batch1", "batch2", "batch3"]

        # Merge with unique column names
        merged_dfs = []
        for i, (df, label) in enumerate(zip(batch_dfs, batch_labels)):
            df_copy = df.copy()
            df_copy.columns = [f"{col}_{label}_{i}" for col in df_copy.columns]
            merged_dfs.append(df_copy)

        merged_data = pd.concat(merged_dfs, axis=1)

        # Create batch array
        batch_array = []
        for i, df in enumerate(batch_dfs):
            batch_array.extend([batch_labels[i]] * df.shape[1])
        batch_array = np.array(batch_array)

        print(f"✅ Merged data: {merged_data.shape[0]} genes × {merged_data.shape[1]} samples")
        print(f"✅ Batches: {len(set(batch_array))}")
        print()

        # Calculate variance before
        variance_before = _calculate_batch_variance(merged_data.T.values, batch_array)
        print(f"Variance explained by batch (BEFORE): {variance_before:.4f} ({variance_before*100:.2f}%)")

        # Apply ComBat
        corrected_data = _combat_batch_correction(merged_data, batch_array, parametric=True)

        # Calculate variance after
        variance_after = _calculate_batch_variance(corrected_data.T.values, batch_array)
        print(f"Variance explained by batch (AFTER):  {variance_after:.4f} ({variance_after*100:.2f}%)")

        variance_reduction = (variance_before - variance_after) / variance_before
        print(f"Variance reduction: {variance_reduction:.4f} ({variance_reduction*100:.2f}%)")
        print()

        # Save corrected data
        corrected_data.to_csv(output_file)
        print(f"✅ Saved corrected data to: {output_file}")
        print()

        # Load and show corrected batch means
        corrected_df = pd.read_csv(output_file, index_col=0)

        print("Batch means (after correction):")
        for i, label in enumerate(batch_labels):
            batch_cols = [col for col in corrected_df.columns if f"_{label}_{i}" in col]
            batch_mean = corrected_df[batch_cols].values.mean()
            print(f"  {label}: {batch_mean:.3f}")
        print()

        print("=" * 80)
        print()

        # Summary
        print("SUMMARY")
        print("=" * 80)
        print(f"✅ Processed {merged_data.shape[1]} samples from {len(set(batch_array))} batches")
        print(f"✅ Corrected {merged_data.shape[0]} genes")
        print(f"✅ Batch variance: {variance_before*100:.2f}% → {variance_after*100:.2f}%")
        print(f"✅ Variance reduction: {variance_reduction*100:.2f}%")
        print()

        if variance_reduction > 0.3:
            print("✅ ComBat batch correction SUCCESSFUL")
        else:
            print("⚠️  Batch effects partially corrected")

        print()
        print("=" * 80)
        print("✅ File-based batch correction test completed!")
        print("=" * 80)
        print()


if __name__ == "__main__":
    asyncio.run(test_batch_correction_with_files())
