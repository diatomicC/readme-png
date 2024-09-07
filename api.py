import time
from openai import OpenAI
import streamlit as st

# Initialize OpenAI client
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def run_llm_api_test():
    # Simulate a 2-second delay
    time.sleep(2)
    return "LLM API test completed successfully!"

def get_openai_stream(messages, model):
    stream = client.chat.completions.create(
        model=model,
        messages=[
            {"role": m["role"], "content": m["content"]}
            for m in messages
        ],
        stream=True,
        temperature=1,
        max_tokens=1024,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        response_format={
            "type": "json_object"
        }
    )
    for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            yield chunk.choices[0].delta.content