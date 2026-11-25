[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$raw = [Console]::In.ReadToEnd()
try { $j = $raw | ConvertFrom-Json } catch { Write-Output "statusline: bad input"; exit 0 }

# ANSI colors
$E = [char]27
$RST = "$E[0m"; $DIM = "$E[2m"; $BOLD = "$E[1m"
$CYAN = "$E[36m"; $MAG = "$E[35m"; $GRN = "$E[32m"; $YEL = "$E[33m"; $RED = "$E[31m"

# Green < 50%, yellow < 80%, red otherwise
function Pct-Color($p) {
    if ($p -ge 80) { return $RED }
    if ($p -ge 50) { return $YEL }
    return $GRN
}

function Fmt-Tok($n) {
    if ($null -eq $n) { return "--" }
    if ($n -ge 1000000) { return ("{0:0.#}M" -f ($n / 1000000)) }
    if ($n -ge 1000) { return ("{0:0}k" -f ($n / 1000)) }
    return "$n"
}

function Fmt-Reset($epoch, $fmt) {
    if ($null -eq $epoch) { return $null }
    try {
        $dt = [DateTimeOffset]::FromUnixTimeSeconds([long]$epoch).LocalDateTime
        return $dt.ToString($fmt, [System.Globalization.CultureInfo]::InvariantCulture)
    } catch { return $null }
}

# Model
$model = "--"
if ($j.model -and $j.model.display_name) { $model = $j.model.display_name }
$model = "$BOLD$CYAN$model$RST"

# Context
$ctx = "${MAG}ctx$RST $DIM--$RST"
$cw = $j.context_window
if ($cw -and $null -ne $cw.used_percentage) {
    $c = Pct-Color $cw.used_percentage
    $ctx = "${MAG}ctx$RST $c{0:0}%$RST" -f $cw.used_percentage
    if ($null -ne $cw.total_input_tokens -and $null -ne $cw.context_window_size) {
        $ctx += " $DIM({0}/{1})$RST" -f (Fmt-Tok $cw.total_input_tokens), (Fmt-Tok $cw.context_window_size)
    }
}

# Rate limits
function Fmt-Limit($label, $w, $fmt) {
    if ($null -eq $w -or $null -eq $w.used_percentage) { return "$MAG$label$RST $DIM--$RST" }
    $c = Pct-Color $w.used_percentage
    $s = "$MAG$label$RST $c{0:0}%$RST" -f $w.used_percentage
    $r = Fmt-Reset $w.resets_at $fmt
    if ($r) { $s += " $DIM(reset $r)$RST" }
    return $s
}
$rl = $j.rate_limits
$five = $null; $week = $null
if ($rl) { $five = $rl.five_hour; $week = $rl.seven_day }
$h5 = Fmt-Limit "5h" $five "HH:mm"
$d7 = Fmt-Limit "7d" $week "ddd HH:mm"

$sep = " $DIM|$RST "
Write-Output ($model + $sep + $ctx + $sep + $h5 + $sep + $d7)
