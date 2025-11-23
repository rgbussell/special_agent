# agents/knowledge.py
from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings
import os

os.environ.pop("OPENAI_API_KEY", None)

embeddings = OllamaEmbeddings(
    model="llama3.2:3b-instruct",
    base_url="http://localhost:11434"
)

DB_PATH = "./data/vector_db"

def get_knowledge_base():
    return Chroma(persist_directory=DB_PATH, embedding_function=embeddings)

def add_documents(texts, metadatas=None):
    db = get_knowledge_base()
    db.add_texts(texts, metadatas)
    db.persist()