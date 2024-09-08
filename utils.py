from gtts import gTTS
import os
import openai
import json
from tinydb import TinyDB, Query
import os
import uuid
from PIL import Image
import io
import base64
import streamlit as st

def translate_text_into_json(text, target_languages):
    messages = [
        {
            "role": "system",
            "content": f'Given a text about a product\'s information on an online shopping mall, translate it into {", ".join(target_languages)}.\n\nRespond with the following format:\n```json\n{{\n  "English": "",\n  // add language names as needed\n}}\n```'
        },
        {
            "role": "user",
            "content": text,
        }
    ]

    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        max_tokens=2048,
        response_format={"type": "json_object"}
    )
    
    content = response.choices[0].message.content
    translations = json.loads(content)
    return translations

def image_to_base64(image):
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    img_bytes = buffered.getvalue()
    encoded_string = base64.b64encode(img_bytes).decode('utf-8')
    return encoded_string

def save_to_database(filename, extracted_text, translations_json, product_name, price, image):
    os.makedirs('./saved_images', exist_ok=True)
    
    filename = f"{uuid.uuid4()}.png"
    save_path = os.path.join('./saved_images', filename)
    image.save(save_path)
    
    db = TinyDB("database.json")
    db.insert({
        "image_filename": filename,
        "extracted_text": extracted_text,
        "translations": translations_json,
        "product_name": product_name,
        "price": price
    })
    print("Data saved successfully:", db.all()[-1])

def get_all_from_database():
    db = TinyDB("database.json")
    return db.all()


def text_to_speech(text):
    tts = gTTS(text=text, lang='en')
    filename = "speech.mp3"
    tts.save(filename)
    
    with open(filename, "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        md = f"""
            <audio controls autoplay="true">
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
            """
        st.markdown(md, unsafe_allow_html=True)
    
    os.remove(filename)