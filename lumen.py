#!/usr/bin/env python3
"""
Lumen CLI Tool - Convert TIFF images to PNG format
"""

import sys
import os
import zipfile
import tempfile
import shutil
from pathlib import Path
from PIL import Image
import logging

# Setup logging format
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Add success method to logger
def success(self, message, *args, **kwargs):
    if self.isEnabledFor(logging.INFO):
        self._log(logging.INFO, message, args, **kwargs)
logging.Logger.success = success

def validate_zip(file_path):
    """Validate that the input file exists and is a valid ZIP archive."""
    if not os.path.exists(file_path):
        logger.error(f"Input file does not exist: {file_path}")
        return False
    
    if not zipfile.is_zipfile(file_path):
        logger.error(f"File is not a valid ZIP archive: {file_path}")
        return False
    
    return True

def extract_zip(zip_path, extract_dir):
    """Extract ZIP archive to the specified directory."""
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        logger.info(f"Extracted ZIP archive to: {extract_dir}")
        return True
    except Exception as e:
        logger.error(f"Failed to extract ZIP archive: {e}")
        return False

def is_tiff_file(filename):
    """Check if a file is a TIFF image based on extension."""
    return filename.lower().endswith(('.tif', '.tiff'))

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
            if mode in ('L', 'P'):
                bit_depth = 8
            elif mode == 'I;16':  # 16-bit grayscale
                bit_depth = 16
            elif mode == 'RGB':
                # Check if it's 16-bit per channel (48-bit total)
                if img.getbands() and len(img.getbands()) == 3:
                    # Try to get bit depth from first band
                    band = img.getchannel(0) if hasattr(img, 'getchannel') else img.split()[0]
                    if band.mode == 'I;16':
                        bit_depth = 16
                    else:
                        bit_depth = 8
                else:
                    bit_depth = 8
            elif mode == 'RGBA':
                bit_depth = 8  # Typically 8-bit per channel
            else:
                # For other modes, assume 8-bit but log warning
                logger.warning(f"Unsupported image mode '{mode}' for {tiff_path}, assuming 8-bit")
                bit_depth = 8
            
            logger.info(f"Processing: {tiff_path} ({width}x{height}, {mode}, {bit_depth}-bit)")
            
            # Ensure output directory exists
            os.makedirs(os.path.dirname(png_path), exist_ok=True)
            
            # Save as PNG (lossless)
            img.save(png_path, 'PNG')
            
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
                png_rel_path = os.path.splitext(rel_path)[0] + '.png'
                png_path = os.path.join(output_dir, png_rel_path)
                
                if convert_tiff_to_png(tiff_path, png_path):
                    converted_count += 1
                else:
                    failed_count += 1
    
    return converted_count, failed_count

def main():
    """Main entry point for the CLI tool."""
    if len(sys.argv) != 2:
        logger.error("Usage: lumen.py <input.zip>")
        logger.error("Example: lumen.py images.zip")
        sys.exit(1)
    
    input_zip = sys.argv[1]
    
    logger.info("Starting Lumen TIFF to PNG converter")
    logger.info(f"Input file: {input_zip}")
    
    # Validate input
    if not validate_zip(input_zip):
        sys.exit(1)
    
    # Create output directory
    output_dir = "lumen_output"
    if os.path.exists(output_dir):
        logger.warning(f"Output directory '{output_dir}' already exists, files may be overwritten")
    else:
        os.makedirs(output_dir)
        logger.info(f"Created output directory: {output_dir}")
    
    # Process in temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        logger.info(f"Using temporary directory: {temp_dir}")
        
        # Extract ZIP
        if not extract_zip(input_zip, temp_dir):
            sys.exit(1)
        
        # Process images
        converted, failed = process_directory(temp_dir, output_dir)
        
        # Summary
        logger.info(f"Conversion complete: {converted} successful, {failed} failed")
        
        if failed > 0:
            logger.warning(f"{failed} files failed to convert")
            sys.exit(1)
        else:
            logger.success(f"All {converted} images converted successfully to {output_dir}/")

if __name__ == "__main__":
    # Add success method to logger
    def success(self, message, *args, **kwargs):
        if self.isEnabledFor(logging.INFO):
            self._log(logging.INFO, message, args, **kwargs)
    logging.Logger.success = success
    
    main()