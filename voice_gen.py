from openai import OpenAI
import os
from pathlib import Path
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

CLIENT_OPENAI = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

client = CLIENT_OPENAI

with open(str("default_menu/default_restaurant_menu.txt"), "rb") as menu:    
    menu_file = client.files.create(file=menu,
        purpose='assistants')
menu_file_id = menu_file.id   

vector_store = client.beta.vector_stores.create(name=f"MOM AI EXAMPLARY DEFAULT MENU")



# Ready the files for upload to OpenAI
file_paths = ["default_menu/default_restaurant_menu.txt"]
file_streams = [open(path, "rb") for path in file_paths]

# Use the upload and poll SDK helper to upload the files, add them to the vector store,
# and poll the status of the file batch for completion.
file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
vector_store_id=vector_store.id, files=file_streams
)

print(menu_file_id)
print(vector_store.id)




















'''
voice_output_text = """
                   Привет, как твои дела? 
                   Hi, how are you? 
                   Hallo, wie geht's du? 
                   Привіт, як справи? 
                   Hola, chica, tienes ojos bonitos"
                   """

speech_file_path = Path(__file__).parent / "speech.mp3"

response = client.audio.speech.create(
    model="tts-1",
    voice="alloy",
    input=voice_output_text
    )

print(response)

response.stream_to_file(speech_file_path)
"""

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You are a cool punk!"},
        {"role": "user", "content": "Hey, what's up bro"},
        
    ]
    )

print(response)

response_text = response.choices[0].message.content

print(response_text)
"""
'''