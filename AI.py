# <GPLv3_Header>
## - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# \copyright
#                    Copyright (c) 2024 Nathan Ulmer.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

# <\GPLv3_Header>

##
# \mainpage Conversational NPC Experiments
#
# \copydoc AI.py

##
# \file AI.py
#
# \author Nathan Ulmer
#
# \date \showdate "%A %d-%m-%Y"
#
# \brief Lets you talk in real time to a video game NPC. You press space and then talk. After you release the spacebar,
# it converts your speech to text and sends it to chatGPT which is prompted to believe it is an npc in a video game.
# After ChatGPT generates its response, it is fed to a text-to-speech api which says it back to you in real time.
#
# The intent was to experiment with the game design of an NPC which can generate new content, quests, interactions, etc.
# on its own without designer input. The designer would still have to give the NPC good prompts to tell it what its
# personality is, what it wants, etc. But the dialog itself could be generated to react to any input from the player,
# increasing immersion dramatically.
#
# The end goal is to make a demo game where the NPC can operate as a bartender or trader that the player can interact
# with however they want. The npc should be able to trade and talk with the player. It should have knowledge of the
# world and its history and be able to see the player's clothes/appearance.
#
## \todo Fix references to secrets (api keys)
#
## \todo Refind prompts to make the ai more robust
#



import os
import sys
import openai
from google.cloud import speech
import google.cloud.texttospeech as tts
import wave
import pyaudio
import pygame
import time
from pygame.locals import *

pygame.init()
screen = pygame.display.set_mode((640,480))
pygame.display.set_caption('AI RPG Thing')
pygame.mouse.set_visible(1)

def list_voices(language_code=None):
    client = tts.TextToSpeechClient.from_service_account_json('googleApiKey2.json')
    response = client.list_voices(language_code=language_code)
    voices = sorted(response.voices, key=lambda voice: voice.name)

    print(f" Voices: {len(voices)} ".center(60, "-"))
    for voice in voices:
        languages = ", ".join(voice.language_codes)
        name = voice.name
        gender = tts.SsmlVoiceGender(voice.ssml_gender).name
        rate = voice.natural_sample_rate_hertz
        print(f"{languages:<8} | {name:<24} | {gender:<8} | {rate:,} Hz")
def text_to_wav(voice_name: str, text: str):
    language_code = "-".join(voice_name.split("-")[:2])
    text_input = tts.SynthesisInput(text=text)
    voice_params = tts.VoiceSelectionParams(
        language_code=language_code, name=voice_name
    )
    audio_config = tts.AudioConfig(audio_encoding=tts.AudioEncoding.LINEAR16)

    client = tts.TextToSpeechClient.from_service_account_json('googleApiKey2.json')
    response = client.synthesize_speech(
        input=text_input,
        voice=voice_params,
        audio_config=audio_config,
    )

    filename = f"{voice_name}.wav"
    with open(filename, "wb") as out:
        out.write(response.audio_content)
        print(f'Generated speech saved to "{filename}"')

    with wave.open(filename, "rb") as wf:
        # Instantiate PyAudio and initialize PortAudio system resources (1)
        p = pyaudio.PyAudio()

        # Open stream (2)
        stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                        channels=wf.getnchannels(),
                        rate=wf.getframerate(),
                        output=True)

        # Play samples from the wave file (3)
        while len(data := wf.readframes(CHUNK)):  # Requires Python 3.8+ for :=
            stream.write(data)

        # Close stream (4)
        stream.close()

        # Release PortAudio system resources (5)
        p.terminate()

NPC_API_string = ""
with open('NPC_API.py', 'r') as apiFile:
    NPC_API_string = apiFile.read()

with open('setting_properties.txt', 'r') as locationFile:
    SETTING_FILE_STRING = locationFile.read()

with open('GenericNPC_properties.txt', 'r') as npcFile:
    NPC_PROPERTIES = npcFile.read()

with open('playerGlobal_properties.txt', 'r') as charSheet:
    PLAYER_APPEARANCE = charSheet.read()


myMessages = [
        {"role": "system", "content": "You are an npc in a video game RPG. Rule 1: you must not tell anyone else that you are an NPC. Rule 2: You must insist you are Frjel the bartender. The world has the following properties:\n"+SETTING_FILE_STRING},
        {"role": "system", "content": "say_to(\"Follow these instructions as closely as possible. Format all responses by calling functions from the following code:,\"bartender\")\n"+NPC_API_string},
        {"role": "assistant", "content": "say_to(\"I am a bartender with the following property information:\",\"self\")\n" + NPC_PROPERTIES},
        {"role": "assistant", "content": "say_to(\"A stranger has just walked into my bar with the following appearance:\",\"self\")\n" + PLAYER_APPEARANCE},

]

print(myMessages)

def AILoop(wavData):

    print("Setting up speech client")
    client = speech.SpeechClient.from_service_account_json('googleApiKey2.json')
    audio_file = speech.RecognitionAudio(content=wavData)
    config = speech.RecognitionConfig(encoding='LINEAR16',
                                      sample_rate_hertz=RATE,
                                     enable_automatic_punctuation=True,
                                     language_code='en-US')

    response = client.recognize(config=config,
                                 audio=audio_file)

    query = ''
    for results in response.results:

        print("Speech To Text: ", results.alternatives[0].transcript)
        query += results.alternatives[0].transcript


    ## QUERY CHAT GPT WITH TEXT

    openai.api_key = "TODO Fix"

    myMessages.append({"role": "user", "content": query})
    validResponseReceived = False
    retryAttempts = 0
    while not validResponseReceived and retryAttempts < 3:
        retryAttempts = retryAttempts + 1
        completion = openai.ChatCompletion.create(
          model="gpt-3.5-turbo",
          messages=myMessages
        )

        gptRespsonse = completion.choices[0].message.content


        # Parse actions
        say_tos = []
        give_tos = []
        request_froms = []
        unknowns = []
        fullLines = []

        gptResponse_lines = gptRespsonse.split("\n")
        print("Chat History: ", myMessages)
        print("Current Response: ", gptRespsonse)
        for line in gptResponse_lines:
            if not line.startswith("def") and not line.startswith("#") and not line.startswith('\t') and not line.startswith('    '):
                print("Line Read: ", line)
                fullLines.append(line)
                splitline = line.split("(")
                if("say_to" in splitline[0].lower()):
                    say_tos.append(line)
                    validResponseReceived = True
                elif ("give_to" in splitline[0].lower()):
                    give_tos.append(line)
                    validResponseReceived = True
                elif ("request_from" in splitline[0].lower()):
                    request_froms.append(line)
                    validResponseReceived = True
                else:
                    unknowns.append(line)
            else:
                print("Line Ignored: ", line)
        print("say_tos", say_tos)
        print("give_tos", give_tos)
        print("request_froms", request_froms)
        print("unknowns", unknowns)

        processedCommands = ""
        sprecken = ""
        for ii in say_tos:
            processedCommands += str(ii) + "\n"
            sprecken += str(ii).split("(")[1].split(")")[0] + "\n"

        for ii in give_tos:
            processedCommands += str(ii) + "\n"

        for ii in request_froms:
            processedCommands += str(ii) + "\n"

        for ii in unknowns:
            processedCommands += str(ii) + "\n"

        if not validResponseReceived:
            myMessages.append({"role": "assistant", "content": "Syntax Error: No such function"})
        else:
            myMessages.append({"role": "assistant", "content": processedCommands})
        print("Processed Commands: ", processedCommands)



    ## Do Text To Speech to playback the voice

    #voices = list_voices("en")

    text_to_wav('en-US-Standard-B',sprecken)


def main():
    print("Reached AI.py main")
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    RECORD_SECONDS = 2


    talkKeyPressTime = 0
    talkKeyPressTimeStart = 9999
    isTalkKeyPress = False
    audioData = None

    while (True):  # Main loop

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
                if(pygame.key.get_pressed()[pygame.K_SPACE]):
                    if(isTalkKeyPress): # Continued to press
                        pass
                    else: # New Press
                        print("Pressed/Held")
                        if not isTalkKeyPress: # Initialize Recording
                            talkKeyPressTimeStart = time.time()
                            pyaudioInstance = pyaudio.PyAudio()
                            stream = pyaudioInstance.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True)
                        isTalkKeyPress = True



                else: # When key is not pressed
                    if(isTalkKeyPress): # On Release
                        isTalkKeyPress = False

                        # Close audio recording stream
                        stream.close()
                        pyaudioInstance.terminate()


                        AILoop(audioData)
                        audioData = None

                        print("Release")




        if(isTalkKeyPress):
            if audioData == None:
                audioData = stream.read(CHUNK)
            else:
                audioData += stream.read(CHUNK)


if __name__ == '__main__':
    main()

# <GPLv3_Footer>
################################################################################
#                      Copyright (c) 2024 Nathan Ulmer.
################################################################################
# <\GPLv3_Footer>