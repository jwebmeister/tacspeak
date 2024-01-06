$RetainTsvFilepath = ".\cleanaudio\retain.tsv"
$NewTsvFilepath = ".\cleanaudio_cmds\retain.tsv"


# The only thing that matters is the `audio_data` and the `text` for model training - don't trust anything else
$Header =   'audio_data',       # file name of the audio file for the recognition
            'wav_length',       # length of the wav in seconds
            'grammar_name',     # name of the recognized grammar
            'rule_name',        # name of the recognized rule
            'text',             # text of the recognition
            'likelihood',       # the engine’s estimated confidence of the recognition (not very reliable)
            'tag',              # a single text tag, described below
            'has_dictation'     # whether the recognition contained (in part) a dictation element

$RetainTsv = Import-Csv -Path $RetainTsvFilepath -Delimiter "`t" -Header $Header
$NewTsv = @()
foreach($row in $RetainTsv) {
    if ($row.rule_name -eq "YellFreeze") {
        continue
    } else {
        $NewTsv += $row
    }
}

# $NewTsv | Export-Csv -Path $NewTsvFilepath -Delimiter "`t" -NoTypeInformation -NoHeader -UseQuotes Never -Force

foreach($row in $NewTsv) {
    $WavFilename = Split-Path $row.audio_data -Leaf
    $WavFilepath = (Split-Path -Parent $RetainTsvFilepath) + "\" + $WavFilename
    $NewWavFilepath = (Split-Path -Parent $NewTsvFilepath) + "\" + $WavFilename
    # echo $WavFilepath
    # echo $NewWavFilepath
    Copy-Item -Path $WavFilepath -Destination $NewWavFilepath -Force
    $row.audio_data = ("./" + (Split-Path (Split-Path -Parent $NewTsvFilepath) -Leaf) + "/" + $WavFilename)
}

$NewTsv | Export-Csv -Path $NewTsvFilepath -Delimiter "`t" -NoTypeInformation -NoHeader -UseQuotes Never -Force