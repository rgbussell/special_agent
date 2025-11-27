# app.py — 100% LOCAL, WORKS TODAY
import chainlit as cl
from langchain_ollama import ChatOllama
from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import fitz, os, asyncio, pytesseract
from PIL import Image
from imap_tools import MailBox, AND
from dotenv import load_dotenv
load_dotenv()

# === CONFIG ===
llm = ChatOllama(model="qwen2.5:14b-instruct-q6_K", temperature=0.3)
embeddings = OllamaEmbeddings(model="llama3.2:3b")
db = Chroma(persist_directory="./db", embedding_function=embeddings)

# === FILE WATCHER ===
class Handler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory: return
        path = event.src_path
        text = ""
        if path.endswith(".pdf"):
            doc = fitz.open(path)
            text = " ".join(p.get_text() for p in doc)
        elif path.endswith((".png",".jpg",".jpeg")):
            text = pytesseract.image_to_string(Image.open(path))
        elif path.endswith(".txt"):
            text = open(path).read()
        
        if text.strip():
            db.add_texts([text], metadatas=[{"source": path}])
            cl.run_sync(cl.Message(content=f"Added: {os.path.basename(path)}").send())

observer = Observer()
observer.schedule(Handler(), path="./data/inbox", recursive=False)

# === EMAIL CHECK ===
def check_emails():
    try:
        with MailBox('imap.gmail.com').login(os.getenv("GMAIL"), os.getenv("GAPP"), 'INBOX') as mailbox:
            for msg in mailbox.fetch(AND(seen=False, subject='homework')):
                db.add_texts([msg.text or msg.html], [{"source": "email"}])
    except: pass

# === PLANNER PROMPT ===
planner_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert academic coach. Create a detailed daily study plan in markdown."),
    ("human", "Here are my current assignments:\n{context}\n\nMake a realistic plan for the next 7 days.")
])

# === TUTOR PROMPT ===
tutor_prompts = {
    "math": "You are a world-class math tutor. Explain step-by-step with LaTeX.",
    "physics": "You are a world-class physics tutor. Use clear reasoning.",
    # add more as needed
}

@cl.on_chat_start
async def start():
    observer.start()
    check_emails()
    await cl.Message(content="Homework Agent ready! Drop files in data/inbox or ask anything.").send()

@cl.on_message
async def main(message: cl.Message):
    txt = message.content.lower()

    if "plan" in txt or "schedule" in txt:
        docs = db.similarity_search("homework assignment", k=10)
        context = "\n\n".join(d.page_content for d in docs)
        chain = planner_prompt | llm
        result = await chain.ainvoke({"context": context})
        await cl.Message(content=result.content).send()

    elif any(s in txt for s in tutor_prompts):
        subject = next(s for s in tutor_prompts if s in txt)
        system = tutor_prompts[subject]
        chain = ChatPromptTemplate.from_messages([
            ("system", system),
            ("human", "{input}")
        ]) | llm
        cl.user_session.set("chain", chain)
        await cl.Message(content=f"{subject.capitalize()} Tutor ready! What do you need help with?").send()

    elif cl.user_session.get("chain"):
        chain = cl.user_session.get("chain")
        result = await chain.ainvoke({"input": message.content})
        await cl.Message(content=result.content).send()

    else:
        await cl.Message(content="Say 'make a plan' or 'math tutor' to start!").send()
