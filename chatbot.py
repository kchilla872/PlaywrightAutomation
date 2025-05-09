import os

# Environment fixes for compatibility
from langchain.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain.embeddings import HuggingFaceEmbeddings


os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE" # avoids a common PyTorch issue
os.environ["STREAMLIT_WATCHER_TYPE"] = "none" # disables the problematic module watcher
os.environ["PYTORCH_JIT"] = "0"

import streamlit as st
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from transformers import pipeline
from sentence_transformers import SentenceTransformer
import faiss
import torch

# Device setup
device = "cuda" if torch.cuda.is_available() else "cpu"

# Load QA pipeline
@st.cache_resource
def load_qa_model():
    return pipeline("question-answering", model="distilbert-base-uncased-distilled-squad",
                    device=0 if device == "cuda" else -1)

# Load embedding model
@st.cache_resource
def load_embedder():
    return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")




qa_pipeline = load_qa_model()
embedder = load_embedder()

st.header("PDF Question-Answer Chatbot")

# Sidebar for file upload
with st.sidebar:
    st.title("Upload PDF")
    uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")

# Initialize FAISS and variables
index = None
chunk_map = {}

# Process uploaded PDF
if uploaded_file:
    pdf_reader = PdfReader(uploaded_file)
    text = ""
    for page in pdf_reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text

    if text.strip():
        st.subheader("Extracted Text (preview):")
        st.write(text[:3000])  # preview only

        # Split into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            separators=["\n"],
            chunk_size=1000,
            chunk_overlap=150,
            length_function=len
        )
        chunks = text_splitter.split_text(text)

        vector_store = FAISS.from_texts(chunks,embedder)

        user_question = st.text_input("Type your question")

        if user_question:
            match = vector_store.similarity_search(user_question)
            st.write(match)

