import pyttsx3
import speech_recognition as sr
import config as config
import cv2
import sys

from openai import OpenAI

api_key = config.config['openai']

client = OpenAI(api_key=api_key)

#openai.api_key = config.config['openai']

engine = pyttsx3.init()

engine.setProperty("rate", 150)

for voice in engine.getProperty('voices'):
    print(voice)

def change_voice(engine, language, gender='VoiceGenderFemale'):
    for voice in engine.getProperty('voices'):
        if language in voice.languages and gender == voice.gender:
            engine.setProperty('voice', voice.id)
            return True

    raise RuntimeError("Language '{}' for gender '{}' not found".format(language, gender))


def audio_to_text(f):
  recognizer = sr.Recognizer()
  with sr.AudioFile(f) as source:
    audio = recognizer.record(source)
  try:
    return recognizer.recognize_google(audio)
  except:
    return ("Could not understand audio")


def gpt_response(prompt):
    # Ensure messages is a list of dictionaries, each representing a message in the chat
    messages = [{"role": "user", "content": prompt}]
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=messages,
        max_tokens=4096,
        temperature=0.5,
    )
    return response.choices[0].message.content

def speak(text):
  engine.say(text)
  engine.runAndWait()
  
def main():
    running = True
    while running:
        try:
            filename = "prompt.wav"
            print("\nListening...\n")
            with sr.Microphone() as source:
                recognizer = sr.Recognizer()
                source.pause_threshold = 1
                audio = recognizer.listen(source, phrase_time_limit=None, timeout=None)
                with open(filename, "wb") as f:
                    f.write(audio.get_wav_data())

            change_voice(engine, "en_US", "VoiceGenderFemale")
            text = audio_to_text(filename)
            if text:
                print("Prompten din er: ", text)

                response = gpt_response(text)
                print("\nGPT svarer: ", response)
                speak(response)

                if "we are done" in text.lower():
                    print("Exiting program as requested.")
                    running = False
        except Exception as e:
            print(f"An error occurred: {e}")

main()