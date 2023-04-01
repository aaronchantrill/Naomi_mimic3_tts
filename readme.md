---
id: mimic3-tts
label: Mimic3-tts
title: Mimic3 Text to Speech
type: ttss
description: "Allows Naomi to use Mimic3 Text to Speech voices"
source: https://github.com/aaronchantrill/Naomi_mimic3_tts/blob/master/readme.md
meta:
  - property: og:title
    content: "Mimic3 Text to Speech"
  - property: og:description
    content: "Allows Naomi to use Mimic3 Text to Speech voices"
---

# Mimic 3 Text to Speech

This plugin uses the Mycroft [Mimic 3](https://mycroft.ai/mimic-3/) text to speech module to convert text into Naomi's spoken responses.

This is a system with an amazing number of voices which are further subdivided into speakers.

To install this plugin, go to your Naomi's personal plugins directory at ~/.config/naomi/plugins/

Create a "tts" folder if there isn't already one.

`cd tts`

`git clone https://github.com/aaronchantrill/Naomi_mimic3_tts.git`

finally, install the mycroft-mimic3-tts PyPi package with
`cd Naomi_mimic3_tts`
`pip install -r python_requirements.txt`

Then start Naomi with Naomi --repopulate and select "mimic3-tts" as your text to speech engine.

You can also just install this package through the Naomi Plugin Exchange with
`Naomi --install "mimic3-tts"`

Naomi will start with a default voice of "en_US/cmu-arctic_low#slt".
The list of available voices is at https://github.com/MycroftAI/mimic3-voices.
Mimic voice strings include a voice followed by an optional hash and the name of the speaker.
You shouldn't have to manually install any voices.
Mimic3 should automatically download the voice the first time you use it, so just configure your desired voice in your profile.yml:

```
mimic3-tts:
  voice: en_US/cmu-arctic_low#slt
```

<EditPageLink/>
