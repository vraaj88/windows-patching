param (
    [string]$UserName = $('$LocalAdm'),
    [string]$Password = $('$LocalAdmPwd'),
    [string]$Result = $('$Results')
)

# Set up auto-logon
$resumed = 0
$auditing = 0
if ((Get-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Setup\State").ImageState -ne "IMAGE_STATE_COMPLETE") {
    $auditing = 1
}

if(-not $auditing) {
    if ((Get-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\winlogon").AutoAdminLogon -ne 1) {
        #Write-Host "Setting auto-login & scheduling script auto-run..."
        $result = New-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\winlogon" -name AutoAdminLogon -value 1 -PropertyType "DWord" -Force
        $result = New-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\winlogon" -name DefaultUserName -value $UserName -Force
        $result = New-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\winlogon" -name DefaultPassword -value $Password -Force
        &schtasks /Create /TN "Windows-Update-Script" /RU `""$UserName"`" /SC ONLOGON /TR "powershell.exe -NoLogo -ExecutionPolicy ByPass -File ""$PSCommandPath"" -UserName ""$UserName"" -Password ""$Password""" /IT /F /RL HIGHEST
    } else {
        #Write-Host "Resuming previous Windows-Update session..."
        $resumed = 1
        &timeout 30
    }
}

# Define update criteria.
$BaseCriteria = "IsInstalled=0 and IsHidden=0 and AutoSelectOnWebSites=1"

Function InstallUpdates($Criteria, $Name) {
    # Search for relevant updates.
    #Write-Host "Searching for updates: $Name"
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
        #Write-Host "Installing" $SearchResult.Count "Updates..."
        $i = 0
        foreach($Result in $SearchResult) {
            $i++
            #Write-Host "  $($i):" $Result.Title
            $Result.AcceptEULA()
        }
        #Write-Host ""
        $Installer = New-Object -ComObject Microsoft.Update.Installer
        $Installer.Updates = $SearchResult
        $Result = $Installer.Install()

        # Reboot if required by updates.
        if($Result.rebootRequired) {
            #Write-Host "Reboot is required..."
            shutdown.exe /t 5 /r
            exit
        }
    }
}

# First try Service Packs


#Write-Host "All Updates Installed!"
#Write-Host ""

$retObj = [ordered]@{}
$retObj.foundupdates =  "$SearchResult"
$retObj.installed =  "$Installer"
New-Object -TypeName PSObject -Property $retObj | ConvertTo-Json 
Write-Host "$retObj"



# If we made it to here, everything is good, so we can turn off auto-logon
if(-not $auditing) {
    Write-Host "Stopping auto-login & script auto-run..."
    Remove-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\winlogon" -name AutoAdminLogon
    Remove-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\winlogon" -name DefaultUserName
    Remove-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\winlogon" -name DefaultPassword
    &schtasks /Delete /TN "Windows-Update-Script" /F
}
if($resumed) { Pause }

