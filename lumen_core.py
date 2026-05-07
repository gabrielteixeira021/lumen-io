"""
Core conversion logic for the Lumen TIFF to PNG tool.
"""

import os
import tempfile
import zipfile

from PIL import Image


class LumenError(Exception):
    """Base error for recoverable conversion failures."""


def _emit_log(log_callback, message, level="info"):
    """Send log messages to an optional callback."""
    if log_callback is not None:
        log_callback(level, message)


def validate_zip(file_path):
    """Validate that the input file exists and is a valid ZIP archive."""
    if not os.path.exists(file_path):
        raise LumenError(f"Input file does not exist: {file_path}")

    if not zipfile.is_zipfile(file_path):
        raise LumenError(f"File is not a valid ZIP archive: {file_path}")


def extract_zip(zip_path, extract_dir):
    """Extract ZIP archive to the specified directory."""
    try:
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(extract_dir)
    except Exception as exc:
        raise LumenError(f"Failed to extract ZIP archive: {exc}") from exc


def is_tiff_file(filename):
    """Check if a file is a TIFF image based on extension."""
    return filename.lower().endswith((".tif", ".tiff"))


def _get_bit_depth(img, tiff_path, log_callback=None):
    """Infer bit depth from the image mode for logging/reporting."""
    mode = img.mode

    if mode in ("L", "P"):
        return 8
    if mode == "I;16":
        return 16
    if mode == "RGB":
        if img.getbands() and len(img.getbands()) == 3:
            band = img.getchannel(0) if hasattr(img, "getchannel") else img.split()[0]
            return 16 if band.mode == "I;16" else 8
        return 8
    if mode == "RGBA":
        return 8

    _emit_log(
        log_callback,
        f"Unsupported image mode '{mode}' for {tiff_path}, assuming 8-bit",
        "warning",
    )
    return 8


def convert_tiff_to_png(tiff_path, png_path, log_callback=None):
    """
    Convert a single TIFF image to PNG format.

    Preserves bit depth (8-bit or 16-bit) and directory structure.
    """
    try:
        with Image.open(tiff_path) as img:
            width, height = img.size
            mode = img.mode
            bit_depth = _get_bit_depth(img, tiff_path, log_callback=log_callback)

            _emit_log(
                log_callback,
                f"Processing: {tiff_path} ({width}x{height}, {mode}, {bit_depth}-bit)",
            )

            os.makedirs(os.path.dirname(png_path), exist_ok=True)
            img.save(png_path, "PNG")

            _emit_log(log_callback, f"Converted: {png_path}", "success")
            return True
    except Exception as exc:
        _emit_log(log_callback, f"Failed to convert {tiff_path}: {exc}", "error")
        return False


def process_directory(input_dir, output_dir, progress_callback=None, log_callback=None):
    """
    Recursively process all TIFF files in the input directory.

    Converts them to PNG while preserving directory structure.
    """
    tiff_paths = []
    for root, _, files in os.walk(input_dir):
        for file in files:
            if is_tiff_file(file):
                tiff_paths.append(os.path.join(root, file))

    converted_count = 0
    failed_count = 0
    total = len(tiff_paths)

    for index, tiff_path in enumerate(sorted(tiff_paths), start=1):
        rel_path = os.path.relpath(tiff_path, input_dir)
        png_rel_path = os.path.splitext(rel_path)[0] + ".png"
        png_path = os.path.join(output_dir, png_rel_path)

        if progress_callback is not None:
            progress_callback(
                {
                    "current": index,
                    "total": total,
                    "file": rel_path,
                    "output": png_rel_path,
                }
            )

        if convert_tiff_to_png(tiff_path, png_path, log_callback=log_callback):
            converted_count += 1
        else:
            failed_count += 1

    return converted_count, failed_count, total


def convert_zip(
    input_zip, output_dir="lumen_output", progress_callback=None, log_callback=None
):
    """
    Convert all TIFF images from a ZIP archive to PNG files.

    Returns a structured result suitable for CLI or GUI callers.
    """
    validate_zip(input_zip)

    if os.path.exists(output_dir):
        _emit_log(
            log_callback,
            f"Output directory '{output_dir}' already exists, files may be overwritten",
            "warning",
        )
    else:
        os.makedirs(output_dir)
        _emit_log(log_callback, f"Created output directory: {output_dir}")

    with tempfile.TemporaryDirectory() as temp_dir:
        _emit_log(log_callback, f"Using temporary directory: {temp_dir}")

        extract_zip(input_zip, temp_dir)
        _emit_log(log_callback, f"Extracted ZIP archive to: {temp_dir}")

        converted, failed, total = process_directory(
            temp_dir,
            output_dir,
            progress_callback=progress_callback,
            log_callback=log_callback,
        )

    result = {
        "converted": converted,
        "failed": failed,
        "total": total,
        "output_dir": output_dir,
        "errors": [],
    }

    if total == 0:
        _emit_log(log_callback, "No TIFF files were found in the ZIP archive.", "warning")
    else:
        _emit_log(
            log_callback,
            f"Conversion complete: {converted} successful, {failed} failed",
        )

    if failed > 0:
        result["errors"].append(f"{failed} file(s) failed to convert")

    return result
