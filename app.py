import streamlit as st
from PIL import Image
import os
from openai import OpenAI
import io
import base64
import datetime
import uuid
from chatbot_ui import chatbot_ui
from pages import show_all_items_page
from utils import save_to_database, translate_text_into_json, get_all_from_database

st.set_page_config(layout="centered", page_title="ReadMePNG")

if "page" not in st.session_state:
    st.session_state.page = "upload"
    st.session_state.step = 0


def image_to_base64(image):
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    img_bytes = buffered.getvalue()
    encoded_string = base64.b64encode(img_bytes).decode('utf-8')
    return encoded_string

def extract_text_from_image(image):
    try:
        img_base64 = image_to_base64(image)

        client = OpenAI()

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "Take ALL the text EXACTLY from this given image about a product on an online shop.\n\nRespond only with the extracted text."
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{img_base64}"
                            }    
                        }
                    ]
                }
            ],
            max_tokens=1000,
        )

        extracted_text = response.choices[0].message.content
        return extracted_text

    except Exception as e:
        st.error(f"Error with GPT-4 Vision API: {e}")
        return ""

    

def main():
    st.title("ReadMePNG Service")
    
    page = st.sidebar.radio("Navigation", ["Upload", "View All Items"])
    
    if page == "Upload":
        uploaded_files = st.file_uploader("Upload PNG files", type="png", accept_multiple_files=True)
       
        if uploaded_files:
            st.subheader("Uploaded Images")
            for file in uploaded_files:
                with st.expander(f"Image: {file.name}", expanded=True, icon="📜"):
                    st.image(file, caption=file.name, use_column_width=True)
            
            if st.button("Process Images"):
                extracted_text = ""
                for file in uploaded_files:
                    image = Image.open(file)
                    extracted_text += extract_text_from_image(image) + "\n\n"
                
                st.session_state.extracted_text = extracted_text
                st.success("Text extracted successfully!")
        
        if 'extracted_text' in st.session_state:
            st.subheader("Extracted Text from Image")
            st.text_area("OCR Result", value=st.session_state.extracted_text, height=300)

            languages = [
                "English", "Chinese", "Japanese", "Spanish", "French", "German", 
                "Italian", "Portuguese", "Russian", "Korean", "Arabic", "Hindi", 
                "Dutch", "Swedish", "Danish", "Finnish", "Turkish", "Greek", "Polish", "Thai"
            ]
            selected_languages = st.multiselect("Select target languages for translation", languages)

            if selected_languages and st.button("Translate"):
                translations_json = translate_text_into_json(st.session_state.extracted_text, selected_languages)
                st.session_state.translations = translations_json
                st.success("Translation completed!")

            if 'translations' in st.session_state:
                st.subheader("Translated Text Content")
                for lang, translation in st.session_state.translations.items():
                    with st.expander(f"{lang} Translation"):
                        st.text_area(value=translation, height=300, label=f"{lang} Translation")

                st.subheader("Product Information")
                product_name = st.text_input("Product Name")
                price = st.number_input("Price", min_value=0.0, format="%.2f")
                
                if st.button("Final Save"):
                    if product_name and price > 0:
                        for file in uploaded_files:
                            filename = file.name
                            # Save the image file
                            
                            image = Image.open(file)
                            # Save to database
                            save_to_database(filename, st.session_state.extracted_text, st.session_state.translations, product_name, price, image)
                        st.success("All data saved to database successfully!")
                    else:
                        st.error("Please enter a valid product name and price before saving.")
                
    elif page == "View All Items":
        show_all_items_page()

if __name__ == "__main__":
    main()

st.write(f"Last loaded: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
if st.button('Rerun'):
    st.rerun()