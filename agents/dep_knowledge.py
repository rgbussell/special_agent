from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings
import logging


embeddings = OllamaEmbeddings(model="qwen2.5:32b-instruct-q4_K_M", base_url="http://localhost:11434")
DB_PATH = "./data/vector_db"

def get_knowledge_base():
    return Chroma(persist_directory=DB_PATH, embedding_function=embeddings)

def add_documents(texts, metadatas=None):
    db = get_knowledge_base()
    logging.info(f"Adding {len(texts)} document(s) to db")
    for i, text in enumerate(texts):
        logging.info(f"Document {i+1} length: {len(text)} chars | source: {metadatas[i] if metadatas else 'unknown'}")
    db.add_texts(texts, metadatas)
    db.persist()
    logging.info(f"ChromaDB now has {db._collection.count()} documents total")

def retrieve_relevant_docs(query, k=30):
    db = get_knowledge_base()
    logging.info(f"\nQUERY: {query!r}")
    logging.info(f"Total docs in DB: {db._collection.count()}")
    
    if db._collection.count() == 0:
        logging.info("Vector DB is empty — no documents to search!")
        return []
    
    docs_and_scores = db.similarity_search_with_score(query, k=k)
    logging.info(f"Raw retrieval returned {len(docs_and_scores)} results")

    # start with highest relevance documents and reduce relevance if we cannot
    # find at least one document
    score_thr_list = [0.85, 0.7, 0.6, 0.3]
    relevant = [doc for doc, score in docs_and_scores if score < score_thr_list[0]]
    for score_thr in score_thr_list:
        if not relevant:
            relevant = [doc for doc, score in docs_and_scores if score >= score_thr]
        else:
            break
    logging.info(f"After filtering (score < 0.9): {len(relevant)} documents")
    
    for i, (doc, score) in enumerate(docs_and_scores[:10]):
        preview = doc.page_content[:200].replace("\n", " ")
        logging.info(f"  {i+1}. score={score:.4f} | source={doc.metadata.get('source','?')} | preview: {preview}...")
    
    return relevant[:20]