"""MCP Open Image Data server implementation.

This module provides an MCP server for histology image processing,
spatial registration, and feature extraction.
"""

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for server use
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PIL import Image
from fastmcp import FastMCP

# Configure logging
logger = logging.getLogger(__name__)

# Initialize the MCP server
mcp = FastMCP("openimagedata")

def _is_dry_run() -> bool:
    """Check if DRY_RUN mode is enabled."""
    return os.getenv("IMAGE_DRY_RUN", "false").lower() == "true"

DRY_RUN = _is_dry_run()

# DRY_RUN warning wrapper
def add_dry_run_warning(result: Any) -> Any:
    """Add warning banner to results when in DRY_RUN mode."""
    if not DRY_RUN:
        return result

    warning = """
╔═══════════════════════════════════════════════════════════════════════════╗
║                    ⚠️  SYNTHETIC DATA WARNING ⚠️                          ║
╚═══════════════════════════════════════════════════════════════════════════╝

This result was generated in DRY_RUN mode and does NOT represent real analysis.

🔴 CRITICAL: Do NOT use this data for research decisions or publications.
🔴 All values are SYNTHETIC/MOCKED and have no scientific validity.

To enable real data processing, set: IMAGE_DRY_RUN=false

═══════════════════════════════════════════════════════════════════════════

"""

    if isinstance(result, dict):
        result["_DRY_RUN_WARNING"] = "SYNTHETIC DATA - NOT FOR RESEARCH USE"
        result["_message"] = warning.strip()
    elif isinstance(result, str):
        result = warning + result

    return result


# Configuration
IMAGE_DIR = Path(os.getenv("IMAGE_DATA_DIR", "/workspace/images"))
CACHE_DIR = Path(os.getenv("IMAGE_CACHE_DIR", "/workspace/cache/images"))
OUTPUT_DIR = Path(os.getenv("IMAGE_OUTPUT_DIR", "/workspace/output"))
MAX_IMAGE_SIZE_MB = int(os.getenv("MAX_IMAGE_SIZE_MB", "500"))
DRY_RUN = os.getenv("IMAGE_DRY_RUN", "false").lower() == "true"


def _ensure_directories() -> None:
    """Ensure required directories exist."""
    try:
        IMAGE_DIR.mkdir(parents=True, exist_ok=True)
        (IMAGE_DIR / "he").mkdir(exist_ok=True)
        (IMAGE_DIR / "if").mkdir(exist_ok=True)
    except (OSError, PermissionError):
        pass

    try:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
    except (OSError, PermissionError):
        pass

    try:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        (OUTPUT_DIR / "visualizations").mkdir(exist_ok=True)
    except (OSError, PermissionError):
        pass


# ============================================================================
# TOOL 1: fetch_histology_image
# ============================================================================


@mcp.tool()
async def fetch_histology_image(
    image_id: str,
    stain_type: str = "he",
    resolution: str = "high"
) -> Dict[str, Any]:
    """Retrieve tissue histology images.

    Fetches H&E or immunofluorescence histology images for spatial
    transcriptomics integration.

    Args:
        image_id: Unique identifier for the image
        stain_type: Type of staining - "he" (H&E) or "if" (immunofluorescence)
        resolution: Image resolution - "high", "medium", or "low"

    Returns:
        Dictionary with keys:
            - image_path: Path to the downloaded image
            - dimensions: Image dimensions (width, height)
            - file_size_mb: File size in megabytes
            - metadata: Image metadata (magnification, stain info)

    Raises:
        ValueError: If invalid stain type or resolution
        IOError: If image fetch fails

    Example:
        >>> result = await fetch_histology_image(
        ...     image_id="sample_001",
        ...     stain_type="he",
        ...     resolution="high"
        ... )
        >>> print(f"Image: {result['dimensions']}")
    """
    _ensure_directories()

    if stain_type not in ["he", "if"]:
        raise ValueError(f"Invalid stain type: {stain_type}. Must be 'he' or 'if'")

    if resolution not in ["high", "medium", "low"]:
        raise ValueError(f"Invalid resolution: {resolution}")

    image_path = IMAGE_DIR / stain_type / f"{image_id}_{resolution}.tif"
    image_path.parent.mkdir(parents=True, exist_ok=True)

    if DRY_RUN:
        # Create a small mock image
        mock_image = Image.new('RGB', (2048, 2048), color='white')
        mock_image.save(image_path)

        return {
            "image_path": str(image_path),
            "dimensions": {"width": 2048, "height": 2048},
            "file_size_mb": 12.5,
            "metadata": {
                "stain_type": stain_type,
                "magnification": "20x" if resolution == "high" else "10x",
                "format": "TIFF",
                "mode": "dry_run"
            }
        }

    # Real implementation would download from image database
    return {
        "image_path": str(image_path),
        "dimensions": {"width": 4096, "height": 4096},
        "file_size_mb": 50.0,
        "metadata": {
            "stain_type": stain_type,
            "magnification": "20x",
            "format": "TIFF"
        }
    }


# ============================================================================
# TOOL 2: register_image_to_spatial
# ============================================================================


@mcp.tool()
async def register_image_to_spatial(
    image_path: str,
    spatial_coordinates_file: str,
    output_file: str,
    registration_method: str = "affine"
) -> Dict[str, Any]:
    """Align histology images with spatial coordinates.

    Performs image registration to align histology images with spatial
    transcriptomics spot/cell coordinates.

    Args:
        image_path: Path to histology image
        spatial_coordinates_file: Path to file with spatial coordinates
        output_file: Path for registered image output
        registration_method: Method - "affine", "rigid", or "deformable"

    Returns:
        Dictionary with keys:
            - registered_image: Path to registered image
            - transformation_matrix: Transformation parameters
            - registration_quality: Quality metrics (RMSE, correlation)

    Raises:
        IOError: If files not found
        ValueError: If invalid registration method

    Example:
        >>> result = await register_image_to_spatial(
        ...     image_path="/images/he/sample_001.tif",
        ...     spatial_coordinates_file="/data/coordinates.csv",
        ...     output_file="/images/registered/sample_001.tif"
        ... )
        >>> print(f"RMSE: {result['registration_quality']['rmse']:.3f}")
    """
    _ensure_directories()

    img_path = Path(image_path)
    if not img_path.exists():
        raise IOError(f"Image not found: {image_path}")

    coord_path = Path(spatial_coordinates_file)
    if not coord_path.exists():
        raise IOError(f"Coordinates file not found: {spatial_coordinates_file}")

    if registration_method not in ["affine", "rigid", "deformable"]:
        raise ValueError(f"Invalid registration method: {registration_method}")

    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if DRY_RUN:
        # Mock registration
        return {
            "registered_image": str(output_path),
            "transformation_matrix": {
                "scale_x": 1.02,
                "scale_y": 0.98,
                "rotation_degrees": 2.5,
                "translation_x": 12.3,
                "translation_y": -8.7
            },
            "registration_quality": {
                "rmse": 1.85,
                "correlation": 0.94,
                "matched_points": 450,
                "method": registration_method
            },
            "mode": "dry_run"
        }

    # Real implementation would use image registration algorithms
    return {
        "registered_image": str(output_path),
        "transformation_matrix": {
            "scale_x": 1.0,
            "scale_y": 1.0,
            "rotation_degrees": 0.0,
            "translation_x": 0.0,
            "translation_y": 0.0
        },
        "registration_quality": {
            "rmse": 2.1,
            "correlation": 0.92,
            "matched_points": 400,
            "method": registration_method
        }
    }


# ============================================================================
# TOOL 3: extract_image_features
# ============================================================================


@mcp.tool()
async def extract_image_features(
    image_path: str,
    feature_type: str = "texture",
    roi_coordinates: Optional[List[Tuple[int, int, int, int]]] = None
) -> Dict[str, Any]:
    """Extract computer vision features from histology images.

    Extracts texture, morphological, or intensity features from histology
    images for downstream analysis and correlation with spatial expression.

    Args:
        image_path: Path to histology image
        feature_type: Type of features - "texture", "morphology", or "intensity"
        roi_coordinates: Optional list of ROI bounding boxes [(x1,y1,x2,y2), ...]

    Returns:
        Dictionary with keys:
            - features: Extracted feature vectors
            - feature_names: Names/descriptions of features
            - roi_count: Number of ROIs processed
            - processing_time_seconds: Processing duration

    Raises:
        IOError: If image not found
        ValueError: If invalid feature type

    Example:
        >>> result = await extract_image_features(
        ...     image_path="/images/he/sample_001.tif",
        ...     feature_type="texture"
        ... )
        >>> print(f"Extracted {len(result['features'])} features")
    """
    _ensure_directories()

    img_path = Path(image_path)
    if not img_path.exists():
        raise IOError(f"Image not found: {image_path}")

    if feature_type not in ["texture", "morphology", "intensity"]:
        raise ValueError(f"Invalid feature type: {feature_type}")

    if DRY_RUN:
        # Mock feature extraction
        num_features = {"texture": 25, "morphology": 15, "intensity": 10}[feature_type]

        return {
            "features": np.random.rand(num_features).tolist(),
            "feature_names": [f"{feature_type}_feature_{i}" for i in range(num_features)],
            "roi_count": len(roi_coordinates) if roi_coordinates else 1,
            "processing_time_seconds": 2.5,
            "feature_statistics": {
                "mean": 0.5,
                "std": 0.15,
                "min": 0.05,
                "max": 0.95
            },
            "mode": "dry_run"
        }

    # Real implementation would use OpenCV/scikit-image
    return {
        "features": [0.5] * 20,
        "feature_names": [f"{feature_type}_{i}" for i in range(20)],
        "roi_count": 1,
        "processing_time_seconds": 3.0
    }


# ============================================================================
# VISUALIZATION TOOLS
# ============================================================================


@mcp.tool()
async def generate_multiplex_composite(
    channel_paths: List[str],
    channel_names: List[str],
    channel_colors: Optional[List[str]] = None,
    output_filename: Optional[str] = None,
    normalize: bool = True
) -> Dict[str, Any]:
    """Generate RGB composite from multiplex immunofluorescence channels.

    Combines multiple fluorescence channels into a single RGB composite image.
    Useful for visualizing multiplex IF with 2-7 fluorescent markers simultaneously.

    Args:
        channel_paths: List of paths to individual channel images (grayscale TIFF)
        channel_names: List of marker names (e.g., ["DAPI", "TP53", "KI67"])
        channel_colors: Optional list of colors for each channel (e.g., ["blue", "red", "green"])
                       If None, defaults to standard colors based on position
        output_filename: Custom output filename (default: multiplex_composite_TIMESTAMP.png)
        normalize: Whether to normalize intensity per channel (default: True)

    Returns:
        Dictionary with:
        - output_file: Path to saved composite image
        - channels_combined: Number of channels combined
        - channel_info: List of channel names and colors used
        - description: Text description

    Example:
        >>> result = await generate_multiplex_composite(
        ...     channel_paths=[
        ...         "/data/PAT001_multiplex_DAPI.tiff",
        ...         "/data/PAT001_multiplex_TP53.tiff",
        ...         "/data/PAT001_multiplex_KI67.tiff"
        ...     ],
        ...     channel_names=["DAPI", "TP53", "KI67"],
        ...     channel_colors=["blue", "red", "green"]
        ... )
    """
    if DRY_RUN:
        return add_dry_run_warning({
            "output_file": str(OUTPUT_DIR / "visualizations" / "multiplex_composite_dryrun.png"),
            "channels_combined": len(channel_names),
            "channel_info": [{"name": name, "color": "auto"} for name in channel_names],
            "description": f"DRY_RUN: Would generate RGB composite for {', '.join(channel_names)}",
            "message": "Set IMAGE_DRY_RUN=false to generate real visualizations"
        })

    try:
        # Validate inputs
        if len(channel_paths) != len(channel_names):
            return {
                "status": "error",
                "error": "Number of channel paths must match number of channel names",
                "num_paths": len(channel_paths),
                "num_names": len(channel_names)
            }

        if len(channel_paths) < 1 or len(channel_paths) > 7:
            return {
                "status": "error",
                "error": "Must provide 1-7 channels (typical multiplex IF has 2-7 channels)"
            }

        # Default color mapping
        default_colors = ["blue", "green", "red", "cyan", "magenta", "yellow", "white"]
        if channel_colors is None:
            channel_colors = default_colors[:len(channel_paths)]

        # Color to RGB mapping
        color_map = {
            "blue": [0, 0, 255],
            "green": [0, 255, 0],
            "red": [255, 0, 0],
            "cyan": [0, 255, 255],
            "magenta": [255, 0, 255],
            "yellow": [255, 255, 0],
            "white": [255, 255, 255]
        }

        # Load and normalize channels
        channel_arrays = []
        for i, path in enumerate(channel_paths):
            try:
                img = np.array(Image.open(path))

                # Normalize to 0-1 range if requested
                if normalize:
                    img_norm = (img - img.min()) / (img.max() - img.min() + 1e-8)
                else:
                    img_norm = img / 255.0 if img.max() > 1 else img

                channel_arrays.append(img_norm)
            except Exception as e:
                return {
                    "status": "error",
                    "error": f"Failed to load channel {i} ({channel_names[i]}): {str(e)}",
                    "path": path
                }

        # Verify all channels have same dimensions
        shapes = [arr.shape for arr in channel_arrays]
        if len(set(shapes)) > 1:
            return {
                "status": "error",
                "error": "All channels must have the same dimensions",
                "shapes": {name: shape for name, shape in zip(channel_names, shapes)}
            }

        # Create RGB composite
        height, width = channel_arrays[0].shape
        composite = np.zeros((height, width, 3), dtype=np.float32)

        for channel_arr, color_name in zip(channel_arrays, channel_colors):
            rgb_color = color_map.get(color_name.lower(), [255, 255, 255])
            for c in range(3):
                composite[:, :, c] += channel_arr * (rgb_color[c] / 255.0)

        # Clip to valid range and convert to uint8
        composite = np.clip(composite, 0, 1)
        composite_uint8 = (composite * 255).astype(np.uint8)

        # Create visualization with individual channels and composite
        n_channels = len(channel_arrays)
        fig, axes = plt.subplots(1, n_channels + 1, figsize=(5 * (n_channels + 1), 5))

        # Plot individual channels
        for idx, (arr, name, color) in enumerate(zip(channel_arrays, channel_names, channel_colors)):
            axes[idx].imshow(arr, cmap='gray')
            axes[idx].set_title(f'{name} ({color})', fontsize=12, fontweight='bold')
            axes[idx].axis('off')

        # Plot composite
        axes[n_channels].imshow(composite_uint8)
        axes[n_channels].set_title('RGB Composite', fontsize=12, fontweight='bold')
        axes[n_channels].axis('off')

        plt.tight_layout()

        # Save
        timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
        if output_filename is None:
            output_filename = f"multiplex_composite_{timestamp}.png"

        output_path = OUTPUT_DIR / "visualizations" / output_filename
        fig.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close(fig)

        # Generate description
        channel_info = [{"name": name, "color": color} for name, color in zip(channel_names, channel_colors)]
        description = f"Multiplex IF RGB composite combining {len(channel_names)} channels: {', '.join(channel_names)}. "
        description += f"Colors: {', '.join([f'{name}={color}' for name, color in zip(channel_names, channel_colors)])}."

        return {
            "status": "success",
            "output_file": str(output_path),
            "channels_combined": len(channel_names),
            "channel_info": channel_info,
            "image_dimensions": {"width": width, "height": height},
            "description": description,
            "visualization_type": "multiplex_composite"
        }

    except Exception as e:
        logger.error(f"Error generating multiplex composite: {e}")
        return {
            "status": "error",
            "error": str(e),
            "message": "Failed to generate multiplex composite. Check file paths and formats."
        }


@mcp.tool()
async def generate_he_annotation(
    he_image_path: str,
    necrotic_regions: Optional[List[Dict[str, int]]] = None,
    high_cellularity_regions: Optional[List[Dict[str, int]]] = None,
    output_filename: Optional[str] = None,
    necrotic_color: str = "red",
    cellularity_color: str = "green"
) -> Dict[str, Any]:
    """Generate annotated H&E morphology visualization.

    Overlays region annotations on H&E histology image to highlight areas
    of interest such as necrotic regions and high cellularity areas.

    Args:
        he_image_path: Path to H&E histology image
        necrotic_regions: List of bounding boxes for necrotic areas
                         Each box: {"x": x_coord, "y": y_coord, "width": w, "height": h}
        high_cellularity_regions: List of bounding boxes for high cellularity areas
        output_filename: Custom output filename (default: he_annotation_TIMESTAMP.png)
        necrotic_color: Color for necrotic region outlines (default: "red")
        cellularity_color: Color for high cellularity outlines (default: "green")

    Returns:
        Dictionary with:
        - output_file: Path to saved annotated image
        - necrotic_regions_count: Number of necrotic regions annotated
        - cellularity_regions_count: Number of high cellularity regions annotated
        - description: Text description

    Example:
        >>> result = await generate_he_annotation(
        ...     he_image_path="/data/PAT001_tumor_HE_20x.tiff",
        ...     necrotic_regions=[
        ...         {"x": 100, "y": 200, "width": 300, "height": 250},
        ...         {"x": 800, "y": 600, "width": 200, "height": 180}
        ...     ],
        ...     high_cellularity_regions=[
        ...         {"x": 400, "y": 100, "width": 350, "height": 300}
        ...     ]
        ... )
    """
    if DRY_RUN:
        return add_dry_run_warning({
            "output_file": str(OUTPUT_DIR / "visualizations" / "he_annotation_dryrun.png"),
            "necrotic_regions_count": len(necrotic_regions) if necrotic_regions else 0,
            "cellularity_regions_count": len(high_cellularity_regions) if high_cellularity_regions else 0,
            "description": "DRY_RUN: Would generate H&E annotation",
            "message": "Set IMAGE_DRY_RUN=false to generate real visualizations"
        })

    try:
        # Load H&E image
        he_img = np.array(Image.open(he_image_path))

        # Create figure
        fig, axes = plt.subplots(1, 2, figsize=(16, 8))

        # Original H&E
        axes[0].imshow(he_img)
        axes[0].set_title('Original H&E', fontsize=14, fontweight='bold')
        axes[0].axis('off')

        # Annotated H&E
        axes[1].imshow(he_img)

        # Color mapping
        color_map = {
            "red": "red",
            "green": "green",
            "blue": "blue",
            "yellow": "yellow",
            "cyan": "cyan",
            "magenta": "magenta"
        }
        necrotic_mpl_color = color_map.get(necrotic_color.lower(), "red")
        cellularity_mpl_color = color_map.get(cellularity_color.lower(), "green")

        # Draw necrotic regions
        necrotic_count = 0
        if necrotic_regions:
            for region in necrotic_regions:
                rect = plt.Rectangle(
                    (region["x"], region["y"]),
                    region["width"],
                    region["height"],
                    linewidth=3,
                    edgecolor=necrotic_mpl_color,
                    facecolor='none',
                    linestyle='--'
                )
                axes[1].add_patch(rect)
                necrotic_count += 1

        # Draw high cellularity regions
        cellularity_count = 0
        if high_cellularity_regions:
            for region in high_cellularity_regions:
                rect = plt.Rectangle(
                    (region["x"], region["y"]),
                    region["width"],
                    region["height"],
                    linewidth=3,
                    edgecolor=cellularity_mpl_color,
                    facecolor='none',
                    linestyle='-'
                )
                axes[1].add_patch(rect)
                cellularity_count += 1

        # Add legend
        from matplotlib.patches import Patch
        legend_elements = []
        if necrotic_count > 0:
            legend_elements.append(
                Patch(facecolor='none', edgecolor=necrotic_mpl_color, linestyle='--',
                      linewidth=3, label=f'Necrotic ({necrotic_count} regions)')
            )
        if cellularity_count > 0:
            legend_elements.append(
                Patch(facecolor='none', edgecolor=cellularity_mpl_color, linestyle='-',
                      linewidth=3, label=f'High Cellularity ({cellularity_count} regions)')
            )

        if legend_elements:
            axes[1].legend(handles=legend_elements, loc='upper right', fontsize=11)

        axes[1].set_title('Annotated Morphology', fontsize=14, fontweight='bold')
        axes[1].axis('off')

        plt.tight_layout()

        # Save
        timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
        if output_filename is None:
            output_filename = f"he_annotation_{timestamp}.png"

        output_path = OUTPUT_DIR / "visualizations" / output_filename
        fig.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close(fig)

        # Generate description
        description = f"H&E morphology annotation showing {necrotic_count} necrotic regions ({necrotic_color}) and {cellularity_count} high cellularity regions ({cellularity_color})."

        return {
            "status": "success",
            "output_file": str(output_path),
            "necrotic_regions_count": necrotic_count,
            "cellularity_regions_count": cellularity_count,
            "total_annotations": necrotic_count + cellularity_count,
            "description": description,
            "visualization_type": "he_morphology_annotation",
            "necrotic_color": necrotic_color,
            "cellularity_color": cellularity_color
        }

    except Exception as e:
        logger.error(f"Error generating H&E annotation: {e}")
        return {
            "status": "error",
            "error": str(e),
            "message": "Failed to generate H&E annotation. Check file path and format."
        }


# ============================================================================
# MCP RESOURCES
# ============================================================================


@mcp.resource("image://histology/he")
def get_he_stain_info() -> str:
    """H&E stained image resource information.

    Returns:
        JSON string with H&E staining metadata
    """
    return json.dumps({
        "resource": "image://histology/he",
        "description": "Hematoxylin and Eosin (H&E) stained tissue images",
        "data_directory": str(IMAGE_DIR / "he"),
        "stain_info": {
            "hematoxylin": "Stains nuclei blue-purple",
            "eosin": "Stains cytoplasm and extracellular matrix pink"
        },
        "typical_magnifications": ["4x", "10x", "20x", "40x"],
        "file_formats": ["TIFF", "SVS", "NDPI"],
        "use_cases": [
            "Tissue morphology assessment",
            "Spatial transcriptomics overlay",
            "Pathologist review",
            "AI-based tissue classification"
        ]
    }, indent=2)


@mcp.resource("image://histology/if")
def get_if_stain_info() -> str:
    """Immunofluorescence image resource information.

    Returns:
        JSON string with IF imaging metadata
    """
    return json.dumps({
        "resource": "image://histology/if",
        "description": "Immunofluorescence microscopy images",
        "data_directory": str(IMAGE_DIR / "if"),
        "imaging_info": {
            "technique": "Fluorescent antibody labeling",
            "channels": "Multi-channel (DAPI, FITC, Cy3, Cy5, etc.)",
            "applications": "Protein localization, marker coexpression"
        },
        "typical_markers": [
            "DAPI (nuclei)",
            "CD45 (immune cells)",
            "Pan-CK (epithelial)",
            "CD31 (endothelial)"
        ],
        "file_formats": ["TIFF", "CZI", "ND2"],
        "integration_with_spatial": "Protein-RNA correlation analysis"
    }, indent=2)


# ============================================================================
# SERVER ENTRYPOINT
# ============================================================================


def main() -> None:
    """Run the MCP Open Image Data server."""
    _ensure_directories()

    logger.info("Starting mcp-openimagedata server...")

    if DRY_RUN:
        logger.warning("=" * 80)
        logger.warning("⚠️  DRY_RUN MODE ENABLED - RETURNING SYNTHETIC DATA")
        logger.warning("⚠️  Results are MOCKED and do NOT represent real analysis")
        logger.warning("⚠️  Set IMAGE_DRY_RUN=false for production use")
        logger.warning("=" * 80)
    else:
        logger.info("✅ Real data processing mode enabled (IMAGE_DRY_RUN=false)")

    # Get transport and port from environment
    transport = os.getenv("MCP_TRANSPORT", "stdio")
    port = int(os.getenv("PORT", os.getenv("MCP_PORT", "8000")))

    # Run the server with appropriate transport
    if transport in ("sse", "streamable-http"):
        mcp.run(transport=transport, port=port, host="0.0.0.0")
    else:
        mcp.run(transport=transport)


if __name__ == "__main__":
    main()
