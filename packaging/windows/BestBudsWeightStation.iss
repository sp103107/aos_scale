; Best Buds Cultivator Weight Station — Inno Setup 6 script
; Per-user install (no admin). Build via packaging/windows/build_windows.ps1

#define MyAppName "Best Buds Cultivator Weight Station"
#ifndef MyAppVersion
  #define MyAppVersion "2.0.0-rc6"
#endif
#define MyAppPublisher "Best Buds / Avarachi Ventures"
#define MyAppURL "https://github.com/sp103107/aos_scale"
#define MyAppExeName "BestBudsWeightStation.exe"
; Windows VersionInfo requires numeric a.b.c.d — strip any -rcN/-aN prerelease suffix.
#define DashPos Pos("-", MyAppVersion)
#if DashPos > 0
  #define MyAppNumericVersion Copy(MyAppVersion, 1, DashPos - 1) + ".0"
#else
  #define MyAppNumericVersion MyAppVersion + ".0"
#endif

[Setup]
AppId={{A8F3C2E1-9B47-4D6A-8E15-2C91F0A47B3D}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={localappdata}\BestBudsWeightStation\app
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
LicenseFile=..\..\LICENSE
InfoBeforeFile=..\..\COMMERCIAL.md
OutputDir=..\..\dist\windows
OutputBaseFilename=BestBudsWeightStation-Setup-v{#MyAppVersion}
SetupIconFile=
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
UninstallDisplayName={#MyAppName}
VersionInfoVersion={#MyAppNumericVersion}
VersionInfoCompany={#MyAppPublisher}
VersionInfoProductName={#MyAppName}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "..\..\dist\BestBudsWeightStation\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Code]
function InitializeUninstall(): Boolean;
begin
  Result := True;
  MsgBox('Application files will be removed. Run data under %LOCALAPPDATA%\BestBudsWeightStation\runs is preserved.', mbInformation, MB_OK);
end;
