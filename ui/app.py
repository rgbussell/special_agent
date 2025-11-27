import chainlit as cl
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from ingest.email_checker import check_emails
from ingest.file_watcher import HomeworkHandler, Observer
from agents.knowledge import add_documents, retrieve_relevant_docs
import os

# Pure Ollama LLM — no OpenAI anywhere
llm = ChatOllama(model="qwen2.5:14b-instruct-q6_K", base_url="http://localhost:11434", temperature=0.3)

# Planning chain
planner_prompt = ChatPromptTemplate.from_template(
    "You are an expert study planner. Based on this homework context: {context}\nUser request: {input}\nCreate a detailed daily study plan in markdown."
)
planning_chain = (
    {"context": retrieve_relevant_docs | (lambda docs: "\n".join([d.page_content for d in docs])), "input": RunnablePassthrough()}
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
        {"context": retrieve_relevant_docs | (lambda docs: "\n".join([d.page_content for d in docs])), "input": RunnablePassthrough()}
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
        result = await planning_chain.ainvoke(message.content)
        await cl.Message(content=result.content).send()
    
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