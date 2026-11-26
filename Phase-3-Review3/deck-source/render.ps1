param([string]$deck, [string]$out)
New-Item -ItemType Directory -Force $out | Out-Null
Get-ChildItem $out -Filter *.png | Remove-Item -Confirm:$false
$pp = New-Object -ComObject PowerPoint.Application
$pres = $pp.Presentations.Open($deck, $true, $false, $false)
$i = 0
foreach ($s in $pres.Slides) { $i++; $s.Export("$out\s$('{0:D2}' -f $i).png", "PNG", 1600, 900) }
$pres.Close()
$pp.Quit()
"exported $i slides"
