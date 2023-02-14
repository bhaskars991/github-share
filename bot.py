import openai
import streamlit as st
from streamlit_chat import message
from langchain.llms import OpenAI
from langchain.chains.qa_with_sources import load_qa_with_sources_chain
from langchain.chains.question_answering import load_qa_chain
from langchain.docstore.document import Document
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores.faiss import FAISS
from langchain.text_splitter import CharacterTextSplitter
import requests
import sys

openai.api_key = st.secrets["api_secret"]

def getSmallChunks(source, name) :
    desc = ""
    if (name != "") :
        desc = "This is from " + name + "."
    blocks = []
    splitter = CharacterTextSplitter(separator=" ", chunk_size=512, chunk_overlap=0)
    for s in splitter.split_text(source) :
        blocks.append(Document(page_content = desc+s, metadata = {"source": "the web"})) 
    return blocks   

chunks = []

def prepareText(filename) :
    f = open(filename, mode='r', encoding='utf-8')  
    data = f.read()
    parts = getSmallChunks(data, "")
    for s in parts:
        chunks.append(s)
    docsearch = FAISS.from_documents(chunks, OpenAIEmbeddings())
    return docsearch
        
def getAnswers(qq) :
    docs = docsearch.similarity_search(qq)
    message = chain.run(input_documents=docs, question=qq)
    return message

docsearch = prepareText('test.txt')
chain = load_qa_chain(OpenAI(temperature=0), chain_type="stuff")

st.title("Health Bot")
if 'generated' not in st.session_state :
    st.session_state['generated'] = []
if 'past' not in st.session_state :
    st.session_state['past'] = []
    
question = st.text_input("you:", "what is plant based diet?", key="input")

response = getAnswers(question)
st.session_state.past.append(question)
st.session_state.generated.append(response)

if st.session_state['generated'] :
    for i in range (len(st.session_state['generated'])-1, -1, -1) :
        message(st.session_state['generated'][i], key=str(i))
        message(st.session_state['past'][i], is_user=True, key=str(i) + '_user')
      
