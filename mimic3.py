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

        voice = profile.get(['mimic3-tts', 'voice'], 'en_US/cmu-arctic_low')
        self._logger.info("Voice: {}".format(voice))
        voices = self.get_voices()
        if not voice or voice not in voices:
            self._logger.info(
                "Voice {} not in Voices {}".format(voice, voices)
            )
            voice = ''
        self.voice = voice
        speaker = profile.get(['mimic3-tts','speaker'],'slt')
        self._logger.info("Speaker: {}".format(speaker))
        speakers = self.get_speakers(voice)
        if not speaker or speaker not in speakers:
            self._logger.info(
                "Speaker {} not in speakers {}".format(speaker, speakers)
            )
            speaker = ''
        self.speaker = speaker
        settings = mimic3_tts.tts.Mimic3Settings(
            voice=voice,
            speaker=speaker,
            sample_rate=16000
        )
        self.speakerobj = mimic3_tts.tts.Mimic3TextToSpeechSystem(settings)

    @classmethod
    def get_voices(cls):
        voices = mimic3_tts.tts.Mimic3TextToSpeechSystem(mimic3_tts.tts.Mimic3Settings()).get_voices()
        output = []
        for voice in voices:
            output.append(voice.key)
        return output
    
    @classmethod
    def get_speakers(cls, voice):
        voices = mimic3_tts.tts.Mimic3TextToSpeechSystem(mimic3_tts.tts.Mimic3Settings()).get_voices()
        output = []
        for v in voices:
            if v.key == voice:
                output = v.speakers
                break
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
        self.speakerobj.speak_text(phrase)
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
