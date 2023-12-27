## retain folder

The retain folder is used for storing audio + metadata, which can be used for: 
- training and/or testing models
- debugging issues with the model + grammar modules
- reviewing the accuracy of the model + grammar modules

By default no audio or metadata is retained.  To enable retention of audio + metadata, uncomment (and change if necessary) the following items within `./tacspeak/user_settings.py`, within `KALDI_ENGINE_SETTINGS`:
- "retain_dir":"./retain/",
- "retain_audio":True,
- "retain_metadata":True, 