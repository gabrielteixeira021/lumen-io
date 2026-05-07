#!/usr/bin/env python3
"""
Lumen CLI Tool - Convert TIFF images to PNG format
"""

import logging
import sys

from lumen_core import LumenError, convert_zip


logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


def log_to_cli(level, message):
    """Bridge core log events to CLI logging."""
    log_method = getattr(logger, level, logger.info)
    log_method(message)


def main():
    """Main entry point for the CLI tool."""
    if len(sys.argv) != 2:
        logger.error("Usage: lumen.py <input.zip>")
        logger.error("Example: lumen.py images.zip")
        return 1

    input_zip = sys.argv[1]

    logger.info("Starting Lumen TIFF to PNG converter")
    logger.info(f"Input file: {input_zip}")

    try:
        result = convert_zip(input_zip, log_callback=log_to_cli)
    except LumenError as exc:
        logger.error(str(exc))
        return 1

    if result["failed"] > 0:
        logger.warning(f"{result['failed']} files failed to convert")
        return 1

    logger.info(
        f"All {result['converted']} images converted successfully to "
        f"{result['output_dir']}/"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
