param(
    [switch]$Force
)

$root = Split-Path -Parent $MyInvocation.MyCommand.Definition
$backup = Join-Path $root '..\backups\templates\recomendaciones.html.orig'
$target = Join-Path $root '..\templates\peliculas\recomendaciones.html'

if (-not (Test-Path $backup)) {
    Write-Error "Backup no encontrado: $backup"
    exit 1
}

if (-not $Force) {
    Write-Host "Se restaurará 'recomendaciones.html' desde el backup. Continuar? (S/N)"
    $r = Read-Host
    if ($r -notin @('S','s','Y','y')) { Write-Host "Operación cancelada."; exit 0 }
}

Copy-Item -Path $backup -Destination $target -Force
Write-Host "Restauración completada: recomendaciones.html restaurado desde backup."
