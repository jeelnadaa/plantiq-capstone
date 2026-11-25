# For every heading bookmark (_toc_N) prints: N, start page, end page, start Y, end Y (points from page top), heading.
# A section runs from its heading to the last non-empty paragraph before the next heading; a paragraph that starts
# a new page (the next chapter's "CHAPTER N" line) is not part of the section.
param([string]$Docx)
$word = New-Object -ComObject Word.Application
$word.Visible = $false
try {
  $d = $word.Documents.Open($Docx, $false, $true)
  $d.Repaginate()
  $d.Bookmarks.ShowHidden = $true
  $bms = @()
  foreach ($b in $d.Bookmarks) { if ($b.Name -like '_toc_*') { $bms += ,@([int]$b.Name.Substring(5), $b.Range.Start) } }
  $bms = $bms | Sort-Object { $_[1] }
  $docEnd = $d.Content.End
  for ($i = 0; $i -lt $bms.Count; $i++) {
    $n = $bms[$i][0]; $s = $bms[$i][1]
    $e = if ($i + 1 -lt $bms.Count) { $bms[$i + 1][1] } else { $docEnd }
    $last = $null
    foreach ($p in $d.Range($s, $e).Paragraphs) {
      if ($p.Range.Start -lt $s) { continue }
      if ($p.Format.PageBreakBefore -and $p.Range.Start -gt $s) { break }
      if ($p.Range.Text.Trim().Length -gt 0 -or $p.Range.InlineShapes.Count -gt 0) { $last = $p }
    }
    $rs = $d.Range($s, $s)
    $re = $d.Range($last.Range.End - 1, $last.Range.End - 1)
    $t = $d.Range($s, [Math]::Min($s + 60, $e)).Text.Split("`r")[0]
    "{0}`t{1}`t{2}`t{3:F0}`t{4:F0}`t{5}" -f $n, $rs.Information(3), $re.Information(3), $rs.Information(6), $re.Information(6), $t
  }
  $d.Close($false)
} finally { $word.Quit() }
