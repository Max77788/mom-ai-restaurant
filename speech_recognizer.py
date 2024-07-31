import io
import os
import click
from google.cloud import speech

@click.command()
@click.argument('audio_file', type=click.Path(exists=True))
def transcribe_audio(audio_file):
    """Transcribe the given audio file using Google Cloud Speech-to-Text."""
    try:
        # Read the audio file
        with open(audio_file, 'rb') as f:
            audio_content = f.read()

        print(f"Audio content (length {len(audio_content)} bytes): {audio_content[:100]}...")

        # Transcribe the audio file using Google Cloud Speech-to-Text
        client = speech.SpeechClient()
        audio = speech.RecognitionAudio(content=audio_content)
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            #sample_rate_hertz=48000,
            language_code="pl-PL",
        )

        response = client.recognize(config=config, audio=audio)
        print("Full response ", response)
        user_input = ""
        for result in response.results:
            user_input += result.alternatives[0].transcript
        print(f"Transcription result: {user_input}")
    except Exception as e:
        print(f"Error during transcription: {e}")

if __name__ == '__main__':
    transcribe_audio()
