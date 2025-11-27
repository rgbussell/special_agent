# agents/tutor.py
import os
from langchain_ollama import ChatOllama
from crewai import Agent

os.environ.pop("OPENAI_API_KEY", None)

raise NotImplementedError("This module is deprecated. Use dep_tutor.py instead.")

class LocalLLM:
    def __init__(self, llm):
        self.llm = llm
    def __call__(self, messages, **kwargs):
        return self.llm.invoke(messages)
    def bind(self, **kwargs):
        return self

def create_tutor(subject: str):
    llm = ChatOllama(
        model="qwen2.5:14b-instruct-q4_K_M",
        base_url="http://localhost:11434",
        temperature=0.7
    )
    safe_llm = LocalLLM(llm)
    return Agent(
        role=f"{subject.capitalize()} Tutor",
        goal=f"Help the student master {subject} concepts with clear, step-by-step explanations",
        backstory=f"You are a world-class, patient {subject} teacher.",
        llm=safe_llm,
        verbose=True,
        memory=False
    )