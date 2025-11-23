# ui/app.py
import chainlit as cl
from crewai import Task, Crew
from agents.planner import planner
from agents.tutor import create_tutor
from agents.knowledge import add_documents
from ingest.file_watcher import HomeworkHandler, Observer
from ingest.email_checker import check_emails
import os
import asyncio

os.environ.pop("OPENAI_API_KEY", None)

observer = None

@cl.on_chat_start
async def start():
    global observer
    observer = Observer()
    observer.schedule(HomeworkHandler(), path="./data/inbox", recursive=False)
    observer.start()

    try:
        emails = check_emails()
        if emails:
            add_documents(emails, [{"source": "email", "type": "assignment"}])
            await cl.Message(content=f"Found {len(emails)} new homework emails!").send()
    except Exception as e:
        print(f"Email check failed: {e}")

    await cl.Message(content="Homework Agent ready! Drop files in `data/inbox` or say 'make a plan' or 'math tutor'").send()

@cl.on_message
async def main(message: cl.Message):
    user_input = message.content.lower().strip()

    if "plan" in user_input or "schedule" in user_input:
        task = Task(
            description="Create a detailed daily study plan based on all recent homework from files and emails.",
            agent=planner,
            expected_output="A clean markdown study schedule with daily tasks and deadlines."
        )
        crew = Crew(agents=[planner], tasks=[task], verbose=True, memory=False)
        try:
            result = crew.kickoff()
            await cl.Message(content=str(result)).send()
        except Exception as e:
            await cl.Message(content=f"Error: {str(e)}").send()

    elif any(s in user_input for s in ["math", "physics", "chemistry", "history", "english", "biology"]):
        subject = next(s for s in ["math", "physics", "chemistry", "history", "english", "biology"] if s in user_input)
        tutor = create_tutor(subject)
        task = Task(
            description=f"You are tutoring me in {subject}. Ask what I need help with.",
            agent=tutor,
            expected_output="Engaging tutoring session"
        )
        crew = Crew(agents=[tutor], tasks=[task], verbose=True, memory=False)
        try:
            result = crew.kickoff()
            await cl.Message(content=f"**{subject.capitalize()} Tutor is here!**\n\n{result}").send()
        except Exception as e:
            await cl.Message(content=f"Tutor error: {e}").send()

    else:
        await cl.Message(content="Say **make a plan** or **math tutor** to start!").send()

@cl.on_stop
def stop():
    if observer:
        observer.stop()
        observer.join()