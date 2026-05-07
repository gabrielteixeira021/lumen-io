#!/usr/bin/env python3
"""
Lumen CLI Tool - Convert TIFF images to PNG format
"""

import logging
import os
import sys
import tempfile
import zipfile

# Setup logging format
logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


# Add success method to logger
def success(self, message, *args, **kwargs):
    if self.isEnabledFor(logging.INFO):
        self._log(logging.INFO, message, args, **kwargs)


logging.Logger.success = success


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
        logger.warning(
            f"Output directory '{output_dir}' already exists, files may be overwritten"
        )
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
            logger.success(
                f"All {converted} images converted successfully to {output_dir}/"
            )


if __name__ == "__main__":
    # Add success method to logger
    def success(self, message, *args, **kwargs):
        if self.isEnabledFor(logging.INFO):
            self._log(logging.INFO, message, args, **kwargs)

    logging.Logger.success = success

    main()
