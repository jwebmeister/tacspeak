# Tacspeak

>**Fast, lightweight, modular - speech recognition for gaming**

[![GithubDownloads](https://img.shields.io/github/downloads/jwebmeister/tacspeak/total?logo=github)](https://github.com/jwebmeister/tacspeak/releases) [![NexusmodsModPage](https://img.shields.io/badge/download-Nexus%20Mods-orange)](https://www.nexusmods.com/readyornot/mods/3159) [![Discord](https://img.shields.io/discord/1183400761372180610?logo=discord)](https://discord.gg/QfMV2J8SgP)

[![Donate](https://img.shields.io/badge/donate-GitHub-pink.svg)](https://github.com/sponsors/jwebmeister) [![Donate](https://img.shields.io/badge/donate-PayPal-green.svg)](https://paypal.me/jwebmeister)


## Introduction

Tacspeak has been designed specifically for **recognising speech commands while playing games**, particularly system resource and FPS hungry games!

**Fast** - typically on the order of 10-50ms, from detected speech end (VAD) to action.

**Lightweight** - it runs on CPU, with ~2GB RAM.

**Modular** - you can build your own set of voice commands for additional games, or modify [existing ones](tacspeak/grammar).

**Open source** - you can modify any part of Tacspeak for yourself, and/or contribute back to the project and help build it as part of the community.

[![Watch the video demo of me using Tacspeak while playing Ready or Not](https://img.youtube.com/vi/qBL0bCt_VMo/maxresdefault.jpg)](https://youtu.be/qBL0bCt_VMo)

---

Tacspeak is built atop the excellent [Dragonfly](https://github.com/dictation-toolbox/dragonfly) speech recognition framework for Python. 
- Note: Tacspeak uses a *modified version* of Dragonfly located at [jwebmeister/dragonfly](https://github.com/jwebmeister/dragonfly).
- Please see the Dragonfly [docs](http://dragonfly.readthedocs.org/en/latest/) for information on building grammars and rules (i.e. voice commands). 
- Please also see the existing [examples](tacspeak/grammar) of Tacspeak grammar modules.

Also built atop the excellent [Kaldi Active Grammar](https://github.com/daanzu/kaldi-active-grammar/), which provides the [Kaldi](https://github.com/kaldi-asr/kaldi) (also excellent) engine backend and model for Dragonfly.

## Requirements

- OS: Windows 10/11, 64-bit
- ~2GB+ disk space for model plus temporary storage and cache.
- ~2GB+ RAM.
- Only supports English language speech recognition, as provided via [Kaldi Active Grammar](https://github.com/daanzu/kaldi-active-grammar).

## Basic install - packaged executable

[![Watch the video demo of me downloading and install Tacspeak](https://img.youtube.com/vi/P405ucc2wP4/maxresdefault.jpg)](https://youtu.be/P405ucc2wP4)

1. Download and install [Microsoft Visual C++ Redistributable](https://aka.ms/vs/17/release/vc_redist.x64.exe)
2. Download the [latest release](https://github.com/jwebmeister/tacspeak/releases/latest/), including both (they are separate downloads and/or releases):
    - the Tacspeak application .zip (includes .exe)
    - a pre-trained Kaldi model .zip (includes kaldi_model folder).
3. Extract the Tacspeak application .zip into a folder, and extract the Kaldi model .zip into the same folder. Check the following files exists:
    - `./tacspeak.exe`
    - `./tacspeak/user_settings.py`
    - `./tacspeak/grammar/_readyornot.py`
    - `./kaldi_model/Dictation.fst` - if not you need to download and extract the pre-trained model
4. Run the executable `Tacspeak/tacspeak.exe` :)

## Usage
### Basic

[![Watch the video Tacspeak getting starting guide how to use & change settings (basic)](https://img.youtube.com/vi/KnYrxzThG-E/maxresdefault.jpg)](https://youtu.be/KnYrxzThG-E)

Run `tacspeak.exe` (or `python ./cli.py`) and it will...
- load `./tacspeak/user_settings.py`
- load all modules `./tacspeak/grammar/_*.py`
- start the speech engine
- begin listening for commands, but it will...
    - wait for a matching app context (defined in the `grammar` modules), then activate those relevant modules.
    - wait for the `listen_key` to be activated if it's specified, and depending on `listen_key_toggle` (toggle mode).

Also:
- You may need to **"Run as administrator"** `tacspeak.exe`
- Review and adjust  `./tacspeak/user_settings.py` to your liking. 
    - see example [./tacspeak/user_settings.py](tacspeak/user_settings.py)
- Review and adjust any module settings in `./tacspeak/grammar/_*.py`, e.g. keybindings. 
    - see example [./tacspeak/grammar/_readyornot.py](tacspeak/grammar/_readyornot.py)
- (Note: you will need to restart Tacspeak for changes to take effect.)
- [Tacspeak - Ready or Not commands list](https://docs.google.com/spreadsheets/d/1jpuR8JHmh0LOOcUQ7JMMzDOmSYYe2uMpy63X238ZySs/edit?usp=sharing) (imperfect, outdated, not maintained, but maybe useful)

### Important advisory

*Please use caution and your own discretion when installing or using any third-party files, specifically \*.py files. Don't install or use files from untrustworthy sources.*

Tacspeak automatically loads (and executes) `./tacspeak/user_settings.py` and all modules `./tacspeak/grammar/_*.py`, regardless of what code it contains.

### User settings

It is highly recommended to review and adjust  [./tacspeak/user_settings.py](tacspeak/user_settings.py) to your liking.

Open `./tacspeak/user_settings.py` in a text editor, change the settings, then save and overwrite the file.  There are comments in the file explaining most of the important settings.

For example, you might want to change these:
- `listen_key`=`0x05` 
    - `0x05` = mouse thumb button 1.
    - `0x10` = Shift key.
    - See [here](https://learn.microsoft.com/en-us/windows/win32/inputdev/virtual-key-codes) for more info.
    - `None` = overrides `listen_key_toggle`, and sets it into always listening mode; uses Voice Activity Detector (VAD) to detect end of speech and recognise commands.
- `listen_key_toggle`=`-1` 
    - Recommended is `0` or `-1`. 
    - `0` for toggle mode off, listen only while key is pressed; must release key for the command to be recognised.
    - `1` for toggle mode on, key press toggles listening on/off; must toggle off for the command to be recognised.
    - `2` for global toggle mode on, key press toggles listening on/off, but it uses Voice Activity Detector (VAD) to detect end of speech and recognise commands so you don't have to toggle off to recognise commands.
    - `-1` for toggle mode off + priority, listen only while key is pressed, except always listen for priority grammar ("freeze!") even when key is not pressed.
- `listen_key_padding_end_ms_min`=`1`
    - recommended is `1` if using `listen_key_toggle` `0` or `-1`; set to `0` for anything else.
    - min ms of audio captured after `listen_key` is released (or toggled off), after which if VAD detects silence it will stop capturing.
- `listen_key_padding_end_ms_max`=`170`
    - recommended is `170` if using `listen_key_toggle` `0` or `-1`; set to `0` for anything else.
    - max ms of audio captured after `listen_key` is released (or toggled off), but will stop short if VAD detects silence.
- `listen_key_padding_end_always_max`=`False`
    - disregard VAD and always capture `listen_key_padding_end_ms_max` of audio after `listen_key` is released (or toggled off)
- `vad_padding_end_ms`=`250`
    - recommended is `150` if using `listen_key_toggle` `0` or `-1`; set to `250` for anything else.
    - ms of required silence after VAD.
    - change this if you use VAD and find it's too quick or slow to identify the figure out you've stopped speaking and that it should try to recognise the command.
- `audio_input_device`=`None`
    - should use default microphone (as set within Windows Sound Settings), but should be able to change the index (number) to select a different input device.
- `USE_NOISE_SINK`=`True`
    - load NoiseSink rule(s), if it's setup in the grammar module - it should *partially* capture other noises and words outside of other rules, and do nothing. Set to `False` if you're having issues with recognition accuracy.
- `retain_dir`= `./retain/`
    - use this setting to retain recordings of recognised commands - set to a writeable directory to retain recognition metadata and/or audio data. Disabled by default.
- `retain_audio`= `True`
    - use this setting to retain recordings of recognised commands - set to True to retain speech data wave files in the `retain_dir`. Disabled by default.
- `retain_metadata`= `True`
    - use this setting to retain recordings of recognised commands - set to True to retain metadata of recognitions in a `.tsv` file in `retain_dir`. Disabled by default.
- `retain_approval_func`= `my_retain_func`
    - use this setting to retain recordings of recognised commands - set to a function returning `True` or `False` based on `AudioStoreEntry` contents. Disabled by default.

### Grammar modules

It is likely you will want to modify or customise some of the [existing Tacspeak grammar modules](tacspeak/grammar) (if not also add your own!), which you can do by editing the `./tacspeak/grammar/_*.py` file corresponding to the application you're interested in.  

As an example, in the [Ready or Not module](tacspeak/grammar/_readyornot.py) you can change `ingame_key_bindings` to align the Tacspeak module with your in-game keybindings.  
You could also change the words and/or sentences used for recognising speech commands, for example, adding "smoke it out" as an alternative to "breach and clear".

Additional notes:
- Please see the existing [examples](tacspeak/grammar) of Tacspeak grammar modules.
- Please see the Dragonfly [docs](http://dragonfly.readthedocs.org/en/latest/) for information on building grammars, rules, and actions (i.e. voice commands). 
- Note: Tacspeak uses a *modified version* of Dragonfly located at [jwebmeister/dragonfly](https://github.com/jwebmeister/dragonfly). Review the source and/or commits of the fork to understand its differences to the original project and the corresponding docs.

### Models

See [kaldi_model/README.md](kaldi_model/README.md) for more information.

## Troubleshooting

Things to check or try first:
- Is [Microsoft Visual C++ Redistributable](https://aka.ms/vs/17/release/vc_redist.x64.exe) installed?
- Have the Tacspeak application and model files been extracted into the correct locations? Check the following files exists:
    - `./tacspeak.exe`
    - `./tacspeak/user_settings.py`
    - `./tacspeak/grammar/_readyornot.py`
    - `./kaldi_model/Dictation.fst` - if not you need to download and extract the pre-trained model
- Have you tried "Run as administrator" on `tacspeak.exe`?
- Is the correct microphone set as the default in Windows Sound Settings?
- Are you pressing the `listen_key` (by default it is mouse thumb button), and does it show "Hot mic" in the console?
- Are you running ReadyOrNot and have the window focused (i.e. you're not alt-tabbed to another window)?
- Are you pressing the `listen_key` (default is mouse thumb button), speaking, then releasing after you finish speaking?
- Check the key bindings in `./tacspeak/grammar/_readyornot.py`. It's set for default game keybindings.
- Check the ".tacspeak.log" file for any useful error messages to narrow it down.
- Try reinstalling (extracting from .zips) everything, including the model, don't change anything in `./tacspeak/user_settings.py` or `./tacspeak/grammar/_readyornot.py` keep it all default, try running `tacspeak.exe`.
- For Tacspeak version ≥0.1.1, run `./tacspeak.exe --print_mic_list` in Powershell or command prompt. 
    - This will list all of the audio devices found on your system, and can be useful for figuring out the correct index number for the `audio_input_device` setting in `./tacspeak/user_settings.py`. 
    - A far easier option to try first is to set the correct default recording device in Windows Sound Settings.
- The underlying model that Tacspeak currently uses is based on "16-bit Signed Integer PCM 1-channel 16kHz" audio. Tacspeak tries to convert the incoming audio from your device to this format, but if it's too much for a single CPU core to convert in real-time it may fall over. 
    - I've had no issues using Tacspeak with a 48kHz, 16-bit, 2-channel microphone array and also using a Rode AI-1 and Podmic at 48kHz, 24-bit, 1-channel. 
    - If, for example, your device is recording at 144kHz, or something a single core on your CPU can't handle, it will likely display errors in the console.
- If you no longer hear audio from your output device (headphones), or no audio is coming through from your input device (microphone), you might have to disable "Exclusive Mode" for your audio device in Windows Sound Settings. Follow these steps to disable Exclusive Mode:
    - Right-click the Speaker icon on the Windows toolbar, and select Open Sound settings.
    - Click Device properties located underneath Choose your output device, then click Additional device properties located underneath Related Settings.
    - In the Line Properties window, click the Advanced tab, then uncheck Allow applications to take exclusive control of this device.
    - Click Apply, then click OK.
- All commands are being queued? AZERTY keyboard? You might need to change your in-game keybinding for "Hold command" to something other than Shift, and also update the key bindings in `./tacspeak/grammar/_readyornot.py`.
- In your Windows privacy and security settings, can apps (including Tacspeak) access your microphone?  Is your microphone working in other apps?
- Try setting `USE_NOISE_SINK` (in `./tacspeak/user_settings.py`) to `True` or `False` if you're getting too many false positive or false negative speech recognitions respectively.
- If you want to retain recordings of the speech recognitions from Tacspeak, set `retain_dir`, `retain_audio` and `retain_metadata` (in `./tacspeak/user_settings.py`) appropriately.

## Advanced install - Python

### Prerequisites: 

1. [Microsoft Visual C++ Redistributable](https://aka.ms/vs/17/release/vc_redist.x64.exe) installed
2. Python 3.11 installed

### Steps:

1. Clone this repo into a folder, e.g. `Tacspeak/`.
2. Download a pre-trained Kaldi model .zip from the [latest release](https://github.com/jwebmeister/tacspeak/releases/latest/) and extract into the cloned project folder, e.g. `Tacspeak/kaldi_model/` after extraction.
3. Open the `Tacspeak/` folder in PowerShell (or equivalent).
4. Strongly recommended to use a virtual environment, e.g. 
    - create within `Tacspeak` folder: `python -m venv "./.venv"`
    - activate within `Tacspeak` folder: `./.venv/Scripts/Activate.ps1`
5. Install required packages via pip
    - `pip install -r requirements.txt`
6. Done! Should now be able to run Tacspeak via `python ./cli.py`


## Build instructions

### Prerequisites: 

1. [Microsoft Visual C++ Redistributable](https://aka.ms/vs/17/release/vc_redist.x64.exe) installed
2. Python 3.11 installed
3. A compatible compiler for cx_freeze installed, 
    - Only tested Visual Studio 2022, [MSVC](https://visualstudio.microsoft.com/downloads/)
4. (Optional, but necessary for releases) PortAudio v19.7.0, `portaudio_x64.dll`, build from [source here](https://files.portaudio.com/archives/pa_stable_v190700_20210406.tgz) using [docs here](https://files.portaudio.com/docs/v19-doxydocs/compile_cmake.html), or [download here](https://github.com/jwebmeister/portaudio/releases/tag/v19.7.0)

### Steps - Option 1

1. Clone this repo into a folder, e.g. `Tacspeak/`.
2. Open the `Tacspeak/` folder in PowerShell, keep it as your current working directory.
3. Create and activate a python virtual environment in directory `./.venv`, e.g. 
    - create within `Tacspeak` folder: `python -m venv "./.venv"`
    - activate within `Tacspeak` folder: `./.venv/Scripts/Activate.ps1`
4. Run `scripts\setup_for_build.ps1` in PowerShell. This will download and install dependencies via running the following scripts:
    - scripts\pip_reinstall_all.ps1
    - scripts\download_replace_portaudio_x64_dll.ps1
    - scripts\download_extract_model.ps1
    - scripts\move_extracted_model.ps1
    - scripts\generate_all_licenses.ps1
5. Run `scripts\build_app.ps1` in PowerShell


### Steps - Option 2

1. Clone this repo into a folder, e.g. `Tacspeak/`.
2. Download a pre-trained Kaldi model .zip from the [latest release](https://github.com/jwebmeister/tacspeak/releases/latest/) and extract into the cloned project folder, e.g. `Tacspeak/kaldi_model/`.
3. Open the `Tacspeak/` folder in PowerShell (or equivalent).
4. Strongly recommended to use a virtual environment, e.g. 
    - create within `Tacspeak` folder: `python -m venv "./.venv"`
    - activate within `Tacspeak` folder: `./.venv/Scripts/Activate.ps1`
5. Install required packages via pip
    - `pip install -r requirements.txt`
6. (Optional, but necessary for releases) rename `portaudio_x64.dll` to `libportaudio64bit.dll`, copy and paste overwriting the existing file located at `./venv/Lib/site-packages/_sounddevice_data/portaudio-binaries/libportaudio64bit.dll`.
7. Build via setup.py
    - `python setup.py build`

## Motivation

I built Tacspeak because I was fed-up with how poorly accurate the Windows Speech Recognition engine was with my voice, even after training. No other alternatives I tested (there were many) fit exactly what I wanted from speech recognition while gaming. 

What I learned from my research and testing:
- most state-of-the-art Automatic Speech Recognition (ASR) systems are not fit for the purpose of speech command recognition while gaming. They:
    - take too long, e.g. 1-3 seconds.
    - take too much memory, e.g. 2-4 GB of VRAM (textures pop-in in-game). 
    - take too much CPU/GPU processing power.
    - are designed for wider applications beyond speech *command* recognition, e.g. free-form dictation.
- there are decades-old ASR's that are fit-for-purpose, but their tool and build chains were too unwieldy.
- on paper, the Windows Speech Recognition engine should be perfect for my use-case, it just hates me (and everyone else).
- I needed a customisable speech recognition framework to fit my specific use-case.

Tacspeak isn't perfect, but it is a very strong option, precisely because it can be so highly customised to your specific commands, for your specific application.

## Contributing

Issues, suggestions, and feature requests are welcome. 

Pull requests are considered, but be warned the project structure is in flux and there may be breaking changes to come.  
We'd also like *some* (TBD) quality testing be done on grammar modules before they're brought into the project. If you can help define what we mean by "some (TBD) quality testing"... well, trailblazers are welcome!

Tacspeak uses a modified version of Dragonfly located at [jwebmeister/dragonfly](https://github.com/jwebmeister/dragonfly).  This is where the heart of the beast (bugs) lives... please help slay it!  
Also, be warned the project structure is in flux and there may be breaking changes there too.

You can also consider supporting the projects Tacspeak are built upon, [dictation-toolbox/dragonfly](https://github.com/dictation-toolbox/dragonfly) and [daanzu/kaldi-active-grammar](https://github.com/daanzu/kaldi-active-grammar).

Any and all donations are very much appreciated and help encourage development.

[![Donate](https://img.shields.io/badge/donate-GitHub-pink.svg)](https://github.com/sponsors/jwebmeister) [![Donate](https://img.shields.io/badge/donate-PayPal-green.svg)](https://paypal.me/jwebmeister)

## Author

- Joshua Webb ([@jwebmeister](https://github.com/jwebmeister))

## License

This project is licensed under the GNU Affero General Public License v3 (AGPL-3.0-or-later). See the [LICENSE.txt file](LICENSE.txt) for details.

## Acknowledgments

- Based upon and may include code from "Dragonfly" [dictation-toolbox/dragonfly](https://github.com/dictation-toolbox/dragonfly), under the LGPL-3.0 license.
- Based upon and may include code from "Kaldi Active Grammar" [daanzu/kaldi-active-grammar](https://github.com/daanzu/kaldi-active-grammar), under the AGPL-3.0 license.
