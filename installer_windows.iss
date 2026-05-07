[Setup]
AppName=Lumen Converter
AppVersion=1.0.0
DefaultDirName={autopf}\LumenConverter
DefaultGroupName=Lumen Converter
OutputDir=dist_installer
OutputBaseFilename=LumenConverter-Setup-Windows-x64
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Files]
Source: "dist\LumenConverter-Windows-x64.exe"; DestDir: "{app}"; DestName: "LumenConverter.exe"; Flags: ignoreversion

[Icons]
Name: "{group}\Lumen Converter"; Filename: "{app}\LumenConverter.exe"
Name: "{group}\Desinstalar Lumen Converter"; Filename: "{uninstallexe}"
Name: "{autodesktop}\Lumen Converter"; Filename: "{app}\LumenConverter.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Criar atalho na area de trabalho"; GroupDescription: "Atalhos adicionais:"

[Run]
Filename: "{app}\LumenConverter.exe"; Description: "Executar Lumen Converter"; Flags: nowait postinstall skipifsilent
