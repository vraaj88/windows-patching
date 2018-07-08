 param(
        [Parameter(Mandatory=$False)][ValidateSet("TEST","PROD",ignorecase=$True)][String] $AzureEnvironment = "TEST",
        [Parameter(Mandatory=$False)] [String] $OutputPath =$pwd
    )

$azrSubId = @{}
$azrSubId.test = "ec6c1802-b58d-4228-a71e-c47cbc64f715"
$azrSubId.prod = "84b4806d-9df2-40ee-8c6c-c499bd04180c"

try {
    $retval = Get-AzureRmSubscription -ErrorAction Stop
} catch {
    Login-AzureRmAccount
}
Select-AzureRmSubscription -Subscriptionid $azrSubId[$AzureEnvironment.ToLower()]

$grp0 = @()
$grp1 = @()
$grp2 = @()

$txt0 = "$($OutputPath)\patch-windows-2012-$($AzureEnvironment.ToLower())-grp0.txt"
$txt1 = "$($OutputPath)\patch-windows-2012-$($AzureEnvironment.ToLower())-grp1.txt"
$txt2 = "$($OutputPath)\patch-windows-2012-$($AzureEnvironment.ToLower())-grp2.txt"

if (Test-Path $txt0) { Remove-Item $txt0 -Force }
if (Test-Path $txt1) { Remove-Item $txt1 -Force }
if (Test-Path $txt2) { Remove-Item $txt2 -Force }

foreach ($vm in Get-AzureRmVM) {
    
    if (($vm.name -like '*pdw*') -or ($vm.name -like '*tsw*')) {
        switch (($vm.Name.Substring($vm.name.length - 3,3).toint32($null)) % 3) {
            0 {
                $grp0 +=  $vm.name
            }
            1 {
                $grp1 +=  $vm.name
            }
            2 {
                $grp2 +=  $vm.name
            }
        }
    }
}

foreach ($vmss in Get-AzureRmVmss) {

    for ($i=0; $i -lt $vmss.Sku.Capacity; $i++) {

        $vmssHost = "$($vmss.Name)$($i.ToString().PadLeft(6,"0"))"

        switch ($i % 3) {
            0 {
                $grp0 += $vmssHost
            }
            1 {
                $grp1 += $vmssHost
            }
            2 {
                $grp2 += $vmssHost
            }
        }

    }
}


$out  = "Group 0:`n"
$out += $($grp0 -join ',')
$out += "`nGroup 1:`n"
$out += $($grp1 -join ',')
$out += "`nGroup 2:`n"
$out += $($grp2 -join ',')

Out-File -FilePath $txt0 -Force -Encoding utf8 -InputObject ($grp0 -join ',')
Out-File -FilePath $txt1 -Force -Encoding utf8 -InputObject ($grp1 -join ',')
Out-File -FilePath $txt2 -Force -Encoding utf8 -InputObject ($grp2 -join ',')

return $out