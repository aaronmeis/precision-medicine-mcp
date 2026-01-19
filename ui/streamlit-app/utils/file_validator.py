"""File validation utilities for secure file uploads.

Provides validation for bioinformatics file formats with security checks
including magic bytes verification, content validation, and filename sanitization.
"""

import os
import re
import json
import tempfile
from typing import Tuple, Dict, List, Optional, Any
from pathlib import Path
import streamlit as st


# Extension whitelist for bioinformatics formats
ALLOWED_EXTENSIONS = {
    # Sequence formats
    '.fasta', '.fa', '.fna',
    '.fastq', '.fq',
    '.vcf',
    # Annotation formats
    '.gff', '.gtf', '.bed',
    # Tabular formats
    '.csv', '.tsv', '.tab', '.txt',
    # Structured data
    '.json',
    # Binary formats
    '.h5ad', '.h5',
    # Image formats
    '.png', '.jpg', '.jpeg', '.tiff', '.tif'
}

# Magic bytes for binary format verification
MAGIC_BYTES = {
    '.png': b'\x89PNG\r\n\x1a\n',
    '.jpg': b'\xff\xd8\xff',
    '.jpeg': b'\xff\xd8\xff',
    '.tiff': [b'II\x2a\x00', b'MM\x00\x2a'],  # Little/Big endian
    '.tif': [b'II\x2a\x00', b'MM\x00\x2a'],
    '.h5': b'\x89HDF',
    '.h5ad': b'\x89HDF',
}

# Default max file size (100 MB)
DEFAULT_MAX_SIZE_MB = 100
DEFAULT_MAX_SIZE_BYTES = DEFAULT_MAX_SIZE_MB * 1024 * 1024


class FileValidationError(Exception):
    """Custom exception for file validation errors."""
    pass


def sanitize_filename(filename: str) -> str:
    """Sanitize filename to prevent path traversal and special characters.

    Args:
        filename: Original filename

    Returns:
        Sanitized filename safe for filesystem use

    Example:
        >>> sanitize_filename("../../etc/passwd")
        'etc_passwd'
        >>> sanitize_filename("my file.txt")
        'my_file.txt'
    """
    # Get basename only (no path components)
    filename = os.path.basename(filename)

    # Remove or replace dangerous characters
    filename = re.sub(r'[^\w\s\-\.]', '_', filename)

    # Replace multiple underscores/spaces with single underscore
    filename = re.sub(r'[_\s]+', '_', filename)

    # Remove leading/trailing dots and underscores
    filename = filename.strip('._')

    # Limit length
    name, ext = os.path.splitext(filename)
    if len(name) > 200:
        name = name[:200]

    return name + ext


def check_file_size(file_size: int, max_size_bytes: int = DEFAULT_MAX_SIZE_BYTES) -> Tuple[bool, Optional[str]]:
    """Check if file size is within allowed limits.

    Args:
        file_size: File size in bytes
        max_size_bytes: Maximum allowed size in bytes

    Returns:
        Tuple of (is_valid, error_message)
    """
    if file_size > max_size_bytes:
        max_mb = max_size_bytes / (1024 * 1024)
        actual_mb = file_size / (1024 * 1024)
        return False, f"File too large ({actual_mb:.1f}MB). Maximum allowed: {max_mb:.0f}MB"

    if file_size == 0:
        return False, "File is empty"

    return True, None


def check_extension(filename: str) -> Tuple[bool, Optional[str]]:
    """Check if file extension is in the whitelist.

    Args:
        filename: Name of the file

    Returns:
        Tuple of (is_valid, error_message)
    """
    ext = os.path.splitext(filename.lower())[1]

    if not ext:
        return False, "File has no extension"

    if ext not in ALLOWED_EXTENSIONS:
        return False, f"File type '{ext}' not allowed. Allowed types: {', '.join(sorted(ALLOWED_EXTENSIONS))}"

    return True, None


def verify_magic_bytes(file_content: bytes, filename: str) -> Tuple[bool, Optional[str]]:
    """Verify magic bytes for binary file formats.

    Args:
        file_content: Raw file content (bytes)
        filename: Name of the file (for extension)

    Returns:
        Tuple of (is_valid, error_message)
    """
    ext = os.path.splitext(filename.lower())[1]

    # Only check magic bytes for known binary formats
    if ext not in MAGIC_BYTES:
        return True, None  # Skip validation for text formats

    expected_magic = MAGIC_BYTES[ext]

    # Handle multiple possible magic byte sequences
    if isinstance(expected_magic, list):
        for magic in expected_magic:
            if file_content.startswith(magic):
                return True, None
        return False, f"Invalid {ext} file: magic bytes do not match"
    else:
        if file_content.startswith(expected_magic):
            return True, None
        return False, f"Invalid {ext} file: magic bytes do not match"


def validate_fasta_content(content: str) -> Tuple[bool, Optional[str]]:
    """Validate FASTA file format.

    Args:
        content: File content as string

    Returns:
        Tuple of (is_valid, error_message)
    """
    lines = content.strip().split('\n')

    if not lines:
        return False, "FASTA file is empty"

    if not lines[0].startswith('>'):
        return False, "FASTA file must start with '>' header line"

    # Check for at least one sequence line
    has_sequence = any(line and not line.startswith('>') for line in lines[1:])
    if not has_sequence:
        return False, "FASTA file has no sequence data"

    return True, None


def validate_fastq_content(content: str) -> Tuple[bool, Optional[str]]:
    """Validate FASTQ file format.

    Args:
        content: File content as string

    Returns:
        Tuple of (is_valid, error_message)
    """
    lines = content.strip().split('\n')

    if not lines:
        return False, "FASTQ file is empty"

    if not lines[0].startswith('@'):
        return False, "FASTQ file must start with '@' header line"

    # Check basic FASTQ structure (4 lines per record minimum)
    if len(lines) < 4:
        return False, "FASTQ file incomplete (needs at least 4 lines)"

    return True, None


def validate_vcf_content(content: str) -> Tuple[bool, Optional[str]]:
    """Validate VCF file format.

    Args:
        content: File content as string

    Returns:
        Tuple of (is_valid, error_message)
    """
    lines = content.strip().split('\n')

    if not lines:
        return False, "VCF file is empty"

    # Check for required fileformat header
    has_format = any('##fileformat=VCF' in line for line in lines[:10])
    if not has_format:
        return False, "VCF file missing required '##fileformat=VCF' header"

    return True, None


def validate_csv_tsv_content(content: str, delimiter: str = ',') -> Tuple[bool, Optional[str]]:
    """Validate CSV/TSV file format.

    Args:
        content: File content as string
        delimiter: Field delimiter (',' for CSV, '\t' for TSV)

    Returns:
        Tuple of (is_valid, error_message)
    """
    lines = content.strip().split('\n')

    if not lines:
        return False, "File is empty"

    # Check consistent column counts
    col_counts = [len(line.split(delimiter)) for line in lines if line.strip()]

    if not col_counts:
        return False, "File has no data rows"

    if len(set(col_counts)) > 1:
        return False, f"Inconsistent column counts: found rows with {min(col_counts)}-{max(col_counts)} columns"

    return True, None


def validate_json_content(content: str) -> Tuple[bool, Optional[str]]:
    """Validate JSON file format.

    Args:
        content: File content as string

    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        json.loads(content)
        return True, None
    except json.JSONDecodeError as e:
        return False, f"Invalid JSON: {str(e)}"


def validate_text_encoding(content: bytes) -> Tuple[bool, Optional[str]]:
    """Validate that file content is valid UTF-8.

    Args:
        content: Raw file content

    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        content.decode('utf-8')
        return True, None
    except UnicodeDecodeError:
        return False, "File is not valid UTF-8 text"


def validate_file_content(content: bytes, filename: str) -> Tuple[bool, List[str]]:
    """Validate file content based on format.

    Args:
        content: Raw file content
        filename: Name of the file

    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    ext = os.path.splitext(filename.lower())[1]

    # Verify magic bytes for binary formats
    is_valid, error = verify_magic_bytes(content, filename)
    if not is_valid:
        errors.append(error)
        return False, errors

    # For binary formats, skip text content validation
    if ext in {'.h5', '.h5ad', '.png', '.jpg', '.jpeg', '.tiff', '.tif'}:
        return True, []

    # Validate text encoding
    is_valid, error = validate_text_encoding(content)
    if not is_valid:
        errors.append(error)
        return False, errors

    # Decode for text content validation
    text_content = content.decode('utf-8')

    # Format-specific validation
    if ext in {'.fasta', '.fa', '.fna'}:
        is_valid, error = validate_fasta_content(text_content)
        if not is_valid:
            errors.append(error)

    elif ext in {'.fastq', '.fq'}:
        is_valid, error = validate_fastq_content(text_content)
        if not is_valid:
            errors.append(error)

    elif ext == '.vcf':
        is_valid, error = validate_vcf_content(text_content)
        if not is_valid:
            errors.append(error)

    elif ext == '.csv':
        is_valid, error = validate_csv_tsv_content(text_content, delimiter=',')
        if not is_valid:
            errors.append(error)

    elif ext in {'.tsv', '.tab'}:
        is_valid, error = validate_csv_tsv_content(text_content, delimiter='\t')
        if not is_valid:
            errors.append(error)

    elif ext == '.json':
        is_valid, error = validate_json_content(text_content)
        if not is_valid:
            errors.append(error)

    return len(errors) == 0, errors


def extract_file_metadata(content: bytes, filename: str) -> Dict[str, Any]:
    """Extract metadata from validated file.

    Args:
        content: Raw file content
        filename: Name of the file

    Returns:
        Dictionary with file metadata
    """
    metadata = {
        'filename': filename,
        'sanitized_filename': sanitize_filename(filename),
        'size_bytes': len(content),
        'size_mb': len(content) / (1024 * 1024),
        'extension': os.path.splitext(filename.lower())[1],
    }

    # Add format-specific metadata for text files
    ext = metadata['extension']
    if ext not in {'.h5', '.h5ad', '.png', '.jpg', '.jpeg', '.tiff', '.tif'}:
        try:
            text_content = content.decode('utf-8')
            lines = text_content.split('\n')
            metadata['line_count'] = len(lines)
            metadata['is_binary'] = False
        except:
            metadata['is_binary'] = True
    else:
        metadata['is_binary'] = True

    return metadata


def validate_uploaded_file(
    uploaded_file: st.runtime.uploaded_file_manager.UploadedFile,
    max_size_mb: int = DEFAULT_MAX_SIZE_MB
) -> Tuple[bool, List[str], Dict[str, Any]]:
    """Main validation function for uploaded files.

    Performs comprehensive security and format validation:
    - File size check
    - Extension whitelist
    - Magic bytes verification (binary files)
    - Content format validation (text files)
    - Filename sanitization

    Args:
        uploaded_file: Streamlit UploadedFile object
        max_size_mb: Maximum file size in megabytes

    Returns:
        Tuple of (is_valid, list_of_errors, metadata_dict)

    Example:
        >>> is_valid, errors, metadata = validate_uploaded_file(uploaded_file)
        >>> if is_valid:
        ...     st.success(f"Valid file: {metadata['filename']}")
        ... else:
        ...     st.error(f"Invalid file: {errors}")
    """
    errors = []

    # Check file size
    file_size = uploaded_file.size
    is_valid, error = check_file_size(file_size, max_size_mb * 1024 * 1024)
    if not is_valid:
        errors.append(error)
        return False, errors, {}

    # Check extension
    filename = uploaded_file.name
    is_valid, error = check_extension(filename)
    if not is_valid:
        errors.append(error)
        return False, errors, {}

    # Read file content
    content = uploaded_file.read()
    uploaded_file.seek(0)  # Reset file pointer

    # Validate content
    is_valid, content_errors = validate_file_content(content, filename)
    errors.extend(content_errors)

    if errors:
        return False, errors, {}

    # Extract metadata
    metadata = extract_file_metadata(content, filename)

    return True, [], metadata
