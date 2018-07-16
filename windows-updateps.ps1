param (
    [string]$UserName = 'Administrator',
    [string]$Password = ('')
)

# Set up auto-logon
$resumed = 0
$auditing = 0
if ((Get-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Setup\State").ImageState -ne "IMAGE_STATE_COMPLETE") {
    $auditing = 1
}

if(-not $auditing) {
    if ((Get-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\winlogon").AutoAdminLogon -ne 1) {
        Write-Host "Setting auto-login & scheduling script auto-run..."
        $result = New-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\winlogon" -name AutoAdminLogon -value 1 -PropertyType "DWord" -Force
        $result = New-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\winlogon" -name DefaultUserName -value $UserName -Force
        $result = New-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\winlogon" -name DefaultPassword -value $Password -Force
        &schtasks /Create /TN "Windows-Update-Script" /RU `""$UserName"`" /SC ONLOGON /TR "powershell.exe -NoLogo -ExecutionPolicy ByPass -File ""$PSCommandPath"" -UserName ""$UserName"" -Password ""$Password""" /IT /F /RL HIGHEST
    } else {
        Write-Host "Resuming previous Windows-Update session..."
        $resumed = 1
        &timeout 30
    }
}

# Define update criteria.
$BaseCriteria = "IsInstalled=0 and IsHidden=0 and AutoSelectOnWebSites=1"

Function InstallUpdates($Criteria, $Name) {
    # Search for relevant updates.
    Write-Host "Searching for updates: $Name"
    $Searcher = New-Object -ComObject Microsoft.Update.Searcher
    $SearchResult = $Searcher.Search($Criteria).Updates

    if($SearchResult.Count) {
        # Download updates.
        Write-Host "Downloading" $SearchResult.Count "Updates..."
        $Session = New-Object -ComObject Microsoft.Update.Session
        $Downloader = $Session.CreateUpdateDownloader()
        $Downloader.Updates = $SearchResult
        $Downloader.Download()

        # Install updates.
        Write-Host "Installing" $SearchResult.Count "Updates..."
        $i = 0
        foreach($Result in $SearchResult) {
            $i++
            Write-Host "  $($i):" $Result.Title
            $Result.AcceptEULA()
        }
        Write-Host ""
        $Installer = New-Object -ComObject Microsoft.Update.Installer
        $Installer.Updates = $SearchResult
        $Result = $Installer.Install()

        # Reboot if required by updates.
        if($Result.rebootRequired) {
            Write-Host "Reboot is required..."
            shutdown.exe /t 5 /r
            exit
        }
    }
}

# First try Service Packs
$Result = InstallUpdates "$BaseCriteria and CategoryIDs contains '68C5B0A3-D1A6-4553-AE49-01D3A7827828'" "Service Packs"
$Result = InstallUpdates "$BaseCriteria and CategoryIDs contains '28BC880E-0592-4CBF-8F95-C79B17911D5F'" "Update Rollups"
$Result = InstallUpdates "$BaseCriteria and CategoryIDs contains 'E6CF1350-C01B-414D-A61F-263D14D133B4'" "Critical Updates"
$Result = InstallUpdates "$BaseCriteria and CategoryIDs contains '0FA1201D-4330-4FA8-8AE9-B877473B6441'" "Security Updates"
$Result = InstallUpdates "$BaseCriteria and CategoryIDs contains 'E0789628-CE08-4437-BE74-2495B842F43B'" "Definition Updates"
$Result = InstallUpdates "$BaseCriteria and CategoryIDs contains '5C9376AB-8CE6-464A-B136-22113DD69801'" "Application"

Write-Host "All Updates Installed!"
Write-Host ""

# If we made it to here, everything is good, so we can turn off auto-logon
if(-not $auditing) {
    Write-Host "Stopping auto-login & script auto-run..."
    Remove-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\winlogon" -name AutoAdminLogon
    Remove-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\winlogon" -name DefaultUserName
    Remove-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\winlogon" -name DefaultPassword
    &schtasks /Delete /TN "Windows-Update-Script" /F
}
if($resumed) { Pause }

