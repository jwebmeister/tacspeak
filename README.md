# Tacspeak

>**Fast, lightweight, modular - speech recognition for gaming**

[![Donate](https://img.shields.io/badge/donate-GitHub-pink.svg)](https://github.com/sponsors/jwebmeister) [![Donate](https://img.shields.io/badge/donate-PayPal-green.svg)](https://paypal.me/jwebmeister)

## Introduction

Tacspeak has been designed specifically for **recognising speech commands while playing games**, particularly system resource and FPS hungry games!

**Fast** - typically on the order of 10-200ms, depending on complexity.

**Lightweight** - it runs on the CPU, with a little RAM.

**Modular** - you can build your own set of voice commands for additional games, or modify existing ones. See [examples](https://github.com/jwebmeister/tacspeak/tree/main/tacspeak/grammar).

**Open source** - you can modify any part of Tacspeak for yourself, and/or contribute back to the project and help build it as part of the community.

---

Tacspeak is built atop the excellent [Dragonfly](https://github.com/dictation-toolbox/dragonfly) speech recognition framework for Python. 
- Note: Tacspeak uses a modified version of Dragonfly located at [jwebmeister/dragonfly](https://github.com/jwebmeister/dragonfly).
- Please see the Dragonfly [docs](http://dragonfly.readthedocs.org/en/latest/) for information on building grammars and rules (i.e. voice commands). 
- Please also see the existing [examples](https://github.com/jwebmeister/tacspeak/tree/main/tacspeak/grammar) of Tacspeak grammar modules.

Also built atop the excellent [Kaldi Active Grammar](https://github.com/daanzu/kaldi-active-grammar/), which provides the Kaldi engine backed and model for Dragonfly.

## Requirements

- OS: Windows 10/11, 64-bit
- ~2GB+ disk space for model plus temporary storage and cache.
- ~2GB+ RAM.

## Install instructions

todo

## Build instructions

todo

## Motivation

I built Tacspeak because I was fed-up with how poorly accurate the Windows Speech Recognition engine was with my voice, even after training. No other alternatives I tested (there were many) fit exactly what I wanted from speech recognition while gaming. 

What I learned from my research and testing:
- most state-of-the-art Automatic Speech Recognition (ASR) systems are not fit for the purpose of speech command recognition while gaming. They:
    - take too long, e.g. 1-3 seconds.
    - take too much memory, e.g. 2-4 GB of VRAM (textures pop-in in-game). 
    - take too much CPU/GPU processing power, e.g. 20-40% utilisation.
    - are designed for wider applications beyond speech *command* recognition, e.g. free-form dictation.
- there are decades-old ASR's that are fit-for-purpose, but their software toolchain and build process has grown too-far out-of-date.
- on paper, the Windows Speech Recognition engine should be perfect for my use-case, it just hates me (and everyone else).
- I needed a customisable speech recognition framework to fit my specific use-case.

Tacspeak isn't perfect, but it beats the competition by a fair margin, precisely because it can be customised to your specific commands, for your specific context.

## Contributing

Issues, suggestions, and feature requests are welcome. 

Pull requests are considered, but we'd like *some* (TBD) quality testing be done on grammar modules before they're brought into the project.  
If you can help define what we mean by "some (TBD) quality testing"... trailblazers are welcome!

Tacspeak uses a modified version of Dragonfly located at [jwebmeister/dragonfly](https://github.com/jwebmeister/dragonfly).  This is where the heart of the beast (bugs) lives... please help slay it!

You can also consider supporting the projects Tacspeak are built upon, [dictation-toolbox/dragonfly](https://github.com/dictation-toolbox/dragonfly) and [daanzu/kaldi-active-grammar](https://github.com/daanzu/kaldi-active-grammar).

Any and all donations are very much appreciated and help encourage development.

[![Donate](https://img.shields.io/badge/donate-GitHub-pink.svg)](https://github.com/sponsors/jwebmeister) [![Donate](https://img.shields.io/badge/donate-PayPal-green.svg)](https://paypal.me/jwebmeister)

Please feel free to reach out to me, contact info [@jwebmeister](https://github.com/jwebmeister).

## Author

- Joshua Webb ([@jwebmeister](https://github.com/jwebmeister))

## License

This project is licensed under the GNU Affero General Public License v3 (AGPL-3.0-or-later). See the [LICENSE.txt file](LICENSE.txt) for details.

## Acknowledgments

- Based upon and may include code from "Dragonfly" [dictation-toolbox/dragonfly](https://github.com/dictation-toolbox/dragonfly), under the LGPL-3.0 license.
- Based upon and may include code from "Kaldi Active Grammar" [daanzu/kaldi-active-grammar](https://github.com/daanzu/kaldi-active-grammar), under the AGPL-3.0 license.
