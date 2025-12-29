#!/usr/bin/env python3
"""Test script for ComBat batch correction implementation.

This script creates synthetic multi-batch data with artificial batch effects
and tests the ComBat batch correction algorithm.
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Import the batch correction functions
from mcp_spatialtools.server import _combat_batch_correction, _calculate_batch_variance


def create_synthetic_batch_data(
    n_genes=100,
    n_samples_per_batch=20,
    n_batches=3,
    batch_effect_size=2.0,
    biological_signal_size=3.0
):
    """Create synthetic gene expression data with batch effects.

    Args:
        n_genes: Number of genes
        n_samples_per_batch: Samples per batch
        n_batches: Number of batches
        batch_effect_size: Magnitude of batch effects
        biological_signal_size: Magnitude of biological signal

    Returns:
        Tuple of (data, batch_labels, true_biological_signal)
    """
    np.random.seed(42)

    # Create biological signal (simulated true expression)
    # Half of samples have high expression, half have low
    n_total_samples = n_samples_per_batch * n_batches
    biological_groups = np.array([0] * (n_total_samples // 2) + [1] * (n_total_samples // 2))
    np.random.shuffle(biological_groups)

    # Generate true biological signal
    true_signal = np.zeros((n_genes, n_total_samples))
    for i in range(n_total_samples):
        if biological_groups[i] == 1:
            # High expression group
            true_signal[:, i] = np.random.normal(biological_signal_size, 1.0, n_genes)
        else:
            # Low expression group
            true_signal[:, i] = np.random.normal(0, 1.0, n_genes)

    # Add batch effects
    data_with_batch = true_signal.copy()
    batch_labels = []

    for batch_idx in range(n_batches):
        start_idx = batch_idx * n_samples_per_batch
        end_idx = start_idx + n_samples_per_batch

        # Add batch-specific shift (location effect)
        batch_shift = np.random.normal(0, batch_effect_size, n_genes)

        # Add batch-specific scale effect
        batch_scale = np.random.uniform(0.5, 1.5, n_genes)

        # Apply batch effects
        data_with_batch[:, start_idx:end_idx] += batch_shift[:, np.newaxis]
        data_with_batch[:, start_idx:end_idx] *= batch_scale[:, np.newaxis]

        # Record batch labels
        batch_labels.extend([f"batch{batch_idx+1}"] * n_samples_per_batch)

    batch_labels = np.array(batch_labels)

    return data_with_batch, batch_labels, true_signal, biological_groups


def test_combat_batch_correction():
    """Test ComBat batch correction with synthetic data."""

    print("=" * 80)
    print("COMBAT BATCH CORRECTION TEST")
    print("=" * 80)
    print()

    # Create synthetic data
    print("Creating synthetic data with batch effects...")
    print("-" * 80)

    n_genes = 100
    n_samples_per_batch = 20
    n_batches = 3
    batch_effect_size = 2.0
    biological_signal_size = 3.0

    data, batch_labels, true_signal, biological_groups = create_synthetic_batch_data(
        n_genes=n_genes,
        n_samples_per_batch=n_samples_per_batch,
        n_batches=n_batches,
        batch_effect_size=batch_effect_size,
        biological_signal_size=biological_signal_size
    )

    print(f"✅ Created data: {n_genes} genes × {len(batch_labels)} samples")
    print(f"✅ Batches: {n_batches} ({n_samples_per_batch} samples each)")
    print(f"✅ Batch effect size: {batch_effect_size}")
    print(f"✅ Biological signal size: {biological_signal_size}")
    print()

    # Convert to DataFrame
    sample_names = [f"sample_{i+1}" for i in range(len(batch_labels))]
    gene_names = [f"gene_{i+1}" for i in range(n_genes)]

    data_df = pd.DataFrame(data, index=gene_names, columns=sample_names)

    # Calculate batch variance BEFORE correction
    print("Analyzing batch effects BEFORE correction...")
    print("-" * 80)

    variance_before = _calculate_batch_variance(data.T, batch_labels)
    print(f"✅ Variance explained by batch: {variance_before:.4f} ({variance_before*100:.2f}%)")

    # Calculate per-batch statistics
    print()
    print("Per-batch statistics (gene means):")
    for batch in np.unique(batch_labels):
        batch_mask = (batch_labels == batch)
        batch_data = data[:, batch_mask]
        batch_mean = np.mean(batch_data)
        batch_std = np.std(batch_data)
        print(f"  {batch}: mean={batch_mean:7.3f}, std={batch_std:6.3f}")

    print()
    print("=" * 80)
    print()

    # Apply ComBat correction
    print("Applying ComBat batch correction...")
    print("-" * 80)

    corrected_df = _combat_batch_correction(data_df, batch_labels, parametric=True)
    corrected = corrected_df.values

    print(f"✅ ComBat correction complete")
    print()

    # Calculate batch variance AFTER correction
    print("Analyzing batch effects AFTER correction...")
    print("-" * 80)

    variance_after = _calculate_batch_variance(corrected.T, batch_labels)
    print(f"✅ Variance explained by batch: {variance_after:.4f} ({variance_after*100:.2f}%)")

    # Calculate per-batch statistics
    print()
    print("Per-batch statistics (gene means) after correction:")
    for batch in np.unique(batch_labels):
        batch_mask = (batch_labels == batch)
        batch_data = corrected[:, batch_mask]
        batch_mean = np.mean(batch_data)
        batch_std = np.std(batch_data)
        print(f"  {batch}: mean={batch_mean:7.3f}, std={batch_std:6.3f}")

    print()

    # Calculate variance reduction
    variance_reduction = (variance_before - variance_after) / variance_before
    print(f"✅ Batch variance reduction: {variance_reduction:.4f} ({variance_reduction*100:.2f}%)")
    print()

    print("=" * 80)
    print()

    # Test biological signal preservation
    print("Testing biological signal preservation...")
    print("-" * 80)

    # Calculate correlation between corrected data and true signal
    # Average correlation across all genes
    correlations = []
    for i in range(n_genes):
        corr = np.corrcoef(corrected[i, :], true_signal[i, :])[0, 1]
        correlations.append(corr)

    mean_corr = np.mean(correlations)
    print(f"✅ Mean correlation with true signal: {mean_corr:.4f}")

    # Test if biological groups are still distinguishable
    group0_samples = biological_groups == 0
    group1_samples = biological_groups == 1

    group0_mean = np.mean(corrected[:, group0_samples])
    group1_mean = np.mean(corrected[:, group1_samples])

    print(f"✅ Biological group 0 mean: {group0_mean:.3f}")
    print(f"✅ Biological group 1 mean: {group1_mean:.3f}")
    print(f"✅ Difference: {abs(group1_mean - group0_mean):.3f}")

    if abs(group1_mean - group0_mean) > 1.0:
        print("✅ Biological signal PRESERVED (groups still distinguishable)")
    else:
        print("⚠️  Biological signal may be WEAKENED")

    print()
    print("=" * 80)
    print()

    # Summary
    print("SUMMARY")
    print("=" * 80)
    print(f"Batch variance BEFORE: {variance_before*100:6.2f}%")
    print(f"Batch variance AFTER:  {variance_after*100:6.2f}%")
    print(f"Variance reduction:    {variance_reduction*100:6.2f}%")
    print(f"Signal preservation:   {mean_corr*100:6.2f}% (correlation)")
    print()

    if variance_reduction > 0.5 and mean_corr > 0.7:
        print("✅ ComBat batch correction SUCCESSFUL!")
        print("   - Batch effects significantly reduced")
        print("   - Biological signal well preserved")
    elif variance_reduction > 0.3:
        print("✅ ComBat batch correction MODERATE")
        print("   - Batch effects partially reduced")
        print("   - Some biological signal preserved")
    else:
        print("⚠️  ComBat batch correction WEAK")
        print("   - Batch effects not significantly reduced")

    print()
    print("=" * 80)
    print("✅ Batch correction test completed!")
    print("=" * 80)
    print()


if __name__ == "__main__":
    test_combat_batch_correction()
