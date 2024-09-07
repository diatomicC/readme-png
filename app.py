import streamlit as st
from PIL import Image
from pages import show_api_page, show_chatbot_page
import datetime

st.set_page_config(layout="centered", page_title="Readme-png")

# Initialize session state
if "page" not in st.session_state:
    st.session_state.page = "upload"

# Display last loaded time and rerun button
st.write(f"Last loaded: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
if st.button('Rerun'):
    st.rerun()

# Create placeholder containers for each page
upload_placeholder = st.empty()
api_placeholder = st.empty()
chatbot_placeholder = st.empty()

# Routing logic
if st.session_state.page == "upload":
    with upload_placeholder.container():
        st.title("Readme.png")

        uploaded_file = st.file_uploader("Choose a PNG file", type=["png"])

        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            st.image(image, caption='Uploaded PNG Image', use_column_width=True)
            st.write("Filename:", uploaded_file.name)
            st.write("File type:", uploaded_file.type)
            st.write("File size (in bytes):", uploaded_file.size)

        if st.button("Go to API Page"):
            st.session_state.page = "api"
            st.rerun()

elif st.session_state.page == "api":
    api_placeholder.empty()
    with api_placeholder.container():
        show_api_page()

elif st.session_state.page == "chatbot":
    chatbot_placeholder.empty()
    with chatbot_placeholder.container():
        show_chatbot_page()