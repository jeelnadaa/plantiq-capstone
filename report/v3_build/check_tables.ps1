# Reports, for every table in the body, the page it starts and ends on (to prove no table is split).
param([string]$Docx = (Resolve-Path "..\Team_35_report_v3.docx").Path)
$word = New-Object -ComObject Word.Application
$word.Visible = $false
try {
  $d = $word.Documents.Open($Docx, $false, $true)
  $d.Repaginate()
  $i = 0
  foreach ($t in $d.Tables) {
    $i++
    $s = $t.Range.Characters.First.Information(3)
    $e = $t.Range.Characters.Last.Information(3)
    $prev = $t.Range.Previous(4,1)   # previous paragraph (caption)
    $cp = if ($prev) { $prev.Information(3) } else { $s }
    $txt = if ($prev) { $prev.Text.Trim() } else { "" }
    if ($txt.Length -gt 60) { $txt = $txt.Substring(0,60) }
    "{0}`t{1}`t{2}`t{3}`t{4}" -f $i, $cp, $s, $e, $txt
  }
  $d.Close($false)
} finally { $word.Quit() }
