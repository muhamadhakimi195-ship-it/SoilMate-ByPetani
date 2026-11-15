param([string]$InputSvg = "$PSScriptRoot/01-system.svg", [string]$OutputPng = "$PSScriptRoot/01-system.png")
# Offline rendering using Windows drawing libraries; no browser is opened.
Add-Type -AssemblyName PresentationCore,PresentationFramework,WindowsBase
$culture = [Globalization.CultureInfo]::GetCultureInfo('en-US')
$visual = [System.Windows.Media.DrawingVisual]::new()
$dc = $visual.RenderOpen()
$scale = 1.5
$dc.PushTransform([System.Windows.Media.ScaleTransform]::new($scale,$scale))
[xml]$doc = Get-Content -LiteralPath $InputSvg -Raw
$diagramWidth = [double]$doc.DocumentElement.width
$diagramHeight = [double]$doc.DocumentElement.height
$script:overflow = [Collections.Generic.List[string]]::new()
function Brush([string]$s) {
    if (!$s -or $s -eq 'none') { return $null }
    return [System.Windows.Media.SolidColorBrush]::new([System.Windows.Media.ColorConverter]::ConvertFromString($s))
}
function Val($n,[string]$key,$fallback) {
    if ($n.HasAttribute($key)) { return $n.GetAttribute($key) }
    return $fallback
}
function DrawNode($n,$state) {
    if ($n.NodeType -ne [System.Xml.XmlNodeType]::Element) { return }
    if ($n.LocalName -in @('defs','style','title','desc','marker')) { return }
    $s = @{} + $state
    foreach ($k in @('fill','stroke','stroke-width','stroke-linecap','stroke-linejoin')) { if ($n.HasAttribute($k)) { $s[$k]=$n.GetAttribute($k) } }
    $push=0
    if ($n.HasAttribute('transform')) {
        $tr=$n.GetAttribute('transform')
        foreach($m in [regex]::Matches($tr,'(translate|scale)\(([^)]+)\)')) {
            $v=@($m.Groups[2].Value -split '[ ,]+' | Where-Object {$_} | ForEach-Object {[double]$_})
            if($m.Groups[1].Value -eq 'translate') { $dc.PushTransform([System.Windows.Media.TranslateTransform]::new($v[0],$(if($v.Count -gt 1){$v[1]}else{0}))) }
            else { $dc.PushTransform([System.Windows.Media.ScaleTransform]::new($v[0],$(if($v.Count -gt 1){$v[1]}else{$v[0]}))) }
            $push++
        }
    }
    $fill=Brush $s.fill
    $pen=$null
    if($s.stroke -and $s.stroke -ne 'none') {
        $pen=[System.Windows.Media.Pen]::new((Brush $s.stroke),[double]$s['stroke-width'])
        if ($s['stroke-linecap'] -eq 'round') { $pen.StartLineCap=[System.Windows.Media.PenLineCap]::Round; $pen.EndLineCap=[System.Windows.Media.PenLineCap]::Round }
        $pen.LineJoin=[System.Windows.Media.PenLineJoin]::Round
        if($n.HasAttribute('stroke-dasharray') -and $n.GetAttribute('stroke-dasharray') -ne 'none') {
            $dashes=[System.Windows.Media.DoubleCollection]::new()
            foreach($d in ($n.GetAttribute('stroke-dasharray') -split '[ ,]+')) { $dashes.Add([double]$d / $pen.Thickness) }
            $pen.DashStyle=[System.Windows.Media.DashStyle]::new($dashes,0)
        }
    }
    switch($n.LocalName) {
        'rect' {
            $r=[System.Windows.Rect]::new([double]$n.x,[double]$n.y,[double]$n.width,[double]$n.height)
            $rad=[double](Val $n 'rx' 0)
            $dc.DrawRoundedRectangle($fill,$pen,$r,$rad,$rad)
        }
        'path' {
            $g=[System.Windows.Media.Geometry]::Parse($n.d)
            $dc.DrawGeometry($fill,$pen,$g)
            if($n.HasAttribute('marker-end')) {
                $tokens=[regex]::Matches($n.d,'[A-Za-z]|-?\d+(?:\.\d+)?') | ForEach-Object {$_.Value}
                $x=0.;$y=0.;$prevx=0.;$prevy=0.;$cmd='';$idx=0
                while($idx -lt $tokens.Count) {
                    if($tokens[$idx] -match '^[A-Za-z]$'){$cmd=$tokens[$idx];$idx++;continue}
                    $prevx=$x;$prevy=$y
                    switch($cmd) { 'M' {$x=[double]$tokens[$idx];$y=[double]$tokens[$idx+1];$idx+=2} 'L' {$x=[double]$tokens[$idx];$y=[double]$tokens[$idx+1];$idx+=2} 'H' {$x=[double]$tokens[$idx];$idx++} 'V' {$y=[double]$tokens[$idx];$idx++} default {$idx++} }
                }
                if($y -gt $prevy) {$shape="M $($x-6),$($y-8) L $x,$($y+1) L $($x+6),$($y-8) Z"}
                elseif($y -lt $prevy) {$shape="M $($x-6),$($y+8) L $x,$($y-1) L $($x+6),$($y+8) Z"}
                elseif($x -lt $prevx) {$shape="M $($x+8),$($y-6) L $($x-1),$y L $($x+8),$($y+6) Z"}
                else {$shape="M $($x-8),$($y-6) L $($x+1),$y L $($x-8),$($y+6) Z"}
                $dc.DrawGeometry((Brush $s.stroke),$null,[System.Windows.Media.Geometry]::Parse($shape))
            }
        }
        'text' {
            $size=[double](Val $n 'font-size' 18)
            $weight=if([double](Val $n 'font-weight' 400) -ge 600){[System.Windows.FontWeights]::SemiBold}else{[System.Windows.FontWeights]::Normal}
            $face=[System.Windows.Media.Typeface]::new([System.Windows.Media.FontFamily]::new('Segoe UI'),[System.Windows.FontStyles]::Normal,$weight,[System.Windows.FontStretches]::Normal)
            $ft=[System.Windows.Media.FormattedText]::new($n.InnerText,$culture,[System.Windows.FlowDirection]::LeftToRight,$face,$size,$fill,1.0)
            $x=[double]$n.x;$y=[double]$n.y
            $anchor=Val $n 'text-anchor' 'start'
            if($anchor -eq 'middle'){$x-=$ft.Width/2} elseif($anchor -eq 'end'){$x-=$ft.Width}
            if($x -lt 0 -or ($x+$ft.Width) -gt $diagramWidth -or ($y-$ft.Baseline) -lt 0 -or ($y-$ft.Baseline+$ft.Height) -gt $diagramHeight){$script:overflow.Add($n.InnerText)}
            if($n.ParentNode.GetAttribute('class') -eq 'arch-node') {
                $nodeBox=$n.ParentNode.SelectSingleNode('*[local-name()="rect"]')
                if($x -lt ([double]$nodeBox.x+8) -or ($x+$ft.Width) -gt ([double]$nodeBox.x+[double]$nodeBox.width-8) -or ($y-$ft.Baseline+$ft.Height) -gt ([double]$nodeBox.y+[double]$nodeBox.height-5)) {$script:overflow.Add('Node text overflow: '+$n.InnerText)}
            }
            $dc.DrawText($ft,[System.Windows.Point]::new($x,$y-$ft.Baseline))
        }
    }
    foreach($child in $n.ChildNodes) { DrawNode $child $s }
    for($i=0;$i -lt $push;$i++) {$dc.Pop()}
}
DrawNode $doc.DocumentElement @{fill='#000000';stroke='none';'stroke-width'='1'}
$dc.Pop(); $dc.Close()
$bitmap=[System.Windows.Media.Imaging.RenderTargetBitmap]::new([int]($diagramWidth*$scale),[int]($diagramHeight*$scale),96,96,[System.Windows.Media.PixelFormats]::Pbgra32)
$bitmap.Render($visual)
$encoder=[System.Windows.Media.Imaging.PngBitmapEncoder]::new()
$encoder.Frames.Add([System.Windows.Media.Imaging.BitmapFrame]::Create($bitmap))
$stream=[IO.File]::Create($OutputPng)
try{$encoder.Save($stream)}finally{$stream.Dispose()}
if($script:overflow.Count){throw "Text outside diagram: $($script:overflow -join '; ')"}
Write-Output "Rendered PNG. No text outside diagram."
