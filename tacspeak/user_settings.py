DEBUG_MODE = False                              # enables additional logging, and if properly setup in the grammar module:
                                                # - enables module without needing the app in focus, i.e. AppContext()
                                                # - actions only print to console, they don't press virtual keys
DEBUG_HEAVY_DUMP_GRAMMAR = False                # expensive on memory, don't set this to True unless you're sure
                                                # if properly setup in the grammar module:
                                                # - generates a .debug_grammar_*.txt that describes the spec of the active commands
USE_NOISE_SINK = True                           # load NoiseSink rule(s), if it's setup in the grammar module.
                                                # - it should partially capture other noises and words outside of commands, and do nothing.
KALDI_ENGINE_SETTINGS = {
    "listen_key":0x05,                          # see https://learn.microsoft.com/en-us/windows/win32/inputdev/virtual-key-codes
                                                # 0x10=SHIFT key
                                                # 0x05=X1 mouse button
                                                # 0x06=X2 mouse button
                                                # None=overrides listen_key_toggle, and sets it into always listening mode; 
                                                #      uses Voice Activity Detector (VAD) to detect end of speech and recognise commands.
    "listen_key_toggle":-1,                     # Recommended is 0 or -1. 
                                                #  0 for toggle mode off; 
                                                #  1 for toggle mode on; 
                                                #  2 for global toggle mode on (use VAD); 
                                                #  -1 for toggle mode off but allow priority grammar even when key not pressed
    "listen_key_padding_end_ms_min":1,          # min ms of audio captured after listen_key is released (or toggled off), after which if VAD detects silence it will stop capturing; 
                                                # recommended is 1 if using listen_key_toggle (0 or -1), 0 for anything else.
    "listen_key_padding_end_ms_max":170,        # max ms of audio captured after listen_key is released (or toggled off), but will stop short if VAD detects silence; 
                                                # recommended is 170 if using listen_key_toggle (0 or -1), 0 for anything else.
    "listen_key_padding_end_always_max":False,  # disregard VAD and always capture listen_key_padding_end_ms_max of audio after listen_key is released (or toggled off)
    "vad_padding_end_ms":150,                   # ms of required silence after VAD; 
                                                # recommended is 150 if using listen_key_toggle (0 or -1), 250 for anything else.
    "auto_add_to_user_lexicon":False,           # this requires g2p_en (which isn't installed by default)
    "allow_online_pronunciations":False,
    # "retain_dir":"./retain/",                 # uncomment this to retain recordings of recognised commands. set to a writeable directory to retain recognition metadata and/or audio data
    # "retain_audio":True,                      # uncomment this to retain recordings of recognised commands. set to True to retain audio of recognitions in .wav files in the retain_dir (if set)
    # "retain_metadata":True,                   # uncomment this to retain recordings of recognised commands. set to True to retain metadata of recognitions in a .tsv file in retain_dir (if set)
    # "retain_approval_func":None,              # keep as None and/or commented.
    # "audio_input_device":None,                # set to an int to choose a non-default microphone. use "./tacspeak.exe --print_mic_list" to see what devices are available.
    # "input_device_index":None,
    # "vad_aggressiveness":3,                   # default aggressiveness of VAD
    # "vad_padding_start_ms":150,               # default ms of required silence before VAD
    # "model_dir":'kaldi_model',                # default model directory
    # "tmp_dir":None, 
    # "audio_self_threaded":True, 
    # "audio_auto_reconnect":True, 
    # "audio_reconnect_callback":None,
    # "vad_complex_padding_end_ms":600,         # default ms of required silence after VAD for complex utterances
    # "lazy_compilation":True,                  # set to True to parallelize & speed up loading
    # "invalidate_cache":False,
    # "expected_error_rate_threshold":None,
    # "alternative_dictation":None,
    # "compiler_init_config":None, 
    # "decoder_init_config":None,
}