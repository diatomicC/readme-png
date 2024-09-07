import streamlit as st
from api import run_llm_api_test
from chatbot_ui import chatbot_ui

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