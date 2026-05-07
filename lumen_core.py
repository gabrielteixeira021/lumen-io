import os
import logging
import tempfile
import zipfile

from PIL import Image


class LumenError(Exception):
    pass

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
        logger.info(f"Extracted ZIP archive to: {extract_dir}")
        return True
    except Exception as e:
        logger.error(f"Failed to extract ZIP archive: {e}")
        return False


def is_tiff_file(filename):
    """Check if a file is a TIFF image based on extension."""
    return filename.lower().endswith((".tif", ".tiff"))


def convert_tiff_to_png(tiff_path, png_path):
    """
    Convert a single TIFF image to PNG format.

    Preserves bit depth (8-bit or 16-bit) and directory structure.
    """
    try:
        # Open the TIFF image
        with Image.open(tiff_path) as img:
            # Get image info for logging
            width, height = img.size
            mode = img.mode

            # Determine bit depth from mode
            bit_depth = None
            if mode in ("L", "P"):
                bit_depth = 8
            elif mode == "I;16":  # 16-bit grayscale
                bit_depth = 16
            elif mode == "RGB":
                # Check if it's 16-bit per channel (48-bit total)
                if img.getbands() and len(img.getbands()) == 3:
                    # Try to get bit depth from first band
                    band = (
                        img.getchannel(0)
                        if hasattr(img, "getchannel")
                        else img.split()[0]
                    )
                    if band.mode == "I;16":
                        bit_depth = 16
                    else:
                        bit_depth = 8
                else:
                    bit_depth = 8
            elif mode == "RGBA":
                bit_depth = 8  # Typically 8-bit per channel
            else:
                # For other modes, assume 8-bit but log warning
                logger.warning(
                    f"Unsupported image mode '{mode}' for {tiff_path}, assuming 8-bit"
                )
                bit_depth = 8

            logger.info(
                f"Processing: {tiff_path} ({width}x{height}, {mode}, {bit_depth}-bit)"
            )

            # Ensure output directory exists
            os.makedirs(os.path.dirname(png_path), exist_ok=True)

            # Save as PNG (lossless)
            img.save(png_path, "PNG")

            logger.success(f"Converted: {png_path}")
            return True

    except Exception as e:
        logger.error(f"Failed to convert {tiff_path}: {e}")
        return False


def process_directory(input_dir, output_dir):
    """
    Recursively process all TIFF files in the input directory.

    Converts them to PNG while preserving directory structure.
    """
    converted_count = 0
    failed_count = 0

    for root, _, files in os.walk(input_dir):
        for file in files:
            if is_tiff_file(file):
                tiff_path = os.path.join(root, file)

                # Calculate relative path from input directory
                rel_path = os.path.relpath(tiff_path, input_dir)
                # Change extension to .png
                png_rel_path = os.path.splitext(rel_path)[0] + ".png"
                png_path = os.path.join(output_dir, png_rel_path)

                if convert_tiff_to_png(tiff_path, png_path):
                    converted_count += 1
                else:
                    failed_count += 1

    return converted_count, failed_count

def convert_zip(input_zip, output_zip="lumen_output", progress_callback=None, log_callback=None):
    """
    Converte um arquivo zip cheio de imagens .tif ou .tiff em png e move para uma pasta
    """

    try:
