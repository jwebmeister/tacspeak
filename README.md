# Tacspeak

>**Fast, lightweight, modular - speech recognition for gaming**

[![Donate](https://img.shields.io/badge/donate-GitHub-pink.svg)](https://github.com/sponsors/jwebmeister) [![Donate](https://img.shields.io/badge/donate-PayPal-green.svg)](https://paypal.me/jwebmeister)

## Introduction

Tacspeak has been designed specifically for **recognising speech commands while playing games**, particularly system resource and FPS hungry games!

**Fast** - typically on the order of 10-200ms, depending on complexity.

**Lightweight** - it runs on spare CPU cores, with ~2GB RAM.

**Modular** - you can build your own set of voice commands for additional games, or modify [existing ones](tacspeak/grammar).

**Open source** - you can modify any part of Tacspeak for yourself, and/or contribute back to the project and help build it as part of the community.

---

Tacspeak is built atop the excellent [Dragonfly](https://github.com/dictation-toolbox/dragonfly) speech recognition framework for Python. 
- Note: Tacspeak uses a modified version of Dragonfly located at [jwebmeister/dragonfly](https://github.com/jwebmeister/dragonfly).
- Please see the Dragonfly [docs](http://dragonfly.readthedocs.org/en/latest/) for information on building grammars and rules (i.e. voice commands). 
- Please also see the existing [examples](tacspeak/grammar) of Tacspeak grammar modules.

Also built atop the excellent [Kaldi Active Grammar](https://github.com/daanzu/kaldi-active-grammar/), which provides the [Kaldi](https://github.com/kaldi-asr/kaldi) (also excellent) engine backend and model for Dragonfly.

## Requirements

- OS: Windows 10/11, 64-bit
- ~2GB+ disk space for model plus temporary storage and cache.
- ~2GB+ RAM.
- Only supports English language speech recognition, as provided via [Kaldi Active Grammar](https://github.com/daanzu/kaldi-active-grammar).

## Usage
### Basic
Run `tacspeak.exe` (or `python ./cli.py`); it will..
- load `./tacspeak/user_settings.py`
- load all modules `./tacspeak/grammar/_*.py`
- start the speech engine
- begin listening for commands, but it will...
    - wait for a matching app context (defined in the `grammar` modules), then activate those relevant modules.
    - wait for the `listen_key` to be activated if it's specified, and depending on toggle-mode.

### User settings

It is highly recommended to review and adjust  `./tacspeak/user_settings.py` to your liking.

Open `./tacspeak/user_settings.py` in a text editor, change the settings, then save and overwrite the file.  There are comments explaining most of the important settings.

By default (you'll likely want to change these):
- `listen_key`=`0x10` (the Shift key), and 
- `listen_key_toggle`=`0` (active only while key is pressed)

### User defined voice commands and words

- Note: Tacspeak uses a modified version of Dragonfly located at [jwebmeister/dragonfly](https://github.com/jwebmeister/dragonfly).
- Please see the Dragonfly [docs](http://dragonfly.readthedocs.org/en/latest/) for information on building grammars and rules (i.e. voice commands). 
- Please also see the existing [examples](tacspeak/grammar) of Tacspeak grammar modules.
- Words not defined within the existing model *can* be added, but it will involve recompiling the model. See [kaldi_model/README.md](kaldi_model/README.md) for more information.

### Important advice

*Please use caution and your own discretion in regards to utilising third-party files, specifically \*.py files.*

Tacspeak automatically loads (and executes) `./tacspeak/user_settings.py` and all modules `./tacspeak/grammar/_*.py`, regardless of what code it contains.

## Simple install - packaged executable

1. Download and install [Microsoft Visual C++ Redistributable](https://aka.ms/vs/17/release/vc_redist.x64.exe)
2. Download the [latest release](https://github.com/jwebmeister/tacspeak/releases/latest/), including both (they are separate downloads and/or releases):
    - the Tacspeak application .zip (includes runtime executable)
    - a pre-trained Kaldi model .zip.
3. Extract the Tacspeak application .zip into a folder, and extract the Kaldi model .zip into the same folder, 
    - e.g. `Tacspeak/` and `Tacspeak/kaldi_model/`, 
    - (Note: there should be a folder `Tacspeak/Tacspeak/` after extraction).
4. Run the executable `Tacspeak/tacspeak.exe` :)

## Complex install - Python

### Prerequisites: 

- Python 3.11 installed

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

### Steps

1. Clone this repo into a folder, e.g. `Tacspeak/`.
2. Download a pre-trained Kaldi model .zip from the [latest release](https://github.com/jwebmeister/tacspeak/releases/latest/) and extract into the cloned project folder, e.g. `Tacspeak/kaldi_model/`.
3. Open the `Tacspeak/` folder in PowerShell (or equivalent).
4. Strongly recommended to use a virtual environment, e.g. 
    - create within `Tacspeak` folder: `python -m venv "./.venv"`
    - activate within `Tacspeak` folder: `./.venv/Scripts/Activate.ps1`
5. Install required packages via pip
    - `pip install -r requirements.txt`
6. Build via setup.py
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

Pull requests are considered, but we'd like *some* (TBD) quality testing be done on grammar modules before they're brought into the project.  
If you can help define what we mean by "some (TBD) quality testing"... trailblazers are welcome!

Tacspeak uses a modified version of Dragonfly located at [jwebmeister/dragonfly](https://github.com/jwebmeister/dragonfly).  This is where the heart of the beast (bugs) lives... please help slay it!

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
