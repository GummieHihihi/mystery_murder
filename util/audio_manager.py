import audioop
import os
import sys
import threading
import queue
import pyaudio
import wave
import time
from pathlib import Path
from playsound import playsound


def print_microphones():
    p = pyaudio.PyAudio()
    info = p.get_host_api_info_by_index(0)
    num_devices = info.get('deviceCount')
    for i in range(0, num_devices):
        if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
            print("Input Device id ", i, " - ", p.get_device_info_by_host_api_device_index(0, i).get('name'))


# Plays an audio file at the specified path. Works for both executable and source code versions.
def play_audio(file_path):
    if getattr(sys, 'frozen', False):
        speech_file_path = Path(sys.executable).parent
    elif __file__:
        speech_file_path = Path(__file__).parent.parent
    speech_file_path = speech_file_path / file_path
    playsound(str(speech_file_path))
    os.remove(str(speech_file_path))


# Record audio from the user (automatic start and stop)
def record_audio_automatic():
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    CHUNK = 1024
    audio_filename = "util/audio/recorded_audio.wav"
    audio_queue = queue.Queue()

    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK,
                        input_device_index=2)

    TIMEOUT_LENGTH = 2
    threshold_start = 1000
    threshold_end = 1000

    print("👂 Listening...")

    data_log = []
    max_record_buffer = 5
    while True:
        data = stream.read(CHUNK)
        data_log.append(data)
        rms_val = audioop.rms(data, 2)
        # print(rms_val)
        if rms_val > threshold_start:
            record_buffer = min(len(data_log), max_record_buffer)
            for i in range(record_buffer):
                audio_queue.put(data_log[-(record_buffer-i)])
            current = time.time()
            end = time.time() + TIMEOUT_LENGTH
            print("🎤 Recording...")
            while current <= end:
                data = stream.read(CHUNK)
                rms_val = audioop.rms(data, 2)
                if rms_val >= threshold_end:
                    end = time.time() + TIMEOUT_LENGTH
                current = time.time()
                audio_queue.put(data)
            break

    print("✅ Finished recording")

    stream.stop_stream()
    stream.close()
    audio.terminate()

    with wave.open(audio_filename, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(list(audio_queue.queue)))

    return audio_filename


# Record audio from the user (manual stop)
def record_audio_manual():
    audio_filename = "util/audio/recorded_audio.wav"
    stop_event = threading.Event()
    audio_queue = queue.Queue()
    record_thread = threading.Thread(target=record_audio_thread, args=(audio_filename, stop_event, audio_queue))
    record_thread.start()
    input("\n")
    stop_event.set()
    record_thread.join()
    return audio_filename


# Record audio (thread for manual stopping)
def record_audio_thread(filename, stop_event, audio_queue):
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    CHUNK = 1024

    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        frames_per_buffer=CHUNK,
                        input_device_index=1)

    print("Recording... Press return key to stop.")

    while not stop_event.is_set():
        data = stream.read(CHUNK)
        audio_queue.put(data)

    print("Finished recording")

    stream.stop_stream()
    stream.close()
    audio.terminate()

    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(list(audio_queue.queue)))
