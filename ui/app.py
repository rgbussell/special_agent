import chainlit as cl
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from ingest.email_checker import check_emails
from ingest.file_watcher import HomeworkHandler, Observer
from agents.dep_knowledge import add_documents, retrieve_relevant_docs
import os
import logging

# Pure Ollama LLM — no OpenAI anywhere
llm = ChatOllama(
    model="qwen2.5:14b-instruct-q6_K", 
    base_url="http://localhost:11434", 
    temperature=0.3)

# Planning chain
planner_prompt = ChatPromptTemplate.from_template("""
    You are an expert study planner. Your #1 priority is to base EVERY recommendation on the actual homework assignments below.

    HOMEWORK ASSIGNMENTS (YOU MUST USE THESE):
    {context}

    USER REQUEST: {input}

    Rules:
    1. Quote specific problems, topics, or deadlines from the homework above.
    2. Never invent assignments — only use what is explicitly written.
    3. Break down every single task mentioned.
    4. Create a realistic daily schedule that completes everything on time.
    5. If no homework is found, say "No assignments detected in inbox/emails" and ask the user to drop files.

    Respond in clean markdown with dates and bullet points.
""")

planning_chain = (
    {"context": retrieve_relevant_docs | RunnableLambda(lambda docs: "\n".join([d.page_content for d in docs])), "input": RunnablePassthrough()}
    | planner_prompt
    | llm
)

# Tutoring chains (per subject)
tutor_prompts = {
    "math": "You are a patient math tutor. Explain concepts step-by-step with examples. User: {input}\nContext: {context}",
    "physics": "You are a physics tutor. Use clear reasoning and diagrams if needed. User: {input}\nContext: {context}",
    # Add more subjects as needed
}
tutor_chains = {}
for subject, prompt in tutor_prompts.items():
    tutor_prompt = ChatPromptTemplate.from_template(prompt)
    tutor_chains[subject] = (
        {"context": retrieve_relevant_docs | RunnableLambda(lambda docs: "\n".join([d.page_content for d in docs])), "input": RunnablePassthrough()}
        | tutor_prompt
        | llm
    )

observer = None

@cl.on_chat_start
async def start():
    global observer
    observer = Observer()
    observer.schedule(HomeworkHandler(), path="./data/inbox", recursive=False)
    observer.start()
    
    emails = check_emails()
    if emails:
        add_documents(emails, [{"source": "email", "type": "assignment"}])
        await cl.Message(content=f"Found {len(emails)} new homework emails!").send()
    
    await cl.Message(content="Homework Agent ready! Drop files in `data/inbox` or say 'make a plan' or 'math tutor'.").send()

@cl.on_message
async def main(message: cl.Message):
    user_input = message.content.lower()
    
    if "plan" in user_input or "schedule" in user_input:
        logging.info(f"\n=== PLANNING DEBUG START ===")
        logging.info(f"Raw user input: {message.content}")
        
        # Step 1: Call retrieval directly (bypass chain for now)
        raw_query = message.content  # This is what's passed to retrieve_relevant_docs
        logging.info(f"Query sent to retrieval: '{raw_query}'")
        
        docs = retrieve_relevant_docs(raw_query, k=30)  # Increase k for more chances
        logging.info(f"Retrieved {len(docs)} docs from DB (total DB count should be >0)")
        
        if docs:
            for i, doc in enumerate(docs[:3]):  # Preview first 3
                logging.info(f"  Doc {i+1}: source={doc.metadata.get('source', 'unknown')}, len={len(doc.page_content)}, preview='{doc.page_content[:200]}'")
        else:
            logging.info("  ZERO DOCS — check if DB is populated (file watcher/email ran?)")
        
        # Step 2: Test the lambda conversion
        if docs:
            context_str = "\n\n---\n\n".join([f"DOCUMENT {i+1} (source: {d.metadata.get('source','?')}):\n{d.page_content}" 
                                            for i, d in enumerate(docs)])
            logging.info(f"Lambda output (context_str) length: {len(context_str)}")
            logging.info(f"Lambda preview: {context_str[:500]!r}")
        else:
            context_str = "No homework found — check data/inbox."
            logging.info(f"Lambda fallback: {context_str}")
        
        # Step 3: Test full chain invoke
        try:
            result = await planning_chain.ainvoke(message.content)
            logging.info(f"Chain result type: {type(result)}")
            if hasattr(result, 'content'):
                logging.info(f"LLM output preview: {result.content[:500]}")
                logging.info(f"Does output mention 'Book Thief'? {'Book Thief' in result.content}")
            else:
                logging.info(f"Raw result preview: {str(result)[:500]}")
        except Exception as e:
            logging.info(f"Chain error: {e}")

        logging.info("=== PLANNING DEBUG END ===\n")

        await cl.Message(content=result.content if hasattr(result, 'content') else str(result)).send()

    elif any(subject in user_input for subject in tutor_chains):
        subject = next(s for s in tutor_chains if s in user_input)
        cl.user_session.set("tutor_subject", subject)
        result = await tutor_chains[subject].ainvoke(message.content)
        await cl.Message(content=f"**{subject.capitalize()} Tutor:**\n{result.content}").send()
    
    elif cl.user_session.get("tutor_subject"):
        subject = cl.user_session.get("tutor_subject")
        result = await tutor_chains[subject].ainvoke(message.content)
        await cl.Message(content=f"**{subject.capitalize()} Tutor:**\n{result.content}").send()
    
    else:
        await cl.Message(content="Say 'make a plan' or 'math tutor' to begin!").send()

@cl.on_stop
def stop():
    global observer
    if observer:
        observer.stop()
        observer.join()