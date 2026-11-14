; Instalador de Windows. Lo compila el workflow con ISCC /DVersion=X.Y.Z-rcN tools\pelis.iss
; a partir de lo que dejó PyInstaller en build\dist\pelis (corré antes tools\build_win.bat).
#ifndef Version
  #define Version "0.0.0"
#endif

[Setup]
AppId={{381528D1-ECB9-415C-B1B5-EE4858E631C2}
AppName=Pelis
AppVersion={#Version}
AppPublisher=Pelis
; Por usuario y sin administrador, para que no pida UAC y la app pueda actualizarse sola
PrivilegesRequired=lowest
DefaultDirName={localappdata}\Programs\Pelis
DisableProgramGroupPage=yes
DisableDirPage=yes
OutputDir=..\dist
OutputBaseFilename=Pelis-windows-v{#Version}-setup
SetupIconFile=..\assets\icono.ico
UninstallDisplayIcon={app}\pelis.exe
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
CloseApplications=yes
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Files]
Source: "..\build\dist\pelis\*"; DestDir: "{app}"; Flags: recursesubdirs ignoreversion

[Icons]
Name: "{userprograms}\Pelis"; Filename: "{app}\pelis.exe"

[Run]
; En una actualización silenciosa abre la app el script de Pelis, que conserva sus argumentos
Filename: "{app}\pelis.exe"; Description: "Abrir Pelis"; Flags: nowait postinstall skipifsilent
