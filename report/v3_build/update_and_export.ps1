# Opens the built report in Word, refreshes every field (PAGEREF page numbers, PAGE), saves, exports the PDF.
param([string]$Docx = (Resolve-Path "..\Team_35_report_v3.docx").Path)
$pdf = [System.IO.Path]::ChangeExtension($Docx, ".pdf")
$word = New-Object -ComObject Word.Application
$word.Visible = $false
$word.DisplayAlerts = 0
try {
    $d = $word.Documents.Open($Docx)
    $d.Repaginate()
    for ($k = 0; $k -lt 2; $k++) {
        foreach ($story in $d.StoryRanges) { [void]$story.Fields.Update() }
        $d.Repaginate()
    }
    $d.Save()
    $d.ExportAsFixedFormat($pdf, 17)   # wdExportFormatPDF
    "pages: " + $d.ComputeStatistics(2)
    $d.Close()
} finally {
    $word.Quit()
}
"exported $pdf"
