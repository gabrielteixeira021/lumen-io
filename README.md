# Lumen Desktop Application

Aplicacao desktop e CLI para converter imagens TIFF dentro de um arquivo `.zip` para PNG sem perdas, preservando a estrutura de diretorios para uso posterior em pipelines de classificacao.

## Features

- **Input**: Accepts a `.zip` file containing one or more `.tif` or `.tiff` images (supports nested directories)
- **Output**: Creates a `lumen_output/` folder with all images converted to `.png`, preserving directory structure
- **Validation**: Checks for valid ZIP file and handles corrupted/unsuported files gracefully
- **Conversion**: 
  - Recursively locates all TIFF files
  - Detects bit depth (8-bit or 16-bit) and preserves it in PNG output
  - Uses Pillow (PIL) with correct mode handling for lossless conversion
  - Preserves essential metadata when possible
- **User Interface**: 
  - Intuitive Graphical User Interface (GUI) for easy file selection and conversion.
  - Displays conversion progress and logs with levels: `[INFO]`, `[SUCCESS]`, `[ERROR]`.
- **Cross-platform**: Desktop application available for Linux, macOS, and Windows.

## Requisitos

- Python 3.10+
- `pip`
- Para build: dependencias de `requirements-build.txt`
- Para release no GitHub: `gh` autenticado
- Para build Windows no Linux: `wine`

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

No Windows:

```bat
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Rodando a aplicacao

### Interface grafica

Depois de ativar o ambiente virtual:

```bash
python app_launcher.py
```

ou:

```bash
python -m app.gui
```

Fluxo basico:

1. Selecione um arquivo `.zip` com arquivos `.tif` ou `.tiff`
2. Escolha a pasta de saida
3. Clique em `Converter`
4. Ao final, use o botao `Abrir pasta de saida`

### CLI

Se quiser executar sem interface:

```bash
python lumen.py caminho/para/imagens.zip
```

O resultado sera salvo por padrao em `lumen_output/`.

## Testes

Para rodar os testes unitarios:

```bash
python -m unittest tests/test_lumen.py
```

## Build Linux

Instale as dependencias de build:

```bash
pip install -r requirements-build.txt
```

### Build one-dir

```bash
python build.py
```

Saida esperada:

- `dist/LumenConverter/`

### Build one-file

```bash
python release_build.py
```

Saida esperada:

- `dist/LumenConverter-Linux-x64`

Observacao:

- Depois de alterar codigo da GUI, voce precisa rebuildar o executavel para testar o comportamento no binario empacotado.

## Build Windows no proprio Windows

Se voce estiver no Windows, o fluxo de release ja tenta gerar o instalador automaticamente via Inno Setup.

Pre-requisitos:

- Python com dependencias de `requirements.txt` e `requirements-build.txt`
- `ISCC` do Inno Setup no `PATH`
- `gh` autenticado
- repositorio git com remoto `origin` via SSH

Gerando apenas o executavel:

```bat
python release_build.py
```

Gerando release completa:

```bash
./make_release.sh v1.0.0
```

Esse fluxo:

1. Gera `dist/LumenConverter-Windows-x64.exe`
2. Executa `ISCC installer_windows.iss` no Windows
3. Procura automaticamente o instalador em `dist_installer/LumenConverter-Setup-Windows-x64.exe`
4. Publica os assets via `gh release`

## Windows Build from Linux with Wine

`PyInstaller` does not generate Windows binaries from a native Linux Python runtime. To produce `LumenConverter-Windows-x64.exe` on Linux, this repository now includes a Wine-based build flow that runs a real Windows Python inside an isolated Wine prefix.

### Prerequisites

- `wine`, `wineboot`, and `winepath` installed on Linux
- The Windows Python installer available at `python-3.10.0-amd64.exe` in the repository root
- Optional: Inno Setup 6 installed inside the same Wine prefix if you also want a `Setup` executable

### Build command

```bash
./build_windows_wine.sh
```

The script will:

1. Create an isolated Wine prefix at `.wine-lumen/`
2. Install Windows Python at `C:\python310`
3. Install `requirements.txt` and `requirements-build.txt`
4. Run `release_build.py` using the Windows Python interpreter
5. Try to compile `installer_windows.iss` if `ISCC.exe` is available in Wine

### Outputs

- Portable executable: `dist/LumenConverter-Windows-x64.exe`
- Installer, when Inno Setup is installed: `dist_installer/LumenConverter-Setup-Windows-x64.exe`

### Notes

- This flow avoids relying on your global `~/.wine`, which is a common source of broken `pip` and `PyInstaller` installations.
- If you keep the Python installer in another location, run with `PYTHON_INSTALLER=/path/to/python-3.10.0-amd64.exe ./build_windows_wine.sh`
- If Inno Setup is installed in another path inside Wine, run with `INNO_COMPILER_WINDOWS='C:\path\to\ISCC.exe' ./build_windows_wine.sh`

## Release

Para publicar uma release com assets:

```bash
./make_release.sh v1.0.0
```

O script chama `release_build.py`, tenta gerar instalador Windows quando estiver rodando no Windows, normaliza nomes de assets e publica via GitHub CLI.

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

## Dependencias

- **Pillow** para processamento de imagem
- **PySide6** para a interface grafica
- **PyInstaller** para empacotamento

## Contributing

1. Fork the repository.
2. Create a feature branch.
3. Commit your changes.
4. Push to the branch.
5. Open a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
