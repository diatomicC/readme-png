import streamlit as st
from PIL import Image
from openai import OpenAI
import openai
import io
import base64
import mimetypes
import datetime

from pages import show_api_page, show_chatbot_page

st.set_page_config(layout="centered", page_title="ReadMePNG")

if "page" not in st.session_state:
    st.session_state.page = "upload"

def image_to_base64(image):
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    img_bytes = buffered.getvalue()
    
    mime_type = 'image/png'  
    encoded_string = base64.b64encode(img_bytes).decode('utf-8')
    image_base64 = f"data:{mime_type};base64,{encoded_string}"
    
    return image_base64


def extract_text_from_image(image):
    try:
        # Convert image to base64
        img_base64 = image_to_base64(image)

        client = OpenAI()


        # Prepare the request to GPT-4 Vision
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                "role": "system",
                "content": [
                    {
                    "type": "text",
                    "text": "Take ALL the text EXACTLY from this given image about a product on an online shop, and translate them into Japanese, English, Deutsch, Chinese.\n\nRespond with the following format:\n```JSON\n{\n  \"ko\": {\n    \"result\": \"\",\n  },\n  \"en\": {\n    \"result\": \"\",\n  },\n  // add language codes as needed\n}\n```\n"
                    }
                ]
                }
            ],
            temperature=1,
            max_tokens=2272,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            response_format={
                "type": "json_object"
            }
            )

        extracted_text = response.choices[0].message.content
        return extracted_text

    except Exception as e:
        st.error(f"Error with GPT-4 Vision API: {e}")
        return ""

# Function to translate text using GPT-4
def translate_text_and_generate_markdown(text, target_languages):
    translations = {}
    for lang in target_languages:
        messages = [
            {"role": "system", "content": "You are a helpful assistant that translates and formats text into markdown."},
            {"role": "user", "content": f"Translate this text into {lang}: {text}. Format the translation in Markdown."}
        ]

        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            max_tokens=2048
        )
        
        translations[lang] = response.choices[0].message.content
    
    return translations

# Main Streamlit function
def main():
    st.title("ReadMePNG Service")
    if st.session_state.page == "upload":
        # File upload
        uploaded_files = st.file_uploader("Upload PNG files", type="png", accept_multiple_files=True)
        
        if uploaded_files:
            st.subheader("Uploaded Images")
            for file in uploaded_files:
                st.image(file, caption=file.name, use_column_width=True)
            
            if st.button("Process Images"):
                extracted_text = ""
                for file in uploaded_files:
                    image = Image.open(file)
                    extracted_text += extract_text_from_image(image) + "\n\n"
                
                st.session_state.extracted_text = extracted_text
                st.success("Text extracted successfully!")

        # Display extracted text after processing
        if 'extracted_text' in st.session_state:
            st.subheader("Extracted Text from Image")
            st.text_area("OCR Result", value=st.session_state.extracted_text, height=300)

            # Language selection for translation
            languages = [
                "English", "Chinese", "Japanese", "Spanish", "French", "German", 
                "Italian", "Portuguese", "Russian", "Korean", "Arabic", "Hindi", 
                "Dutch", "Swedish", "Danish", "Finnish", "Turkish", "Greek", "Polish", "Thai"
            ]
            selected_languages = st.multiselect("Select target languages for translation", languages)

            # Translate button
            if selected_languages and st.button("Translate"):
                translations = translate_text_and_generate_markdown(st.session_state.extracted_text, selected_languages)
                st.session_state.translations = translations
                st.success("Translation completed!")

        # Display translated markdown content
        if 'translations' in st.session_state:
            st.subheader("Translated Markdown Content")
            for lang, translation in st.session_state.translations.items():
                with st.expander(f"{lang} Translation"):
                    st.markdown(translation)

            # Download section for markdown files
            st.subheader("Download Translated Markdown Files")
            for lang, translation in st.session_state.translations.items():
                st.download_button(
                    label=f"Download {lang} Markdown",
                    data=translation,
                    file_name=f"product_description_{lang}.md",
                    mime="text/markdown"
                )

if __name__ == "__main__":
    main()

# Display last loaded time and rerun button
st.write(f"Last loaded: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
if st.button('Rerun'):
    st.rerun()

# Page routing
if st.session_state.page == "upload":
    if st.button("Go to API Page"):
        st.session_state.page = "api"
        st.empty()  # Remove existing components
        st.rerun()
elif st.session_state.page == "api":
    show_api_page()
elif st.session_state.page == "chatbot":
    show_chatbot_page()


# import streamlit as st
# from PIL import Image
# from pages import show_api_page, show_chatbot_page
# import datetime
# from api import get_openai_stream

# import requests
# import json
# import io
# import base64
# import openai



# st.set_page_config(layout="centered", page_title="ReadMePNG")

# # Initialize session state
# if "page" not in st.session_state:
#     st.session_state.page = "upload"

# def extract_text_from_image(image):
#     # Convert image to bytes
#     buffered = io.BytesIO()
#     image.save(buffered, format="PNG")
#     img_bytes = buffered.getvalue()

#     # Convert the image to base64
#     img_base64 = base64.b64encode(img_bytes).decode('utf-8')

#     # Naver OCR API request headers
#     headers = {
#         "X-OCR-SECRET": CLOVA_OCR_API_KEY,
#         "Content-Type": "application/json"
#     }

#     # Prepare the data payload for OCR API request
#     data = {
#         "version": "V2",
#         "requestId": "test",
#         "timestamp": 0,
#         "images": [
#             {
#                 "format": "png",
#                 "data": img_base64,
#                 "name": "sample"
#             }
#         ]
#     }

#     # Make the OCR request to Clova
#     response = requests.post(CLOVA_OCR_API_URL, headers=headers, json=data)
    
#     if response.status_code == 200:
#         result = response.json()
#         extracted_text = ""
#         # Extract and concatenate all text from the OCR result
#         for field in result['images'][0]['fields']:
#             extracted_text += field['inferText'] + " "
#         return extracted_text
#     else:
#         st.error(f"Error {response.status_code}: {response.text}")
#         return ""

# def translate_text_and_generate_markdown(text, target_languages):
#     translations = {}
#     for lang in target_languages:
#         # Construct GPT-4o prompt for translation and markdown formatting
#         messages = [
#             {"role": "system", "content": "You are a helpful assistant that translates and formats text into markdown."},
#             {"role": "user", "content": f"Take the ENTIRE {text} from this given image about a product on an online shop, and translate them into {lang}. Don't omit anything, just spot every possible details in the text. You may format that in Markdown. Provide some summarized information around 5-10 sentences as well. Follow the form of the given format:\n```JSON\n{{\"result\": \"\",\"summary\": \"\"}}\n```"} ]


#         response = openai.chat.completions.create(  # Use the new v1.0+ API method
#             model="gpt-4o",  # Specify the GPT-4o model
#             messages=messages,
#             max_tokens=10000  # Adjust as needed
#         )
        
#         # Extract translated markdown content
#         translations[lang] = response.choices[0].message.content
    
#     return translations



# def main():
#     st.title("ReadMePNG Service")

#     # File upload
#     uploaded_files = st.file_uploader("Upload PNG files", type="png", accept_multiple_files=True)
    
#     if uploaded_files:
#         st.subheader("Uploaded Images")
#         for file in uploaded_files:
#             st.image(file, caption=file.name, use_column_width=True)
        
#         # If 'Process Images' button is pressed, extract text from the images
#         if st.button("Process Images"):
#             extracted_text = ""
            
#             for file in uploaded_files:
#                 image = Image.open(file)
#                 extracted_text += extract_text_from_image(image) + "\n\n"
            
#             # Store the extracted text in the session state for further use
#             st.session_state.extracted_text = extracted_text
#             st.success("Text extracted successfully!")

#     # Display extracted text immediately after processing
#     if 'extracted_text' in st.session_state:
#         st.subheader("Extracted Text from Image")
#         st.text_area("OCR Result", value=st.session_state.extracted_text, height=300)

#         # Language selection
#         languages = [
#             "English", "Chinese", "Japanese", "Spanish", "French", "German", 
#             "Italian", "Portuguese", "Russian", "Korean", "Arabic", "Hindi", 
#             "Dutch", "Swedish", "Danish", "Finnish", "Turkish", "Greek", "Polish", "Thai"
#         ]
#         selected_languages = st.multiselect("Select target languages for translation", languages)

#         # Translate button
#         if selected_languages and st.button("Translate"):
#             translations = translate_text_and_generate_markdown(st.session_state.extracted_text, selected_languages)
#             st.session_state.translations = translations
#             st.success("Translation completed!")

#     # Display translated markdown content
#     if 'translations' in st.session_state:
#         st.subheader("Translated Markdown Content")
#         for lang, translation in st.session_state.translations.items():
#             with st.expander(f"{lang} Translation"):
#                 st.markdown(translation)

#         # Download section for markdown files
#         st.subheader("Download Translated Markdown Files")
#         for lang, translation in st.session_state.translations.items():
#             st.download_button(
#                 label=f"Download {lang} Markdown",
#                 data=translation,
#                 file_name=f"product_description_{lang}.md",
#                 mime="text/markdown"
#             )

# if __name__ == "__main__":
#     main()

# # Display last loaded time and rerun button
# st.write(f"Last loaded: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
# if st.button('Rerun'):
#     st.rerun()

# # Routing logic for the page switching
# if st.session_state.page == "upload":
#     if st.button("Go to API Page"):
#         st.session_state.page = "api"
#         st.rerun()

# elif st.session_state.page == "api":
#     show_api_page()

# elif st.session_state.page == "chatbot":
#     show_chatbot_page()
