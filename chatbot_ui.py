import streamlit as st
import json
from api import get_openai_stream

def chatbot_ui(productName, productPrice, productInformation, Language, new_chat=False):
    # Custom CSS (unchanged)
    st.markdown("""
        <style>
        /* ... (unchanged CSS) ... */
        </style>
        <script>
        /* ... (unchanged script) ... */
        </script>
    """, unsafe_allow_html=True)

    st.title("[Chat with Rhythmee]")
    
    st.markdown(f"**Product Name:** {productName}")
    st.markdown(f"**Product Price:** {productPrice}")

    if "openai_model" not in st.session_state:
        st.session_state["openai_model"] = "gpt-4o"

    # Initialize or clear chat history only if it's a new chat
    if new_chat or "messages" not in st.session_state:
        initial_prompt = f"""
You, 'Rhythmee', are a shopping mall customer service chatbot with decades of experience. You will now receive various questions from customers regarding the product provided below. Please offer helpful and friendly information to customers. If there is something you do not know, be sure to state that clearly. Answer the questions in a concise and easy-to-understand manner.

The customer speaks the language: {Language}

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
        st.session_state.suggested_question = None

    # Rest of the function remains largely unchanged
    chat_container = st.container()
    input_container = st.container()

    with chat_container:
        for i, message in enumerate(st.session_state.messages[1:], start=1):
            with st.chat_message(message["role"]):
                if message["role"] == "assistant":
                    response_data = json.loads(message["content"])
                    st.markdown(response_data["response"])
                    if i == len(st.session_state.messages) - 1:
                        if response_data["suggested_questions"]:
                            st.markdown("**Suggested questions:**")
                            unique_questions = list(set(response_data["suggested_questions"]))
                            for j, question in enumerate(unique_questions):
                                if st.button(question, key=f"{i}_{j}_{question}"):
                                    st.session_state.suggested_question = question
                                    st.rerun()
                else:
                    st.markdown(message["content"])

    with input_container:
        st.markdown('<div class="fixed-input">', unsafe_allow_html=True)
        prompt = st.chat_input("Ask Rhythmee anything about the product...", key="chat_input")
        st.markdown('</div>', unsafe_allow_html=True)

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
                        response_data = json.loads(full_response)
                        message_placeholder.markdown(response_data["response"] + "▌")
                    except json.JSONDecodeError:
                        message_placeholder.markdown(full_response + "▌")
                
                response_data = json.loads(full_response)
                message_placeholder.markdown(response_data["response"])
                if response_data["suggested_questions"]:
                    message_placeholder.markdown("**Suggested questions:**")
                    unique_questions = list(set(response_data["suggested_questions"]))
                    for question in unique_questions:
                        message_placeholder.markdown(f"- {question}")

            st.session_state.messages.append({"role": "assistant", "content": full_response})

        st.rerun()