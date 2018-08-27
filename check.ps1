$arrService = Get-Service -Name AmazonCloudWatchAgent

while ($arrService.Status -ne 'Running')
{

    Start-Service $ServiceName
    write-host $arrService.status
    write-host 'Service starting'
    Start-Sleep -seconds 60
    $arrService.Refresh()
    if ($arrService.Status -eq 'Running')
    {
        Write-Host 'Service is now Running'
    }

}
#https://stackoverflow.com/questions/40658251/why-are-cloudwatch-logs-sent-from-my-windows-ec2-instance-not-showing-up-on-aws
#https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_use_switch-role-ec2_instance-profiles.html
#https://docs.aws.amazon.com/cli/latest/reference/iam/add-role-to-instance-profile.html
