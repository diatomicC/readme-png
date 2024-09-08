import streamlit as st
from api import run_llm_api_test
from chatbot_ui import chatbot_ui
from utils import get_all_from_database, text_to_speech

def show_api_page():
    st.title("API Page")
    st.write("This is the API page content.")

    if st.button("Run LLM API Test"):
        with st.spinner("Running LLM API test..."):
            result = run_llm_api_test()
        st.success(result)

    if st.button("Go to Chatbot"):
        st.session_state.page = "chatbot"
        st.rerun()

    if st.button("Go back to Main Page"):
        st.session_state.page = "upload"
        st.rerun()

def show_chatbot_page():
    st.title("Readme-png chatbot")
    chatbot_ui(
        productName="베이스어스 노이즈캔슬링 블루투스 5.3 무선 헤드폰",
        productPrice="₩ 299,000",
        productInformation='''{
        "result": "Active Noise Cancelling Wireless Headphones 30dB Noise Reduction Great Sound Quality Free to Enjoy The Music\n\n36 Hours of Music / Continuous Playback All Day\n\n10 Hours\nLong Battery Life for Wireless Freedom\n\nNoise Cancellation Up to 30dB\nImmerse Yourself In Your Music Sans Noise\n\nWeighs Just 270g Easy and Lightweight\n\n40mm Large Moving Coil Create Your Style With Excellent Bass and Fine Details\n\nActive Noise Cancelling Up to 30dB Multiple Noise Reduction Settings Select Your Favorite\n\nAI Noise Reduction Algorithm Precise Analysis Effective Filtering No Noise During Calls\n\nVarious Modes User Friendly For Different Scenarios With Different Adjustment Modes\n\nFoldable Design More Convenient To Carry\n\nQuick Pairing And Stable Connection Bluetooth 5.0 Easy and Smooth Connectivity\n\nActive Noise Cancelling Up to 30dB Smart AI Adjustable Noise Reduction\n\nEnjoy A Peaceful Weekend Whether You Are Outside, Home, Or Traveling\n\n35dB Transport Mode\n\nProvides Great Sound and Noise Reduction For Clear Calls\n\nEasily Foldable and Portable\n\nEnjoy Long Lasting Music with Listening Modes\n\nStylish and Comfortable Natural Design Smooth curves Fit The Ears Naturally Full Day Comfort Without Pressure\n\nStrong Sound Effect Technology Comfortable Listening Excellent Earphone Performance\n\nEasy to Switch Modes Smart Operation\n\nWireless and Active Noise Cancellation 1. Device 2. Noise Control 3. Active Noise Reduction 4. Transparency Mode\n\nWorry Free Music Enjoyment Up to 35 Hours of Usage When Fully Active\n\nSmart Application Integration User Friendly\nWireless Active Noise Cancelling Headphones Easy Touch Control for Adjustments and Calls\n\nSimple Yet Powerful Professional Design with Wonderful Surround Sound"
        }
        ''',
        Language="Korean"
    )

    if st.button("Go back to API Page"):
        st.session_state.page = "api"
        st.rerun()

def show_all_items_page():
    items = get_all_from_database()
    
    if st.session_state.page == "chatbot":
        chatbot_ui(st.session_state.productName, st.session_state.productPrice, st.session_state.productInformation, st.session_state.Language, new_chat=st.session_state.get("new_chat", False))
        # Reset the new_chat flag after it's been used
        st.session_state.new_chat = False
        if st.button("Stop chatting"):
            st.session_state.page = "upload"
            # Clear chatbot session state
            st.session_state.pop("productName", None)
            st.session_state.pop("productPrice", None)
            st.session_state.pop("productInformation", None)
            st.session_state.pop("Language", None)
            st.session_state.pop("messages", None)
            st.rerun()
    else:
        for item in items:
            with st.expander(f"{item['product_name']} - ${item['price']}", expanded=False):
                st.text("Product Name: " + item['product_name'])
                st.text("Price: $" + str(item['price']))
                st.image(f"./saved_images/{item['image_filename']}", caption=item['image_filename'], use_column_width=True)
                st.subheader("Extracted Text")
                st.text_area("", value=item['extracted_text'], height=100)
                st.subheader("Translations")
                for lang, translation in item['translations'].items():
                    st.text_area(f"{lang} Translation", value=translation, height=100)
                    # add text to speech
                    if st.button(f"Listen to {lang} Translation"):
                        text_to_speech(translation)
                        
                # select language
                languages = [
                    "English", "Chinese", "Japanese", "Spanish", "French", "German", 
                    "Italian", "Portuguese", "Russian", "Korean", "Arabic", "Hindi", 
                    "Dutch", "Swedish", "Danish", "Finnish", "Turkish", "Greek", "Polish", "Thai"
                ]
                selected_language = st.selectbox("Select chatbot language", languages, key=item['image_filename']+'chatbot')
                
                # call chatbot_ui
                if selected_language:
                    if st.button("Go to Chatbot", key=item['image_filename']) and selected_language:
                        st.session_state.page = "chatbot"
                        st.session_state.productName = item['product_name']
                        st.session_state.productPrice = item['price']
                        st.session_state.productInformation = item['extracted_text']
                        st.session_state.Language = selected_language
                        st.session_state.new_chat = True
                        st.rerun()
                    else:
                        st.write("Please select chatbot language to start chatting")
                else:
                    st.write("Please select chatbot language to start chatting")
    