import pinecone
from langchain_community.vectorstores import Pinecone
from langchain_openai import OpenAIEmbeddings
import os
import openai
import streamlit as st
from langchain.chains.question_answering import load_qa_chain
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import base64
load_dotenv()

openai.api_key=os.environ["OPENAI_API_KEY"]
embeddings = OpenAIEmbeddings()
pinecone.init(api_key=os.environ["PINECONE_API_KEY"], environment=os.environ["ENVIRONMENT"])
index = Pinecone.from_existing_index(os.environ["INDEX_NAME"], embeddings)

model_name = "gpt-3.5-turbo"
llm = ChatOpenAI(model_name=model_name)
chain = load_qa_chain(llm, chain_type="stuff")


def get_similiar_docs(query,k=2,score=False):
    if score:
        similar_docs = index.similarity_search_with_score(query,k=k)
    else:
        similar_docs = index.similarity_search(query,k=k)
    return similar_docs

def query_response(conversation_string,query):
    similar_docs=get_similiar_docs(query)
    prompt = f"""You are support chatbot for ONDC (Open Network for Digital Commerce) which is e-commerce webiste, your primary role is to assist users with their queries related to products, provide structured product recommendations, and address other store-related inquiries. Your responses should be truthful, non-offensive, and strictly based on the provided knowledge base.

    Instructions:
    1.Provide assistance within the scope of e-commerce and ONDC.
    2.If the query context require more information ask user but only if necessary.
    3.For product related queries show 3-5 if available products in your knowledge base with the name, price, small combined description.
    4.If you lack information on a topic, respond with "I Don't know."
    5.You must provide answer without asking much questions with minimal words in user query.
    6.For Legal compliance, policies and related queries be concis in response.
    7.Below is the user request history, if this is relevant to 
    current user query then you need to use it if necessary and refer to this while creating response.
    User request history:
    {conversation_string}
    \n
    USER QUERY:\n 
    {query}"""
    
    answer = chain.run(input_documents=similar_docs, question=prompt)
    return answer

def get_conversation_string():
    conversation_string = ""
    for i in range(len(st.session_state['responses'])-1):
        conversation_string += "Human: "+st.session_state['requests'][i] + "\n"
        conversation_string += "Bot: "+ st.session_state['responses'][i+1] + "\n"
    return conversation_string

def speech_to_text(audio_data):
    with open(audio_data, "rb") as audio_file:
        transcript = openai.audio.transcriptions.create(
            model="whisper-1",
            response_format="text",
            file=audio_file
        )
    return transcript

def text_to_speech(input_text):
    response = openai.audio.speech.create(
        model="tts-1",
        voice="nova",
        input=input_text
    )
    webm_file_path = "temp_audio_play.mp3"
    with open(webm_file_path, "wb") as f:
        response.stream_to_file(webm_file_path)
    return webm_file_path

def autoplay_audio(file_path: str):
    with open(file_path, "rb") as f:
        data = f.read()
    b64 = base64.b64encode(data).decode("utf-8")
    md = f"""
    <audio autoplay>
    <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
    </audio>
    """
    st.markdown(md, unsafe_allow_html=True)
