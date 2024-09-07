import streamlit as st
from api import get_openai_stream

def chatbot_ui():

    # Custom CSS to fix the input box at the bottom
    st.markdown("""
        <style>
        .stApp {
            display: flex;
            flex-direction: column;
            height: 100vh;
        }
        .main {
            flex: 1;
            overflow: auto;
            padding-bottom: 80px;  /* Adjust this value based on your input box height */
        }
        .fixed-input {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background-color: white;
            padding: 20px;
            z-index: 1000;
            border-top: 1px solid #ddd;
        }
        </style>
    """, unsafe_allow_html=True)

    st.title("Chat with Rhythmee")

    if "openai_model" not in st.session_state:
        st.session_state["openai_model"] = "gpt-4o"

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Chat history container
    chat_container = st.container()

    # Fixed input container
    input_container = st.container()

    # Display chat history
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # Fixed input at the bottom
    with input_container:
        st.markdown('<div class="fixed-input">', unsafe_allow_html=True)
        prompt = st.chat_input("What is up?")
        st.markdown('</div>', unsafe_allow_html=True)

    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with chat_container:
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                full_response = ""
                for response in get_openai_stream(st.session_state.messages, st.session_state["openai_model"]):
                    full_response += response
                    message_placeholder.markdown(full_response + "▌")
                message_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})

        # Scroll to the bottom after new message
        st.rerun()

if __name__ == "__main__":
    chatbot_ui()