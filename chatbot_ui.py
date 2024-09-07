import streamlit as st
import json
from api import get_openai_stream

def chatbot_ui(productName, productPrice, productInformation, Language):
    # Custom CSS (updated to include scroll management)
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
            padding-bottom: 80px;
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
        <script>
        const doc = window.parent.document;
        const main = doc.querySelector('.main');
        const targetNode = doc.querySelector('section[data-testid="stSidebar"]');
        const config = { attributes: true, childList: true, subtree: true };
        const callback = function(mutationsList, observer) {
            // wait for 0.1s to ensure the sidebar is fully loaded
            setTimeout(() => {
                // scroll to the bottom
                main.scrollTop = main.scrollHeight;
            }, 100);
        };
        const observer = new MutationObserver(callback);
        observer.observe(targetNode, config);
        
        
        </script>
    """, unsafe_allow_html=True)

    st.title("Chat with Rhythmee")

    if "openai_model" not in st.session_state:
        st.session_state["openai_model"] = "gpt-4o"

    if "messages" not in st.session_state:
        # Initialize with the system message (unchanged)
        initial_prompt = f"""
You, 'Rhythmee', are a shopping mall customer service chatbot with decades of experience. You will now receive various questions from customers regarding the product provided below. Please offer helpful and friendly information to customers. If there is something you do not know, be sure to state that clearly.

Guidelines:
1. Your response should be concise and easy to understand, no more than 3-4 sentences. If the customer asks for more details, you can provide a longer answer.
2. If you are unsure or the information is not reliable, honestly say you do not know.
3. After your response, you may generate up to three possible follow-up questions the customer might ask.
4. Only suggest follow-up questions with information strictly available from the given product information.

Product Name: {productName}

Product Price: {productPrice}

Product Information:
```json
{productInformation}
```

Response Format:
```json
{{
    "response": "",
    "suggested_questions": [
        "",
        "",
        ""
    ]
}}
```
"""
        st.session_state.messages = [{"role": "system", "content": initial_prompt}]

    if "suggested_question" not in st.session_state:
        st.session_state.suggested_question = None

    # Chat history container
    chat_container = st.container()

    # Fixed input container
    input_container = st.container()

    # Display chat history (excluding system message)
    with chat_container:
        for i, message in enumerate(st.session_state.messages[1:], start=1):  # Skip the first (system) message
            with st.chat_message(message["role"]):
                if message["role"] == "assistant":
                    response_data = json.loads(message["content"])
                    st.markdown(response_data["response"])
                    if i == len(st.session_state.messages) - 1:  # Only show suggested questions for the latest message
                        if response_data["suggested_questions"]:
                            st.markdown("**Suggested questions:**")
                            # Use set to remove duplicates
                            unique_questions = list(set(response_data["suggested_questions"]))
                            for j, question in enumerate(unique_questions):
                                if st.button(question, key=f"{i}_{j}_{question}"):
                                    st.session_state.suggested_question = question
                                    st.rerun()
                else:
                    st.markdown(message["content"])

    # Fixed input at the bottom
    with input_container:
        st.markdown('<div class="fixed-input">', unsafe_allow_html=True)
        prompt = st.chat_input("Ask Rhythmee anything about the product...", key="chat_input")
        st.markdown('</div>', unsafe_allow_html=True)

    # Handle suggested question
    if st.session_state.suggested_question:
        prompt = st.session_state.suggested_question
        st.session_state.suggested_question = None

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
                    try:
                        # Attempt to parse the JSON as it's being streamed
                        response_data = json.loads(full_response)
                        message_placeholder.markdown(response_data["response"] + "▌")
                    except json.JSONDecodeError:
                        # If it's not valid JSON yet, just display as is
                        message_placeholder.markdown(full_response + "▌")
                
                # Final update with suggested questions
                response_data = json.loads(full_response)
                message_placeholder.markdown(response_data["response"])
                if response_data["suggested_questions"]:
                    message_placeholder.markdown("**Suggested questions:**")
                    unique_questions = list(set(response_data["suggested_questions"]))
                    for question in unique_questions:
                        message_placeholder.markdown(f"- {question}")

            st.session_state.messages.append({"role": "assistant", "content": full_response})

        # Scroll to the bottom after new message
        st.rerun()
        