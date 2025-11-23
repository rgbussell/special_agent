import chainlit as cl
from crewai import Task, Crew
from agents.planner import planner
from agents.tutor import create_tutor
from agents.knowledge import get_knowledge_base, add_documents
from ingest.email_checker import check_emails
from ingest.file_watcher import HomeworkHandler, Observer
import asyncio

observer = None

@cl.on_chat_start
async def start():
    global observer
    # Start file watcher
    observer = Observer()
    observer.schedule(HomeworkHandler(), path="./data/inbox", recursive=False)
    observer.start()
    
    # Load knowledge
    await cl.Message(content="Homework Agent ready! Drop files in `data/inbox` or send emails.").send()
    
    # Check emails
    emails = check_emails()
    if emails:
        add_documents(emails, [{"source": "email", "type": "assignment"}])
        await cl.Message(content=f"Found {len(emails)} new homework emails!").send()

@cl.on_message
async def main(message: cl.Message):
    user_input = message.content.lower()
    
    if "plan" in user_input or "schedule" in user_input:
        task = Task(
            description="Create a detailed daily study plan based on all recent homework from files and emails.",
            agent=planner,
            expected_output="A markdown study schedule with daily tasks and deadlines."
        )
        crew = Crew(agents=[planner], tasks=[task], verbose=2)
        result = crew.kickoff()
        await cl.Message(content=result).send()
        
    elif any(subject in user_input for subject in ["math", "physics", "history", "chemistry", "english"]):
        subject = next(s for s in ["math", "physics", "history", "chemistry", "english"] if s in user_input)
        tutor = create_tutor(subject)
        task = Task(
            description=f"You are now tutoring me in {subject}. Ask me what I need help with.",
            agent=tutor,
            expected_output="Engaging tutoring session"
        )
        crew = Crew(agents=[tutor], tasks=[task])
        result = crew.kickoff()
        await cl.Message(content=f"**{subject.capitalize()} Tutor is here!**\n{result}").send()
        
    else:
        await cl.Message(content="Say 'make a plan' or 'math tutor' to begin!").send()

@cl.on_stop
def stop():
    if observer:
        observer.stop()
        observer.join()