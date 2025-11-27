from crewai import Agent
from langchain_ollama import ChatOllama

def create_tutor(subject: str):
    llm = ChatOllama(model="llama3.2:3b", temperature=0.7)
    return Agent(
        role=f"{subject.capitalize()} Tutor",
        goal=f"Help students master {subject} concepts step-by-step",
        backstory=f"You are a patient, world-class {subject} teacher.",
        llm=llm,
        verbose=True
    )
