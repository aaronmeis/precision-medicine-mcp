"""Google Cloud Storage handler for file access.

Provides utilities to access files from GCS buckets for MCP analysis.
"""

import os
import re
from typing import Tuple, Dict, Optional, Any
from pathlib import Path
import tempfile


def is_gcs_path(path: str) -> bool:
    """Check if a path is a valid GCS URI.

    Args:
        path: Path string to check

    Returns:
        True if path starts with gs://

    Example:
        >>> is_gcs_path("gs://my-bucket/data/file.fastq")
        True
        >>> is_gcs_path("/tmp/local/file.fastq")
        False
    """
    return path.strip().startswith("gs://")


def parse_gcs_uri(gcs_uri: str) -> Tuple[Optional[str], Optional[str]]:
    """Parse GCS URI into bucket and blob path.

    Args:
        gcs_uri: GCS URI (e.g., gs://bucket-name/path/to/file.fastq)

    Returns:
        Tuple of (bucket_name, blob_path) or (None, None) if invalid

    Example:
        >>> parse_gcs_uri("gs://my-bucket/data/sample.fastq")
        ('my-bucket', 'data/sample.fastq')
    """
    if not is_gcs_path(gcs_uri):
        return None, None

    # Remove gs:// prefix
    path = gcs_uri.replace("gs://", "")

    # Split into bucket and path
    parts = path.split("/", 1)
    if len(parts) < 2:
        return parts[0], ""  # Bucket only, no path

    return parts[0], parts[1]


def validate_gcs_uri(gcs_uri: str) -> Tuple[bool, Optional[str]]:
    """Validate GCS URI format.

    Args:
        gcs_uri: GCS URI to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not gcs_uri or not gcs_uri.strip():
        return False, "GCS URI is empty"

    if not is_gcs_path(gcs_uri):
        return False, "URI must start with gs://"

    bucket, blob = parse_gcs_uri(gcs_uri)

    if not bucket:
        return False, "Invalid GCS URI format. Expected: gs://bucket-name/path/to/file"

    # Validate bucket name (basic check)
    if not re.match(r'^[a-z0-9][a-z0-9\-_.]{1,61}[a-z0-9]$', bucket):
        return False, f"Invalid bucket name: {bucket}"

    if not blob:
        return False, "No file path specified after bucket name"

    return True, None


def get_gcs_file_metadata(gcs_uri: str, use_mock: bool = True) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
    """Get metadata for a file in GCS.

    Args:
        gcs_uri: GCS URI to the file
        use_mock: If True, return mock metadata without actually accessing GCS

    Returns:
        Tuple of (success, metadata_dict, error_message)

    Example:
        >>> success, metadata, error = get_gcs_file_metadata("gs://bucket/file.fastq")
        >>> if success:
        ...     print(f"Size: {metadata['size_mb']} MB")
    """
    # Validate URI format first
    is_valid, error = validate_gcs_uri(gcs_uri)
    if not is_valid:
        return False, None, error

    bucket, blob_path = parse_gcs_uri(gcs_uri)
    filename = Path(blob_path).name
    extension = Path(blob_path).suffix.lower()

    if use_mock:
        # Return mock metadata for testing
        metadata = {
            'filename': filename,
            'sanitized_filename': filename,
            'gcs_uri': gcs_uri,
            'bucket': bucket,
            'blob_path': blob_path,
            'size_bytes': 0,  # Unknown
            'size_mb': 0.0,
            'extension': extension,
            'is_binary': extension in {'.h5', '.h5ad', '.png', '.jpg', '.jpeg', '.tiff', '.tif', '.bam'},
            'source': 'gcs',
            'accessible': 'unknown'  # Can't verify without credentials
        }
        return True, metadata, None

    # Real GCS access (requires google-cloud-storage)
    try:
        from google.cloud import storage

        # Initialize GCS client
        # This will use Application Default Credentials or GOOGLE_APPLICATION_CREDENTIALS env var
        client = storage.Client()
        bucket_obj = client.bucket(bucket)
        blob = bucket_obj.blob(blob_path)

        # Check if blob exists
        if not blob.exists():
            return False, None, f"File not found in GCS: {gcs_uri}"

        # Get blob metadata
        blob.reload()  # Fetch latest metadata

        metadata = {
            'filename': filename,
            'sanitized_filename': filename,
            'gcs_uri': gcs_uri,
            'bucket': bucket,
            'blob_path': blob_path,
            'size_bytes': blob.size,
            'size_mb': blob.size / (1024 * 1024),
            'extension': extension,
            'content_type': blob.content_type,
            'is_binary': extension in {'.h5', '.h5ad', '.png', '.jpg', '.jpeg', '.tiff', '.tif', '.bam'},
            'source': 'gcs',
            'accessible': 'verified',
            'updated': blob.updated.isoformat() if blob.updated else None
        }

        return True, metadata, None

    except ImportError:
        return False, None, "google-cloud-storage library not installed. Using mock metadata."
    except Exception as e:
        return False, None, f"Error accessing GCS: {str(e)}"


def download_gcs_file(gcs_uri: str, max_size_bytes: int = 50 * 1024 * 1024) -> Tuple[bool, Optional[str], Optional[str]]:
    """Download a file from GCS to temporary location.

    Args:
        gcs_uri: GCS URI to download
        max_size_bytes: Maximum file size to download (default 50MB)

    Returns:
        Tuple of (success, local_path, error_message)
    """
    # Validate URI
    is_valid, error = validate_gcs_uri(gcs_uri)
    if not is_valid:
        return False, None, error

    # Get metadata first to check size
    success, metadata, error = get_gcs_file_metadata(gcs_uri, use_mock=False)
    if not success:
        return False, None, error

    # Check size limit
    if metadata['size_bytes'] > max_size_bytes:
        max_mb = max_size_bytes / (1024 * 1024)
        actual_mb = metadata['size_mb']
        return False, None, f"File too large ({actual_mb:.1f}MB). Maximum: {max_mb:.0f}MB"

    try:
        from google.cloud import storage

        bucket, blob_path = parse_gcs_uri(gcs_uri)

        # Create temp directory
        temp_dir = Path(tempfile.gettempdir()) / "mcp_uploads" / "gcs"
        temp_dir.mkdir(parents=True, exist_ok=True)

        # Download to temp file
        filename = metadata['sanitized_filename']
        local_path = temp_dir / filename

        client = storage.Client()
        bucket_obj = client.bucket(bucket)
        blob = bucket_obj.blob(blob_path)

        blob.download_to_filename(str(local_path))

        return True, str(local_path), None

    except ImportError:
        return False, None, "google-cloud-storage library not installed"
    except Exception as e:
        return False, None, f"Error downloading from GCS: {str(e)}"


def get_gcs_file_content(gcs_uri: str, max_size_bytes: int = 50 * 1024) -> Tuple[bool, Optional[str], Optional[str]]:
    """Read content of a small text file from GCS.

    Args:
        gcs_uri: GCS URI to read
        max_size_bytes: Maximum size to read (default 50KB for inline content)

    Returns:
        Tuple of (success, content_string, error_message)
    """
    # Download file first
    success, local_path, error = download_gcs_file(gcs_uri, max_size_bytes)
    if not success:
        return False, None, error

    try:
        with open(local_path, 'r') as f:
            content = f.read()
        return True, content, None
    except Exception as e:
        return False, None, f"Error reading file: {str(e)}"
