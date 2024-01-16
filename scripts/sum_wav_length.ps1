$WavFolder = './retain/'

$sum_length = 0.0  # in seconds

Get-ChildItem -Path $WavFolder -Include '*.wav' -Recurse | ForEach-Object {
    [byte[]] $byte_rate = Get-Content -Path $_.FullName -AsByteStream -TotalCount 32 | Select-Object -Last 4
    [byte[]] $size = Get-Content -Path $_.FullName -AsByteStream -TotalCount 44 | Select-Object -Last 4

    $byte_rate_actual = [System.BitConverter]::ToInt32($byte_rate)
    $size_actual = [System.BitConverter]::ToInt32($size)
    $length = $size_actual / $byte_rate_actual
    $sum_length += $length
}

Write-Host $sum_length
return $sum_length
