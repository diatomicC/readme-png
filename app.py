import streamlit as st
from PIL import Image

# Set the title of the app
st.title("Readme.png")

# Create a file uploader for PNG files
uploaded_file = st.file_uploader("Choose a PNG file", type=["png"])

# Check if a file has been uploaded
if uploaded_file is not None:
    # Open the uploaded image
    image = Image.open(uploaded_file)

    # Display the image
    st.image(image, caption='Uploaded PNG Image', use_column_width=True)

    # Optionally, you can show some information about the file
    st.write("Filename:", uploaded_file.name)
    st.write("File type:", uploaded_file.type)
    st.write("File size (in bytes):", uploaded_file.size)
