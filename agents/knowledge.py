from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings
import os

embeddings = OllamaEmbeddings(model="qwen2.5:32b-instruct-q4_K_M", base_url="http://localhost:11434")
DB_PATH = "./data/vector_db"

def get_knowledge_base():
    return Chroma(persist_directory=DB_PATH, embedding_function=embeddings)

def add_documents(texts, metadatas=None):
    db = get_knowledge_base()
    db.add_texts(texts, metadatas)
    db.persist()

def retrieve_relevant_docs(query, k=5):
    db = get_knowledge_base()
    return db.similarity_search(query, k=k)