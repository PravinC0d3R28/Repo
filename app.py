#not gooD try again 
#lol nice try boZo
#L
#a BIG l
import streamlit as st
from streamlit_chat import message
from utils import *
import os
from audio_recorder_streamlit import audio_recorder
from streamlit_float import float_init

# Float feature initialization
float_init()

st.subheader("ONDC Chatbot🤖")

if 'responses' not in st.session_state:
    st.session_state['responses'] = ["Welcome to ONDC! How can I assist you?"]

if 'requests' not in st.session_state:
    st.session_state['requests'] = []

# container for chat history
response_container = st.container()
# container for text box
textcontainer = st.container()

footer_container = st.container()
with footer_container:
    audio_bytes = audio_recorder()


with textcontainer:
    query = st.text_input("Query: ", key="input")
    if query:
        with st.spinner("Thinking🤔..."):
            conversation_string = get_conversation_string()
            final_message = query_response(conversation_string,query)
            st.code(conversation_string)
        st.session_state.requests.append(query)
        st.session_state.responses.append(final_message) 
    if audio_bytes:
    # Write the audio bytes to a file
        with st.spinner("Transcribing..."):
            webm_file_path = "temp_audio.mp3"
            with open(webm_file_path, "wb") as f:
                f.write(audio_bytes)

            transcript = speech_to_text(webm_file_path)
            if transcript:
                os.remove(webm_file_path)
        st.session_state.requests.append(transcript)
        with st.spinner("Thinking🤔..."):
            conversation_string = get_conversation_string()
            final_response = query_response(conversation_string,transcript)
        with st.spinner("Generating audio response..."):    
            audio_file = text_to_speech(final_response)
            autoplay_audio(audio_file)
        st.session_state.responses.append(final_response) 
        os.remove(audio_file)        

with response_container:
    if st.session_state['responses']:

        for i in range(len(st.session_state['responses'])):
            message(st.session_state['responses'][i],key=str(i))
            if i < len(st.session_state['requests']):
                message(st.session_state["requests"][i], is_user=True,key=str(i)+ '_user')

          
