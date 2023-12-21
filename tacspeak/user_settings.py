DEBUG_MODE = False
DEBUG_HEAVY_DUMP_GRAMMAR = False # expensive on memory, don't set this to True unless you're sure
KALDI_ENGINE_SETTINGS = {
    "listen_key":0x05, # 0x10=SHIFT key, 0x05=X1 mouse button, 0x06=X2 mouse button, see https://learn.microsoft.com/en-us/windows/win32/inputdev/virtual-key-codes
    "listen_key_toggle":-1, # Recommended is 0 or -1. 0 for toggle mode off; 1 for toggle mode on; 2 for global toggle on (use VAD); -1 for toggle mode off but allow priority grammar even when key not pressed
    "vad_padding_end_ms":250, # ms of required silence after VAD
    "auto_add_to_user_lexicon":False, # this requires g2p_en (which isn't installed by default)
    "allow_online_pronunciations":False,
    # "audio_input_device":None, # set to an int to choose a non-default microphone
    # "input_device_index":None,
    # "vad_aggressiveness":3, # default aggressiveness of VAD
    # "vad_padding_start_ms":150, # default ms of required silence before VAD
    # "model_dir":'kaldi_model', # default model directory
    # "tmp_dir":None, 
    # "audio_self_threaded":True, 
    # "audio_auto_reconnect":True, 
    # "audio_reconnect_callback":None,
    # "retain_dir":"./retain/", # set to a writable directory path to retain recognition metadata and/or audio data
    # "retain_audio":True, # set to True to retain speech data wave files in the retain_dir (if set)
    # "retain_metadata":True, 
    # "retain_approval_func":None,
    # "vad_complex_padding_end_ms":600, # default ms of required silence after VAD for complex utterances
    # "lazy_compilation":True, # set to True to parallelize & speed up loading
    # "invalidate_cache":False,
    # "expected_error_rate_threshold":None,
    # "alternative_dictation":None,
    # "compiler_init_config":None, 
    # "decoder_init_config":None,
}