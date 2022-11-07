import logging
import mimic3_tts
import opentts_abc
import os
import pipes
import subprocess
import tempfile
import unittest
import uuid
import wave
from collections import OrderedDict
from naomi import diagnose
from naomi import plugin
from naomi import profile


class Mimic3TTSPlugin(plugin.TTSPlugin):
    """
    Uses the flite speech synthesizer
    Requires flite to be available
    """

    def __init__(self, *args, **kwargs):
        plugin.TTSPlugin.__init__(self, *args, **kwargs)

        voice = profile.get(['mimic3-tts', 'voice'], 'en_US/cmu-arctic_low#slt')
        self._logger.info("Voice: {}".format(voice))
        voices = self.get_voices()
        if not voice or voice not in voices:
            self._logger.info(
                "Voice {} not in Voices {}".format(voice, voices)
            )
            voice = ''
        if '#' in voice:
            self.voice, self.speaker = voice.split('#')
        else:
            self.voice = voice
            self.speaker = ''
        settings = mimic3_tts.tts.Mimic3Settings(
            voice=self.voice,
            speaker=self.speaker,
            sample_rate=16000
        )
        self.speakerobj = mimic3_tts.tts.Mimic3TextToSpeechSystem(settings)

    def settings(self):
        return OrderedDict(
            [
                (
                    ('mimic3-tts', 'voice'), {
                        'type': 'listbox',
                        'title': self.gettext('Voice for Mimic 3 Text to Speech'),
                        'description': "".join([
                            self.gettext('This is the voice Naomi will use to speak to you')
                        ]),
                        'options': self.get_voices(),
                        'default': 'en_US/cmu-arctic_low#slt'
                    }
                )
            ]
        )

    @classmethod
    def get_voices(cls):
        language = profile.get_profile_var(['language'])
        # In the language variable, the language and region are separated by
        # a dash. Mimic3 uses an underscore. So convert any dashes to
        # underscores
        language = language.replace('-', '_')
        settings = mimic3_tts.tts.Mimic3Settings()
        speakerobj = mimic3_tts.tts.Mimic3TextToSpeechSystem(settings)
        voices = [voice for voice in speakerobj.get_voices() if voice.language[:len(language)]==language]
        output = []
        for voice in voices:
            if voice.speakers is None:
                output.append(f"{voice.key}")
            else:
                for speaker in voice.speakers:
                    output.append(f"{voice.key}#{speaker}")
        return output

    # This plugin can receive a voice as a third parameter. This allows easier
    # testing of different voices.
    def say(self, phrase, voice=None):
        reconfigure = False
        if voice:
            # split voice and speaker at '#'
            voice, speaker = voice.split('#')
            if voice != self.voice:
                reconfigure = True
            if speaker:
                if speaker != self.speaker:
                    reconfigure = True
            else:
                speaker = self.speaker
        if reconfigure:
            mimic3_settings = {
                'sample_rate': 16000,
                'voice': voice,
                'speaker': speaker
            }
            self.speakerobj = mimic3_tts.tts.Mimic3TextToSpeechSystem(settings)
        self.speakerobj.begin_utterance()
        # Mimic3 spells out any upper case words, so convert everything to
        # lower case
        self.speakerobj.speak_text(phrase.lower())
        tokens = self.speakerobj.end_utterance()
        
        output = b''
        for token in tokens:
            # there should only be one AudioResult token
            # we should be able to add up all the audio_bytes arrays
            # and create one file with all the AudioResults added together
            # if necessary.
            if isinstance(token, opentts_abc.AudioResult):
                # use wave to add the file header
                filename = f"/tmp/mimic3_{uuid.uuid4().hex}.wav"
                # It seems silly to write this to a file since we have the raw
                # data already.
                with wave.open(filename, "wb") as w:
                    w.setnchannels(token.num_channels)
                    w.setsampwidth(token.sample_width_bytes)
                    w.setframerate(token.sample_rate_hz // token.num_channels)
                    w.setnframes(len(token.audio_bytes) // (token.sample_width_bytes * token.num_channels))
                    w.writeframes(token.audio_bytes)
                with open(filename, "rb") as f:
                    output = f.read().strip()
                os.remove(filename)
        return output
