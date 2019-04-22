; http://www.jrsoftware.org/ishelp/index.php

[Setup]
AppName="PyWinStartup"
AppVerName="PyWinStartup 0.1.0"
DefaultDirName="{pf}\PyWinStartup"
DefaultGroupName="PyWinStartup"
AppVersion="0.1.0"
AppCopyright="Taehong Kim"
AppPublisher="Taehong Kim"
UninstallDisplayIcon="{app}\PyWinStartup.exe"
Compression=lzma2/max
SolidCompression=yes
OutputDir="dist"
OutputBaseFilename="PyWinStartup-0.1.0-Setup"
; VersionInfoVersion="0.1.0"
VersionInfoProductVersion="0.1.0"
VersionInfoCompany="Taehong Kim"
VersionInfoCopyright="Taehong Kim"
ArchitecturesInstallIn64BitMode="x64"

[Files]
Source: "dist\*"; DestDir: "{app}"; Flags: recursesubdirs

[Icons]
Name: "{group}\PyWinStartup"; Filename: "{app}\PyWinStartup.exe"
Name: "{commondesktop}\PyWinStartup"; Filename: "{app}\PyWinStartup.exe"
