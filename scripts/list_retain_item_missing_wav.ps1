$RetainTsvFilepath = ".\retain\retain.tsv"

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
$RetainTsv | ForEach-Object -Begin {$TheList=@()} -Process {
    $WavFilepath = $_.audio_data
    if (-not (Test-Path $WavFilepath)) {
        $TheList += $WavFilepath
    }
} -End {return $TheList}