import os
import sys
from pathlib import Path
import requests
import pyaudio
from openai import OpenAI
from playsound import playsound
from base64 import b64decode
import wave

# KEEP THIS SECRET PLEASE!
client = OpenAI(api_key="")


# Generate the next line in a conversation
def text_generation(conversation):
    response = client.chat.completions.create(
        messages=conversation,
        model="gpt-4o",
        max_tokens=200,
        frequency_penalty=0.0,          # Number between -2.0 and 2.0. Positive values penalize new tokens based on their existing frequency in the text so far, decreasing the model's likelihood to repeat the same line verbatim.
        # presence_penalty=0.0,           # Number between -2.0 and 2.0. Positive values penalize new tokens based on whether they appear in the text so far, increasing the model's likelihood to talk about new topics.
        temperature=0.5,                # What sampling temperature to use, between 0 and 2. Higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic.
        # seed=0
    )
    response_text = response.choices[0].message.content
    return response_text


# Transcribe audio into text
def speech_to_text(filename):
    with open(filename, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            response_format="text",
            language="en"
        )
        return transcript


# Convert text into audio (stored as a mp3).
def text_to_speech(text, accent="alloy", filename="util/audio/generated_speech.mp3"):
    if getattr(sys, 'frozen', False):
        speech_file_path = Path(sys.executable).parent
    elif __file__:
        speech_file_path = Path(__file__).parent.parent
    speech_file_path = speech_file_path / filename

    response = client.audio.speech.create(
      model="tts-1",
      voice=accent,
      input=text
    )
    response.stream_to_file(speech_file_path)
    playsound(str(speech_file_path))
    os.remove(str(speech_file_path))


# Convert text into audio (streamed as a wav and not saved).
def text_to_speech_stream(text, accent="alloy", filename="util/audio/generated_speech.wav"):
    data = {
        "model": "tts-1",
        "voice": accent,
        "input": text,
        "response_format": "wav"
    }
    headers = {
        "Authorization": f'Bearer {os.getenv("OPENAI_API_KEY")}',
    }
    response = requests.post('https://api.openai.com/v1/audio/speech', headers=headers, json=data, stream=True)
    CHUNK_SIZE = 1024
    if response.ok:
        with wave.open(response.raw, 'rb') as wf:
            p = pyaudio.PyAudio()
            stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                            channels=wf.getnchannels(),
                            rate=wf.getframerate(),
                            output=True)
            while len(data := wf.readframes(CHUNK_SIZE)):
                stream.write(data)
            # Sleep to make sure playback has finished before closing
            # sleep(1)
            stream.close()
            p.terminate()
    else:
        response.raise_for_status()


# Generate an image based on a provided prompt
def image_generation(prompt, response_format="url", filename="generated_image"):
    response_image = client.images.generate(
      model="dall-e-3",
      prompt=prompt,
      size="1024x1024",
      quality="standard",
      n=1,
      response_format=response_format
    )
    if response_format == "url":
        return response_image.data[0].url
    else:
        base64_string = response_image.data[0].b64_json
        image_data = b64decode(base64_string)
        image_file = filename + ".png"
        with open(image_file, mode="wb") as png:
            png.write(image_data)


# Use vision to analyse an image
def vision(url, conversation, image_prompt="Describe this image"):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages= conversation + [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": image_prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": url,
                            "detail": "high"
                        },
                    },
                ],
            }
        ],
        max_tokens=200
    )
    return response.choices[0].message.content
