; Inno Setup script: wraps dist\YT Downloader.exe (built by
; packaging/windows.spec) into a real Windows installer with a Next/Next/
; Finish wizard, Start Menu + optional Desktop shortcut, and an uninstaller
; entry in "Add or Remove Programs". Compiled by scripts\build_windows.bat
; via ISCC.exe (Inno Setup 6, https://jrsoftware.org/isdl.php).
;
; ffmpeg is bundled into the .exe itself (see windows.spec), so this
; installer needs no separate ffmpeg step -- just Next, Next, Install, Finish.

#define MyAppName "YT Downloader"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "YT Downloader Desktop"
#define MyAppExeName "YT Downloader.exe"

[Setup]
AppId={{B7E6B6C0-6B1B-4E8B-9D1E-3B4E7E6E8C11}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
; Per-user install by default -- no admin/UAC prompt needed. Users who want
; a machine-wide install can still elevate via the "Show details" link.
DefaultDirName={autopf}\{#MyAppName}
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
DisableProgramGroupPage=yes
OutputDir=..\dist\installer
OutputBaseFilename=YT-Downloader-Setup
SetupIconFile=..\app\resources\icon.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
Source: "..\dist\YT Downloader.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
