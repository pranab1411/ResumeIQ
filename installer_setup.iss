; Script generated for Inno Setup - ResumeIQ Automated Installer
#define MyAppName "ResumeIQ"
#define MyAppVersion "1.5.0"
#define MyAppPublisher "ResumeIQ AI Systems"
#define MyAppURL "https://github.com/ResumeIQ"
#define MyAppExeName "ResumeIQ.exe"

[Setup]
AppId={{8E44F491-4D6C-4A2D-A491-04D4A180E2B9}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputBaseFilename=ResumeIQ_Setup_v1.5.0
SetupIconFile=assets\app_icon.ico
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
UninstallDisplayIcon={app}\{#MyAppExeName}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "assets\*"; DestDir: "{app}\assets"; Flags: ignoreversion recursesubdirs createallsubdirs

[Dirs]
Name: "{app}\database"; Permissions: users-full
Name: "{app}\reports"; Permissions: users-full
Name: "{app}\resumes"; Permissions: users-full

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Code]
function IsVCRedistInstalled: Boolean;
var
  Installed: Cardinal;
begin
  Result := RegQueryDWordValue(HKLM, 'SOFTWARE\Microsoft\VisualStudio\14.0\VC\Runtimes\x64', 'Installed', Installed) and (Installed = 1);
  if not Result then
  begin
    Result := RegQueryDWordValue(HKLM32, 'SOFTWARE\Microsoft\VisualStudio\14.0\VC\Runtimes\x64', 'Installed', Installed) and (Installed = 1);
  end;
end;

procedure InitializeWizard;
var
  ResultCode: Integer;
  VCRedistURL, TempPath: String;
begin
  if not IsVCRedistInstalled then
  begin
    if MsgBox('Visual C++ 2015-2022 Redistributable is required by spaCy and PyQt6, but is missing on your system.' + #13#10 + #13#10 +
              'Would you like setup to automatically download and install it now?', mbConfirmation, MB_YESNO) = IDYES then
    begin
      VCRedistURL := 'https://aka.ms/vs/17/release/vc_redist.x64.exe';
      TempPath := ExpandConstant('{tmp}\vc_redist.x64.exe');
      
      Exec('powershell.exe', '-NoProfile -ExecutionPolicy Bypass -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; (New-Object System.Net.WebClient).DownloadFile(''' + VCRedistURL + ''', ''' + TempPath + ''')"', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
      
      if FileExists(TempPath) then
      begin
        Exec(TempPath, '/passive /norestart', '', SW_SHOW, ewWaitUntilTerminated, ResultCode);
      end;
    end;
  end;
end;
