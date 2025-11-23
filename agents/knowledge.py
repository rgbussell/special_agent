from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings
from pathlib import Path

embeddings = OllamaEmbeddings(model="llama3.2:3b-instruct")
DB_PATH = "./data/vector_db"

def get_knowledge_base():
    return Chroma(persist_directory=DB_PATH, embedding_function=embeddings)

def add_documents(texts, metadatas=None):
    db = get_knowledge_base()
    db.add_texts(texts, metadatas)
    db.persist()