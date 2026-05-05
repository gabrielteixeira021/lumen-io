# Lumen CLI Tool

A robust, production-ready CLI tool that converts TIFF images (including 8-bit and 16-bit) into lossless PNG format while preserving pixel integrity for downstream AI classification tasks.

## Features

- **Input**: Accepts a `.zip` file containing one or more `.tif` or `.tiff` images (supports nested directories)
- **Output**: Creates a `lumen_output/` folder with all images converted to `.png`, preserving directory structure
- **Validation**: Checks for valid ZIP file and handles corrupted/unsuported files gracefully
- **Conversion**: 
  - Recursively locates all TIFF files
  - Detects bit depth (8-bit or 16-bit) and preserves it in PNG output
  - Uses Pillow (PIL) with correct mode handling for lossless conversion
  - Preserves essential metadata when possible
- **CLI UX**: 
  - Clear logs with levels: `[INFO]`, `[SUCCESS]`, `[ERROR]`
  - Accepts input file as CLI argument
- **Cross-platform**: Provides execution scripts for Linux/macOS (`lumen.sh`) and Windows (`lumen.bat`)

## Installation

1. **Prerequisites**: Python 3.10+ must be installed and available in your PATH.

2. **Clone or download** this repository to your local machine.

3. **Install dependencies**:
   ```bash
   # Create and activate virtual environment (recommended)
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```
   
   Alternatively, the provided execution scripts (`lumen.sh` or `lumen.bat`) will automatically create and use a virtual environment if one doesn't exist, or use an existing one.

## Usage

### Via Execution Scripts (Recommended)

**Linux/macOS**:
```bash
./lumen.sh /path/to/input.zip
```

**Windows**:
```cmd
lumen.bat C:\path\to\input.zip
```

### Direct Python Execution

```bash
python3 lumen.py /path/to/input.zip
```

### Example

```bash
# Convert images in sample_images.zip
./lumen.sh sample_images.zip
```

After execution, you will find the converted PNG images in the `lumen_output/` directory, preserving the original directory structure.

## Output

- All TIFF images are converted to PNG format losslessly.
- The `lumen_output/` directory mirrors the directory structure of the extracted ZIP.
- Each `.tif` or `.tiff` file is converted to a `.png` file with the same base name.

## Logging

The tool provides clear console output with the following log levels:
- `[INFO]`: General information about the process
- `[SUCCESS]`: Successful operations (e.g., file conversion)
- `[ERROR]`: Errors that halt processing

## Design Decisions & Limitations

1. **Bit Depth Handling**: 
   - The tool detects 8-bit and 16-bit grayscale images (mode `L` and `I;16`) and RGB images.
   - For RGB images, it attempts to determine if they are 16-bit per channel (48-bit total) by checking the bands.
   - Other color modes (e.g., CMYK, LAB) are treated as 8-bit and converted accordingly, with a warning logged.

2. **Lossless Conversion**: 
   - PNG format is used for lossless compression.
   - Pillow's `save` method with `'PNG'` format ensures no loss of pixel data.

3. **Metadata**: 
   - While Pillow does preserve some metadata when saving PNG, the primary focus is on pixel integrity.
   - For maximum metadata preservation, consider using specialized libraries (not required for AI classification tasks).

4. **Temporary Files**: 
   - The tool uses a temporary directory for extraction and automatically cleans up after execution.

5. **Error Handling**:
   - Validates ZIP file before extraction.
   - Handles corrupted images gracefully by logging errors and continuing with other files.
   - Reports summary of successful and failed conversions.

## Dependencies

- **Pillow**: Python Imaging Library (Fork) for image processing.
  - Specified in `requirements.txt` as `Pillow>=9.0.0`

## Contributing

1. Fork the repository.
2. Create a feature branch.
3. Commit your changes.
4. Push to the branch.
5. Open a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
